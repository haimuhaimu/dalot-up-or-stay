from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PORTRAITS = ROOT / "output" / "player_portraits"
OUT_DIR = ROOT / "output" / "team_photo"
CUTOUT_DIR = OUT_DIR / "player_cutouts_fused"
BACKGROUND = OUT_DIR / "全家福_融合版空球场背景.png"
CREST = Path(
    "/var/folders/vk/j68mt4bd4gj4cnlphg13n8yw0000gn/T/"
    "codex-clipboard-219ce363-6937-4371-89e1-31253179c2b4.jpg"
)

ROSTER = [
    "01_王泽隆_26.png", "02_陈海洋_12.png", "03_赵贝_19.png",
    "04_顾晓然_22.png", "05_武健宇_23.png", "06_袁涛_2.png",
    "07_王华辰_9.png", "08_汪栩_14.png", "09_李彬扬_6.png",
    "10_霍永强_11.png", "11_王星宸_20.png", "12_张亮_27.png",
    "13_詹子愚_36.png", "14_陈全_4.png", "15_吴树杰_30.png",
    "16_唐慧_5.png", "17_蔡至钧_56.png", "18_张天颢_21.png",
    "19_张鑫_28.png", "20_范中昱_10.png", "21_么智鹏_17.png",
    "22_邓欢_7.png", "23_王頔正树_39.png", "24_张忠浩_8.png",
    "25_郭磊_1.png", "26_费子铭_32.png", "27_马雪峰_96.png",
    "28_田晟玨_25.png", "29_崔斯腾_99.png", "30_赵航_86.png",
]

W, H = 7680, 4320
CN_FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
EN_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def largest_component(mask: np.ndarray) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if count <= 1:
        return mask
    h, w = mask.shape
    candidates = []
    for label in range(1, count):
        area = stats[label, cv2.CC_STAT_AREA]
        x = stats[label, cv2.CC_STAT_LEFT]
        width = stats[label, cv2.CC_STAT_WIDTH]
        candidates.append((x < w // 2 < x + width, area, label))
    keep = max(candidates)[2]
    return np.where(labels == keep, 255, 0).astype(np.uint8)


def foreground_mask(image: Image.Image) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"))
    h0, w0 = rgb.shape[:2]
    scale = min(1.0, 980 / max(h0, w0))
    w, h = int(w0 * scale), int(h0 * scale)
    small = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_AREA)
    bgr = cv2.cvtColor(small, cv2.COLOR_RGB2BGR)

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
    cv2.ellipse(
        mask, (w//2, int(0.29*h)), (int(0.13*w), int(0.20*h)),
        0, 0, 360, cv2.GC_FGD, -1,
    )
    torso = np.array([
        [0.41*w, 0.49*h], [0.59*w, 0.49*h],
        [0.66*w, 0.98*h], [0.34*w, 0.98*h],
    ], np.int32)
    cv2.fillPoly(mask, [torso], cv2.GC_FGD)
    hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
    reliable_detail = (hsv[:, :, 2] > 72) & (prior > 0)
    mask[reliable_detail] = cv2.GC_FGD

    bg_model = np.zeros((1, 65), np.float64)
    fg_model = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, None, bg_model, fg_model, 8, cv2.GC_INIT_WITH_MASK)
    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0,
    ).astype(np.uint8)
    alpha = largest_component(alpha)
    alpha = cv2.morphologyEx(
        alpha, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8), iterations=2,
    )
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.2)
    alpha = cv2.resize(alpha, (w0, h0), interpolation=cv2.INTER_LANCZOS4)
    return Image.fromarray(alpha, "L")


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        image.convert("RGB"), size, Image.Resampling.LANCZOS,
        centering=(0.5, 0.46),
    )


def grade_player(image: Image.Image, row: int) -> Image.Image:
    alpha = image.getchannel("A")
    rgb = image.convert("RGB")
    # Match the stadium's softer overcast daylight while preserving jersey detail.
    rgb = ImageEnhance.Contrast(rgb).enhance((0.94, 0.97, 1.00)[row])
    rgb = ImageEnhance.Color(rgb).enhance((0.87, 0.91, 0.95)[row])
    rgb = ImageEnhance.Brightness(rgb).enhance((0.94, 0.97, 0.99)[row])
    cool = Image.new("RGB", rgb.size, (70, 92, 108))
    rgb = Image.blend(rgb, cool, (0.035, 0.026, 0.018)[row])
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    if row == 0:
        result = result.filter(ImageFilter.GaussianBlur(0.8))
    elif row == 1:
        result = result.filter(ImageFilter.GaussianBlur(0.35))
    return result


def make_cutout(path: Path) -> Image.Image:
    target = CUTOUT_DIR / path.name
    if target.exists() and target.stat().st_mtime >= path.stat().st_mtime:
        return Image.open(target).convert("RGBA")
    source = Image.open(path).convert("RGBA")
    source.putalpha(foreground_mask(source))
    source.save(target, format="PNG", optimize=True)
    return source


