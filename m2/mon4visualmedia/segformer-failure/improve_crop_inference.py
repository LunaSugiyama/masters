import argparse
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation


def choose_device(device_arg):
    if device_arg != "auto":
        return torch.device(device_arg)
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def run_segmentation(image, processor, model, device):
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        h, w = image.height, image.width
        logits = F.interpolate(logits, size=(h, w), mode="bilinear", align_corners=False)
        probs = torch.softmax(logits, dim=1)
        confidence, pred = probs.max(dim=1)

    return pred[0].cpu().numpy(), confidence[0].cpu().numpy()


def analyze(pred, conf, id2label):
    unique, counts = np.unique(pred, return_counts=True)
    total = pred.size
    rows = []

    for cid, count in zip(unique, counts):
        mask = pred == cid
        rows.append({
            "class_id": int(cid),
            "class_name": id2label[int(cid)],
            "ratio": float(count / total),
            "mean_confidence": float(conf[mask].mean()),
            "pixels": int(count),
        })

    return sorted(rows, key=lambda r: r["ratio"], reverse=True), float(conf.mean())


def save_csv(rows, mean_conf, out_path):
    lines = ["class_id,class_name,ratio,mean_confidence,pixels"]
    for r in rows:
        lines.append(
            f"{r['class_id']},{r['class_name']},{r['ratio']:.6f},"
            f"{r['mean_confidence']:.6f},{r['pixels']}"
        )
    lines.append("")
    lines.append(f"mean_confidence,{mean_conf:.6f}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def draw_bbox(image, bbox, out_path):
    img = image.copy()
    draw = ImageDraw.Draw(img)
    draw.rectangle(bbox, outline="red", width=6)
    img.save(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--bbox", type=int, nargs=4, required=True)
    parser.add_argument("--output", default="crop_improvement_result")
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--model", default="nvidia/segformer-b0-finetuned-ade-512-512")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    device = choose_device(args.device)
    print(f"Using device: {device}")

    image = Image.open(args.image).convert("RGB")
    x1, y1, x2, y2 = args.bbox
    bbox = (x1, y1, x2, y2)

    processor = AutoImageProcessor.from_pretrained(args.model)
    model = AutoModelForSemanticSegmentation.from_pretrained(args.model)
    model.to(device)
    model.eval()
    id2label = {int(k): v for k, v in model.config.id2label.items()}

    # Baseline: full image inference, then analyze only ROI
    pred_full, conf_full = run_segmentation(image, processor, model, device)
    pred_roi = pred_full[y1:y2, x1:x2]
    conf_roi = conf_full[y1:y2, x1:x2]
    baseline_rows, baseline_mean = analyze(pred_roi, conf_roi, id2label)

    # Improved: crop ROI, enlarge, then rerun inference
    crop = image.crop(bbox)
    crop_big = crop.resize(
        (crop.width * args.scale, crop.height * args.scale),
        Image.Resampling.BICUBIC,
    )
    pred_crop, conf_crop = run_segmentation(crop_big, processor, model, device)
    improved_rows, improved_mean = analyze(pred_crop, conf_crop, id2label)

    draw_bbox(image, bbox, out_dir / "baseline_roi_bbox.png")
    crop.save(out_dir / "crop_original_size.png")
    crop_big.save(out_dir / "crop_enlarged.png")

    save_csv(baseline_rows, baseline_mean, out_dir / "baseline_full_image_roi.csv")
    save_csv(improved_rows, improved_mean, out_dir / "improved_crop_inference.csv")

    print("\n=== Baseline: full image ROI ===")
    print(f"Target: {args.target}")
    print(f"Mean confidence: {baseline_mean:.4f}")
    for r in baseline_rows[:10]:
        print(f"{r['class_name']:20s} ratio={r['ratio']:.4f} conf={r['mean_confidence']:.4f}")

    print("\n=== Improved: enlarged crop inference ===")
    print(f"Target: {args.target}")
    print(f"Mean confidence: {improved_mean:.4f}")
    for r in improved_rows[:10]:
        print(f"{r['class_name']:20s} ratio={r['ratio']:.4f} conf={r['mean_confidence']:.4f}")

    print(f"\nSaved results to {out_dir}")


if __name__ == "__main__":
    main()
