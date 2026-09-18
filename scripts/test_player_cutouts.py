from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PORTRAITS = ROOT / "output" / "player_portraits"
OUT = ROOT / "output" / "team_photo" / "cutout_test"
SAMPLES = [
    "14_陈全_4.png",
    "17_蔡至钧_56.png",
    "29_崔斯腾_99.png",
]


def largest_component(mask: np.ndarray) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if count <= 1:
        return mask
    candidates = []
    h, w = mask.shape
    for label in range(1, count):
        area = stats[label, cv2.CC_STAT_AREA]
        x = stats[label, cv2.CC_STAT_LEFT]
        width = stats[label, cv2.CC_STAT_WIDTH]
        contains_center = x < w // 2 < x + width
        candidates.append((contains_center, area, label))
    label = max(candidates)[2]
    return np.where(labels == label, 255, 0).astype(np.uint8)


def foreground_mask(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"))
    h0, w0 = rgb.shape[:2]
    scale = min(1.0, 980 / max(h0, w0))
    w, h = int(w0 * scale), int(h0 * scale)
    small = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_AREA)
    bgr = cv2.cvtColor(small, cv2.COLOR_RGB2BGR)

    # Shape prior: head, neck, sloped shoulders, arms and torso. It prevents the
    # charcoal studio wall from surviving while leaving GrabCut room to find hair.
    prior = np.zeros((h, w), np.uint8)
    silhouette = np.array([
        [0.31*w, 0.10*h], [0.40*w, 0.055*h], [0.60*w, 0.055*h],
        [0.69*w, 0.10*h], [0.74*w, 0.27*h], [0.68*w, 0.47*h],
        [0.89*w, 0.57*h], [0.99*w, 0.73*h], [w, h], [0, h],
        [0.01*w, 0.73*h], [0.11*w, 0.57*h], [0.32*w, 0.47*h],
        [0.26*w, 0.27*h],
    ], np.int32)
    cv2.fillPoly(prior, [silhouette], 255)

    mask = np.full((h, w), cv2.GC_BGD, np.uint8)
    mask[prior > 0] = cv2.GC_PR_FGD
    # Strong foreground seeds are deliberately well inside the body.
    cv2.ellipse(mask, (w//2, int(0.29*h)), (int(0.13*w), int(0.20*h)), 0, 0, 360, cv2.GC_FGD, -1)
    torso = np.array([
        [0.40*w, 0.48*h], [0.60*w, 0.48*h],
        [0.73*w, 0.98*h], [0.27*w, 0.98*h],
    ], np.int32)
    cv2.fillPoly(mask, [torso], cv2.GC_FGD)
    # Coloured piping, white numbers and skin against the black shirt are reliable.
    hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
    bright = (hsv[:, :, 2] > 72) & (prior > 0)
    mask[bright] = cv2.GC_FGD

    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, None, bg_model, fg_model, 8, cv2.GC_INIT_WITH_MASK)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    alpha = largest_component(alpha)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=2)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.25)
    alpha = cv2.resize(alpha, (w0, h0), interpolation=cv2.INTER_LANCZOS4)
    return Image.fromarray(alpha, "L")


def checker(size: tuple[int, int]) -> Image.Image:
    w, h = size
    tile = 48
    bg = Image.new("RGB", size, "#83919a")
    draw = ImageDraw.Draw(bg)
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle((x, y, x+tile, y+tile), fill="#b8c0c5")
    return bg


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    panels = []
    for name in SAMPLES:
        image = Image.open(PORTRAITS / name).convert("RGBA")
        alpha = foreground_mask(image)
        image.putalpha(alpha)
        image.save(OUT / name)
        panel = ImageOps.contain(image, (900, 1120), Image.Resampling.LANCZOS)
        bg = checker((900, 1120)).convert("RGBA")
        bg.alpha_composite(panel, ((900-panel.width)//2, 1120-panel.height))
        panels.append(bg)

    contact = Image.new("RGB", (2700, 1120), "#94a0a7")
    for idx, panel in enumerate(panels):
        contact.paste(panel.convert("RGB"), (idx*900, 0))
    contact.save(OUT / "三人抠图边缘测试.jpg", quality=94)
    print(OUT / "三人抠图边缘测试.jpg")


if __name__ == "__main__":
    main()
