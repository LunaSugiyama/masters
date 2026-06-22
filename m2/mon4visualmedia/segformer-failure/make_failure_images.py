from PIL import Image, ImageEnhance, ImageFilter
from pathlib import Path
import numpy as np
import random
import io


input_path = Path("images/test.png")  # change if needed
out_dir = Path("images_failure_hard")
out_dir.mkdir(exist_ok=True)

img = Image.open(input_path).convert("RGB")


def save(img, name):
    img.save(out_dir / name)


def add_noise(image, sigma=35):
    arr = np.asarray(image).astype(np.float32)
    noise = np.random.normal(0, sigma, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def add_fog(image, strength=0.75):
    arr = np.asarray(image).astype(np.float32)
    fog = np.ones_like(arr) * 255
    out = arr * (1 - strength) + fog * strength
    out = np.clip(out, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def add_blue_night(image, brightness=0.12):
    arr = np.asarray(image).astype(np.float32)
    arr *= brightness
    arr[:, :, 0] *= 0.65  # red down
    arr[:, :, 1] *= 0.75  # green down
    arr[:, :, 2] *= 1.45  # blue up
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def jpeg_compress(image, quality=5):
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def pixelate(image, small_width=96):
    w, h = image.size
    small_h = int(h * small_width / w)
    small = image.resize((small_width, small_h), Image.Resampling.BILINEAR)
    return small.resize((w, h), Image.Resampling.NEAREST)


def motion_blur(image, radius=11):
    # simple horizontal blur kernel
    size = radius
    kernel = [0] * (size * size)
    center = size // 2
    for i in range(size):
        kernel[center * size + i] = 1
    kernel = [v / size for v in kernel]
    return image.filter(ImageFilter.Kernel((size, size), kernel, scale=1))


def add_occlusion(image, num_boxes=8):
    image = image.copy()
    arr = np.asarray(image).copy()
    h, w, _ = arr.shape

    for _ in range(num_boxes):
        x1 = random.randint(0, w - 1)
        y1 = random.randint(0, h - 1)
        box_w = random.randint(w // 12, w // 4)
        box_h = random.randint(h // 12, h // 4)
        x2 = min(w, x1 + box_w)
        y2 = min(h, y1 + box_h)

        color = random.choice([
            [0, 0, 0],
            [255, 255, 255],
            [120, 120, 120],
        ])
        arr[y1:y2, x1:x2] = color

    return Image.fromarray(arr)


# 1. Strong low-light
dark = ImageEnhance.Brightness(img).enhance(0.10)
dark = ImageEnhance.Contrast(dark).enhance(0.55)
save(dark, "failure_01_extreme_dark.png")

# 2. Low-light + sensor noise
dark_noise = add_noise(dark, sigma=28)
save(dark_noise, "failure_02_dark_noise.png")

# 3. Blue night image
blue_night = add_blue_night(img, brightness=0.13)
blue_night = add_noise(blue_night, sigma=20)
save(blue_night, "failure_03_blue_night_noise.png")

# 4. Heavy fog / haze
fog = add_fog(img, strength=0.78)
fog = ImageEnhance.Contrast(fog).enhance(0.45)
save(fog, "failure_04_heavy_fog.png")

# 5. Overexposure / whiteout
over = ImageEnhance.Brightness(img).enhance(2.2)
over = ImageEnhance.Contrast(over).enhance(0.35)
save(over, "failure_05_overexposed.png")

# 6. Strong motion blur
blur = motion_blur(img, radius=17)
save(blur, "failure_06_motion_blur.png")

# 7. Pixelation / small object loss
pix = pixelate(img, small_width=96)
save(pix, "failure_07_pixelated_96px.png")

# 8. JPEG compression artifact
jpeg = jpeg_compress(img, quality=4)
save(jpeg, "failure_08_jpeg_quality4.jpg")

# 9. Random occlusion
occ = add_occlusion(img, num_boxes=10)
save(occ, "failure_09_occlusion.png")

# 10. Combined worst case
combined = ImageEnhance.Brightness(img).enhance(0.12)
combined = ImageEnhance.Contrast(combined).enhance(0.45)
combined = motion_blur(combined, radius=13)
combined = add_noise(combined, sigma=35)
combined = jpeg_compress(combined, quality=8)
save(combined, "failure_10_dark_blur_noise_jpeg.jpg")

print(f"Saved hard failure images to {out_dir}")