def resize_to_height(image: Image.Image, height: int) -> Image.Image:
    width = round(image.width * height / image.height)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def paste_shadow(canvas: Image.Image, player: Image.Image, x: int, y: int, row: int) -> None:
    alpha = player.getchannel("A")
    alpha = alpha.filter(ImageFilter.GaussianBlur((25, 22, 18)[row]))
    opacity = (0.36, 0.42, 0.48)[row]
    alpha = alpha.point(lambda value: int(value * opacity))
    shadow = Image.new("RGBA", player.size, (4, 8, 12, 0))
    shadow.putalpha(alpha)
    canvas.alpha_composite(shadow, (x + 22, y + (28, 24, 20)[row]))


def center_text(draw, center_x, y, text, font, fill, stroke_width=0):
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = center_x - (box[2] - box[0]) // 2
    draw.text(
        (x, y), text, font=font, fill=fill,
        stroke_width=stroke_width, stroke_fill="#0A0D12",
    )


def paste_header(canvas: Image.Image) -> None:
    veil = Image.new("RGBA", (W, 830), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    vd.rectangle((0, 0, W, 710), fill=(2, 6, 10, 78))
    veil = veil.filter(ImageFilter.GaussianBlur(22))
    canvas.alpha_composite(veil, (0, 0))

    crest = ImageOps.fit(Image.open(CREST).convert("RGB"), (330, 330), Image.Resampling.LANCZOS)
    crest_mask = Image.new("L", crest.size, 0)
    ImageDraw.Draw(crest_mask).ellipse((3, 3, 326, 326), fill=255)
    crest_layer = Image.new("RGBA", crest.size, (0, 0, 0, 0))
    crest_layer.paste(crest, (0, 0), crest_mask)
    canvas.alpha_composite(crest_layer, (W//2 - 165, 70))

    draw = ImageDraw.Draw(canvas)
    cn = ImageFont.truetype(CN_FONT, 128)
    en = ImageFont.truetype(EN_FONT, 58)
    center_text(draw, W//2, 410, "北京景从足球俱乐部", cn, "#FFFFFF", 2)
    center_text(draw, W//2, 556, "BEIJING JINGCONG FC  ·  2025 TEAM", en, "#F4A42B", 2)


def main() -> None:
    assert len(ROSTER) == 30
    missing = [name for name in ROSTER if not (PORTRAITS / name).exists()]
    assert not missing, f"missing portraits: {missing}"
    assert BACKGROUND.exists() and CREST.exists()
    CUTOUT_DIR.mkdir(parents=True, exist_ok=True)

    background = fit_cover(Image.open(BACKGROUND), (W, H))
    background = ImageEnhance.Color(background).enhance(0.90)
    background = ImageEnhance.Contrast(background).enhance(0.96)
    background = background.filter(ImageFilter.GaussianBlur(0.65))
    canvas = background.convert("RGBA")

    cutouts = [make_cutout(PORTRAITS / name) for name in ROSTER]
    row_specs = [
        (0, 10, 1780, 930),
        (10, 20, 1940, 1810),
        (20, 30, 2100, 2690),
    ]
    centers = [660 + round(index * (6360 / 9)) for index in range(10)]

    pasted = 0
    for row, (start, end, target_height, y) in enumerate(row_specs):
        prepared = []
        for slot, idx in enumerate(range(start, end)):
            player = resize_to_height(cutouts[idx], target_height)
            player = grade_player(player, row)
            x = centers[slot] - player.width // 2
            prepared.append((slot, x, player))

        # Outer players first and central players last creates symmetric shoulder
        # occlusion instead of an obvious left-to-right stack.
        for _, x, player in sorted(prepared, key=lambda item: abs(item[0] - 4.5), reverse=True):
            paste_shadow(canvas, player, x, y, row)
            canvas.alpha_composite(player, (x, y))
            pasted += 1

    assert pasted == 30

    # A single camera/film pass makes player and location share the same image response.
    unified = canvas.convert("RGB")
    unified = ImageEnhance.Contrast(unified).enhance(0.985)
    unified = ImageEnhance.Color(unified).enhance(0.965)
    cool_grade = Image.new("RGB", unified.size, (25, 39, 50))
    unified = Image.blend(unified, cool_grade, 0.018)
    canvas = unified.convert("RGBA")
    paste_header(canvas)

    full = OUT_DIR / "北京景从_2025全员三排全家福_融合版.png"
    preview = OUT_DIR / "北京景从_2025全员三排全家福_融合版_飞书预览.jpg"
    canvas.convert("RGB").save(full, format="PNG", optimize=True)
    small = canvas.convert("RGB").resize((3840, 2160), Image.Resampling.LANCZOS)
    small.save(preview, format="JPEG", quality=93, optimize=True, progressive=True)

    assert full.exists() and full.stat().st_size > 1_000_000
    assert preview.exists() and 500_000 < preview.stat().st_size < 10_000_000
    with Image.open(full) as check:
        assert check.size == (W, H)
    with Image.open(preview) as check:
        assert check.size == (3840, 2160)
    print(full)
    print(f"players={pasted} size={W}x{H} bytes={full.stat().st_size}")
    print(preview)
    print(f"preview=3840x2160 bytes={preview.stat().st_size}")


if __name__ == "__main__":
    main()
