import argparse
from pathlib import Path
from typing import List, Tuple, Dict

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw
from tqdm import tqdm
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def choose_device(device_arg: str) -> torch.device:
    if device_arg != "auto":
        return torch.device(device_arg)

    if torch.cuda.is_available():
        return torch.device("cuda")

    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def collect_images(input_path: Path) -> List[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() not in IMAGE_EXTS:
            raise ValueError(f"Unsupported image file: {input_path}")
        return [input_path]

    if input_path.is_dir():
        images = []
        for p in sorted(input_path.rglob("*")):
            if p.suffix.lower() in IMAGE_EXTS:
                images.append(p)
        return images

    raise FileNotFoundError(f"Input path not found: {input_path}")


def load_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def gamma_correction(image: Image.Image, gamma: float = 0.65) -> Image.Image:
    """
    gamma < 1.0 brightens the image.
    Useful for low-light failure analysis.
    """
    arr = np.asarray(image).astype(np.float32) / 255.0
    corrected = np.power(arr, gamma)
    corrected = np.clip(corrected * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(corrected)


def run_segmentation(
    image: Image.Image,
    processor,
    model,
    device: torch.device,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        pred: H x W class id mask
        confidence: H x W max softmax probability
    """
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

        # Resize logits to original image size
        h, w = image.height, image.width
        logits = F.interpolate(
            logits,
            size=(h, w),
            mode="bilinear",
            align_corners=False,
        )

        probs = torch.softmax(logits, dim=1)
        confidence, pred = probs.max(dim=1)

    pred_np = pred[0].detach().cpu().numpy().astype(np.int32)
    conf_np = confidence[0].detach().cpu().numpy().astype(np.float32)

    return pred_np, conf_np


def make_palette(num_classes: int = 256) -> np.ndarray:
    """
    Deterministic color palette for class masks.
    """
    rng = np.random.default_rng(12345)
    palette = rng.integers(0, 255, size=(num_classes, 3), dtype=np.uint8)
    palette[0] = np.array([0, 0, 0], dtype=np.uint8)
    return palette


def colorize_mask(pred: np.ndarray, palette: np.ndarray) -> Image.Image:
    color = palette[pred % len(palette)]
    return Image.fromarray(color.astype(np.uint8))


def overlay_mask(
    image: Image.Image,
    pred: np.ndarray,
    palette: np.ndarray,
    alpha: float = 0.55,
) -> Image.Image:
    mask_img = colorize_mask(pred, palette).convert("RGB")
    return Image.blend(image.convert("RGB"), mask_img, alpha=alpha)


def remove_small_regions(pred: np.ndarray, min_area: int = 150) -> np.ndarray:
    """
    Simple post-processing:
    remove tiny connected components and replace them with the most common
    neighboring class.

    This is useful when SegFormer produces small noisy regions.
    """
    cleaned = pred.copy()
    classes = np.unique(pred)
    kernel = np.ones((3, 3), np.uint8)

    for class_id in classes:
        binary = (cleaned == class_id).astype(np.uint8)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        for label_id in range(1, num_labels):
            area = stats[label_id, cv2.CC_STAT_AREA]
            if area >= min_area:
                continue

            component = labels == label_id

            # Get neighboring pixels around the small region
            dilated = cv2.dilate(component.astype(np.uint8), kernel, iterations=2).astype(bool)
            border = dilated & (~component)

            neighbor_values = cleaned[border]
            neighbor_values = neighbor_values[neighbor_values != class_id]

            if len(neighbor_values) == 0:
                continue

            replacement = np.bincount(neighbor_values).argmax()
            cleaned[component] = replacement

    return cleaned


def save_confidence_map(confidence: np.ndarray, out_path: Path) -> None:
    conf_img = np.clip(confidence * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(conf_img).save(out_path)


def save_low_confidence_mask(
    confidence: np.ndarray,
    out_path: Path,
    threshold: float = 0.55,
) -> None:
    """
    White pixels indicate low-confidence regions.
    These are useful as a simple failure detector visualization.
    """
    low = (confidence < threshold).astype(np.uint8) * 255
    Image.fromarray(low).save(out_path)


def resize_for_grid(image: Image.Image, width: int = 360) -> Image.Image:
    w, h = image.size
    new_h = int(h * (width / w))
    return image.resize((width, new_h))


def make_comparison_grid(
    images_with_titles: List[Tuple[str, Image.Image]],
    out_path: Path,
    tile_width: int = 360,
) -> None:
    resized = [(title, resize_for_grid(img, tile_width)) for title, img in images_with_titles]

    title_h = 32
    gap = 8
    total_w = sum(img.width for _, img in resized) + gap * (len(resized) - 1)
    max_h = max(img.height for _, img in resized)

    canvas = Image.new("RGB", (total_w, max_h + title_h), "white")
    draw = ImageDraw.Draw(canvas)

    x = 0
    for title, img in resized:
        draw.text((x + 5, 8), title, fill=(0, 0, 0))
        canvas.paste(img.convert("RGB"), (x, title_h))
        x += img.width + gap

    canvas.save(out_path)


def save_class_summary(
    pred: np.ndarray,
    confidence: np.ndarray,
    id2label: Dict[int, str],
    out_path: Path,
) -> None:
    unique, counts = np.unique(pred, return_counts=True)
    total = pred.size

    lines = []
    lines.append("class_id,class_name,pixels,ratio")
    for class_id, count in sorted(zip(unique, counts), key=lambda x: -x[1]):
        class_name = id2label.get(int(class_id), str(class_id))
        ratio = count / total
        lines.append(f"{class_id},{class_name},{count},{ratio:.6f}")

    lines.append("")
    lines.append(f"mean_confidence,{float(confidence.mean()):.6f}")
    lines.append(f"min_confidence,{float(confidence.min()):.6f}")
    lines.append(f"max_confidence,{float(confidence.max()):.6f}")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def process_one_image(
    image_path: Path,
    out_root: Path,
    processor,
    model,
    device: torch.device,
    palette: np.ndarray,
    id2label: Dict[int, str],
    gamma: float,
    min_area: int,
    alpha: float,
    low_conf_threshold: float,
) -> None:
    image = load_rgb(image_path)
    stem = image_path.stem
    out_dir = out_root / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Baseline SegFormer
    pred_base, conf_base = run_segmentation(image, processor, model, device)
    mask_base = colorize_mask(pred_base, palette)
    overlay_base = overlay_mask(image, pred_base, palette, alpha=alpha)

    # 2. Gamma correction + SegFormer
    gamma_img = gamma_correction(image, gamma=gamma)
    pred_gamma, conf_gamma = run_segmentation(gamma_img, processor, model, device)
    mask_gamma = colorize_mask(pred_gamma, palette)
    overlay_gamma = overlay_mask(gamma_img, pred_gamma, palette, alpha=alpha)

    # 3. Gamma correction + post-processing
    pred_post = remove_small_regions(pred_gamma, min_area=min_area)
    mask_post = colorize_mask(pred_post, palette)
    overlay_post = overlay_mask(gamma_img, pred_post, palette, alpha=alpha)

    # Save individual results
    image.save(out_dir / "00_input.png")
    gamma_img.save(out_dir / "01_gamma_input.png")

    mask_base.save(out_dir / "10_baseline_mask.png")
    overlay_base.save(out_dir / "11_baseline_overlay.png")
    save_confidence_map(conf_base, out_dir / "12_baseline_confidence.png")
    save_low_confidence_mask(conf_base, out_dir / "13_baseline_low_confidence.png", threshold=low_conf_threshold)

    mask_gamma.save(out_dir / "20_gamma_mask.png")
    overlay_gamma.save(out_dir / "21_gamma_overlay.png")
    save_confidence_map(conf_gamma, out_dir / "22_gamma_confidence.png")
    save_low_confidence_mask(conf_gamma, out_dir / "23_gamma_low_confidence.png", threshold=low_conf_threshold)

    mask_post.save(out_dir / "30_gamma_postprocess_mask.png")
    overlay_post.save(out_dir / "31_gamma_postprocess_overlay.png")

    save_class_summary(
        pred_base,
        conf_base,
        id2label,
        out_dir / "baseline_class_summary.csv",
    )
    save_class_summary(
        pred_gamma,
        conf_gamma,
        id2label,
        out_dir / "gamma_class_summary.csv",
    )
    save_class_summary(
        pred_post,
        conf_gamma,
        id2label,
        out_dir / "gamma_postprocess_class_summary.csv",
    )

    # Save comparison image for report
    make_comparison_grid(
        [
            ("Input", image),
            ("Baseline", overlay_base),
            (f"Gamma {gamma}", overlay_gamma),
            (f"Gamma + postprocess", overlay_post),
        ],
        out_dir / "comparison_overlay.png",
    )

    make_comparison_grid(
        [
            ("Input", image),
            ("Baseline mask", mask_base),
            (f"Gamma mask", mask_gamma),
            ("Postprocess mask", mask_post),
        ],
        out_dir / "comparison_mask.png",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to an image file or directory containing images.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="segformer_results",
        help="Output directory.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="nvidia/segformer-b0-finetuned-ade-512-512",
        help="Hugging Face SegFormer model name.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help="auto, cpu, cuda, or mps.",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.65,
        help="Gamma value for low-light improvement. gamma < 1 brightens image.",
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=150,
        help="Minimum connected-component area for post-processing.",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.55,
        help="Overlay alpha.",
    )
    parser.add_argument(
        "--low-conf-threshold",
        type=float,
        default=0.55,
        help="Threshold for low-confidence failure detector mask.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    out_root = Path(args.output)
    out_root.mkdir(parents=True, exist_ok=True)

    device = choose_device(args.device)
    print(f"Using device: {device}")

    print(f"Loading model: {args.model}")
    processor = AutoImageProcessor.from_pretrained(args.model)
    model = AutoModelForSemanticSegmentation.from_pretrained(args.model)
    model.to(device)
    model.eval()

    id2label = {int(k): v for k, v in model.config.id2label.items()}
    palette = make_palette(num_classes=max(id2label.keys()) + 1)

    image_paths = collect_images(input_path)
    print(f"Found {len(image_paths)} image(s).")

    for image_path in tqdm(image_paths):
        process_one_image(
            image_path=image_path,
            out_root=out_root,
            processor=processor,
            model=model,
            device=device,
            palette=palette,
            id2label=id2label,
            gamma=args.gamma,
            min_area=args.min_area,
            alpha=args.alpha,
            low_conf_threshold=args.low_conf_threshold,
        )

    print(f"Done. Results saved to: {out_root}")


if __name__ == "__main__":
    main()