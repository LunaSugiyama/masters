import argparse
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation


def choose_device(device_arg: str) -> torch.device:
    if device_arg != "auto":
        return torch.device(device_arg)

    if torch.cuda.is_available():
        return torch.device("cuda")

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def run_segmentation(image, processor, model, device):
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

        h, w = image.height, image.width
        logits = F.interpolate(
            logits,
            size=(h, w),
            mode="bilinear",
            align_corners=False,
        )

        probs = torch.softmax(logits, dim=1)
        confidence, pred = probs.max(dim=1)

    pred = pred[0].detach().cpu().numpy().astype(np.int32)
    confidence = confidence[0].detach().cpu().numpy().astype(np.float32)

    return pred, confidence


def normalize_label(s):
    return s.lower().replace("_", " ").replace("-", " ").strip()


def check_target_in_labels(target, id2label):
    target_norm = normalize_label(target)
    labels_norm = [normalize_label(v) for v in id2label.values()]

    exact = target_norm in labels_norm
    partial = [label for label in labels_norm if target_norm in label or label in target_norm]

    return exact, partial


def save_roi_visualization(image, bbox, target, top_info, out_path):
    img = image.copy()
    draw = ImageDraw.Draw(img)

    x1, y1, x2, y2 = bbox
    draw.rectangle((x1, y1, x2, y2), outline="red", width=6)

    text_lines = [f"Target: {target}", "SegFormer predicts:"]
    for name, ratio, conf in top_info[:3]:
        text_lines.append(f"{name}: {ratio:.1%}, conf {conf:.2f}")

    text = "\n".join(text_lines)

    text_x = x1
    text_y = max(0, y1 - 90)

    draw.rectangle(
        (text_x, text_y, text_x + 520, text_y + 85),
        fill=(255, 255, 255),
        outline="red",
    )
    draw.text((text_x + 8, text_y + 8), text, fill=(0, 0, 0))

    img.save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True)
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument(
        "--bbox",
        type=int,
        nargs=4,
        required=True,
        metavar=("X1", "Y1", "X2", "Y2"),
        help="Bounding box around the target object.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="ood_roi_result",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="nvidia/segformer-b0-finetuned-ade-512-512",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
    )
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    device = choose_device(args.device)
    print(f"Using device: {device}")

    image = Image.open(args.image).convert("RGB")
    w, h = image.size

    x1, y1, x2, y2 = args.bbox
    x1 = max(0, min(x1, w - 1))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h - 1))
    y2 = max(0, min(y2, h))

    if x2 <= x1 or y2 <= y1:
        raise ValueError("Invalid bbox.")

    processor = AutoImageProcessor.from_pretrained(args.model)
    model = AutoModelForSemanticSegmentation.from_pretrained(args.model)
    model.to(device)
    model.eval()

    id2label = {int(k): v for k, v in model.config.id2label.items()}

    exact, partial = check_target_in_labels(args.target, id2label)

    print("")
    print("=== Label-set check ===")
    print(f"Target object: {args.target}")
    print(f"Exact label exists in ADE20K label set: {exact}")

    if partial:
        print("Possible related ADE20K labels:")
        for p in partial:
            print(f"  - {p}")
    else:
        print("No obvious related label found.")

    pred, confidence = run_segmentation(image, processor, model, device)

    pred_roi = pred[y1:y2, x1:x2]
    conf_roi = confidence[y1:y2, x1:x2]

    unique, counts = np.unique(pred_roi, return_counts=True)
    total = pred_roi.size

    rows = []
    for class_id, count in zip(unique, counts):
        class_mask = pred_roi == class_id
        ratio = count / total
        mean_conf = float(conf_roi[class_mask].mean())
        class_name = id2label[int(class_id)]
        rows.append((class_name, ratio, mean_conf, int(count), int(class_id)))

    rows = sorted(rows, key=lambda x: x[1], reverse=True)

    print("")
    print("=== Predictions inside ROI ===")
    print(f"ROI bbox: {(x1, y1, x2, y2)}")
    print(f"ROI mean confidence: {float(conf_roi.mean()):.4f}")
    print("")
    print("Top predicted classes in ROI:")
    for class_name, ratio, mean_conf, count, class_id in rows[:10]:
        print(
            f"{class_id:3d} | {class_name:20s} | "
            f"ratio={ratio:.4f} | mean_conf={mean_conf:.4f} | pixels={count}"
        )

    # Save CSV
    csv_lines = ["class_id,class_name,ratio,mean_confidence,pixels"]
    for class_name, ratio, mean_conf, count, class_id in rows:
        csv_lines.append(
            f"{class_id},{class_name},{ratio:.6f},{mean_conf:.6f},{count}"
        )

    csv_lines.append("")
    csv_lines.append(f"target,{args.target}")
    csv_lines.append(f"target_exact_label_exists,{exact}")
    csv_lines.append(f"roi_mean_confidence,{float(conf_roi.mean()):.6f}")

    (out_dir / "ood_roi_summary.csv").write_text(
        "\n".join(csv_lines),
        encoding="utf-8",
    )

    save_roi_visualization(
        image=image,
        bbox=(x1, y1, x2, y2),
        target=args.target,
        top_info=[(r[0], r[1], r[2]) for r in rows],
        out_path=out_dir / "ood_roi_visualization.png",
    )

    print("")
    print(f"Saved: {out_dir / 'ood_roi_summary.csv'}")
    print(f"Saved: {out_dir / 'ood_roi_visualization.png'}")


if __name__ == "__main__":
    main()