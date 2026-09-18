from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PORTRAITS = ROOT / "output" / "player_portraits"
OUT_DIR = ROOT / "output" / "team_photo"
BACKGROUND = OUT_DIR / "全家福_空球场背景.png"
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


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        image.convert("RGB"), size, Image.Resampling.LANCZOS,
        centering=(0.5, 0.44),
    )


def feathered_player(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    player = fit_cover(image, size).convert("RGBA")
    width, height = size
    mask = Image.new("L", size, 0)
    pixels = mask.load()
    side = max(28, int(width * 0.12))
    bottom_start = int(height * 0.79)
    for y in range(height):
        if y < 8:
            y_alpha = int(255 * y / 8)
        elif y <= bottom_start:
            y_alpha = 255
        else:
            y_alpha = max(0, int(255 * (height - y) / (height - bottom_start)))
        for x in range(width):
            if x < side:
                x_alpha = int(255 * x / side)
            elif x >= width - side:
                x_alpha = int(255 * (width - 1 - x) / side)
            else:
                x_alpha = 255
            pixels[x, y] = min(x_alpha, y_alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(11))
    player.putalpha(mask)
    return player


def paste_crest(canvas: Image.Image) -> None:
    crest = Image.open(CREST).convert("RGB")
    crest = ImageOps.fit(crest, (420, 420), Image.Resampling.LANCZOS)
    mask = Image.new("L", crest.size, 0)
    ImageDraw.Draw(mask).ellipse((4, 4, 415, 415), fill=255)
    layer = Image.new("RGBA", crest.size, (0, 0, 0, 0))
    layer.paste(crest, (0, 0), mask)
    canvas.alpha_composite(layer, (W // 2 - 210, 120))


def center_text(draw, center_x, y, text, font, fill, stroke_width=0):
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    x = center_x - (box[2] - box[0]) // 2
    draw.text(
        (x, y), text, font=font, fill=fill,
        stroke_width=stroke_width, stroke_fill="#111111",
    )


def main() -> None:
    expected = 30
    assert len(ROSTER) == expected
    missing = [name for name in ROSTER if not (PORTRAITS / name).exists()]
    assert not missing, f"missing portraits: {missing}"
    assert BACKGROUND.exists()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base = fit_cover(Image.open(BACKGROUND), (W, H))
    base = ImageEnhance.Color(base).enhance(0.88)
    base = ImageEnhance.Contrast(base).enhance(1.04)
    canvas = base.convert("RGBA")

    # Unify the individual charcoal portrait backdrops with the black stadium risers.
    blend = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blend)
    bd.rounded_rectangle((350, 770, W - 350, 4020), radius=150, fill=(0, 0, 0, 110))
    blend = blend.filter(ImageFilter.GaussianBlur(65))
    canvas = Image.alpha_composite(canvas, blend)

    # Back, middle, and seated/front rows: ten verified portraits in each row.
    row_specs = [
        (0, 10, 632, 790, 570, 1070),
        (10, 20, 694, 868, 624, 1940),
        (20, 30, 758, 948, 676, 2840),
    ]
    pasted = 0
    for start, end, pw, ph, step, y in row_specs:
        total_width = pw + step * 9
        start_x = (W - total_width) // 2
        for slot, idx in enumerate(range(start, end)):
            x = start_x + slot * step
            player = feathered_player(Image.open(PORTRAITS / ROSTER[idx]), (pw, ph))
            shadow = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            sh = Image.new("L", (pw, ph), 0)
            ImageDraw.Draw(sh).ellipse((pw * 0.18, ph * 0.22, pw * 0.82, ph * 0.98), fill=145)
            sh = sh.filter(ImageFilter.GaussianBlur(32))
            shadow.putalpha(sh)
            canvas.alpha_composite(shadow, (x + 12, y + 24))
            canvas.alpha_composite(player, (x, y))
            pasted += 1
    assert pasted == expected

    # A restrained official header keeps the result like a team photograph, not a card grid.
    top = Image.new("RGBA", (W, 790), (0, 0, 0, 0))
    td = ImageDraw.Draw(top)
    td.rectangle((0, 0, W, 690), fill=(0, 0, 0, 92))
    top = top.filter(ImageFilter.GaussianBlur(20))
    canvas.alpha_composite(top, (0, 0))
    paste_crest(canvas)
    draw = ImageDraw.Draw(canvas)
    cn = ImageFont.truetype(CN_FONT, 154)
    en = ImageFont.truetype(EN_FONT, 74)
    center_text(draw, W // 2, 565, "北京景从足球俱乐部", cn, "#FFFFFF", 2)
    center_text(draw, W // 2, 738, "BEIJING JINGCONG FC  ·  2025 TEAM", en, "#F6A623", 2)

    # Grounding shadow ties the front row to the chairs/grass.
    ground = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ground)
    gd.ellipse((900, 3810, W - 900, 4230), fill=(0, 0, 0, 90))
    ground = ground.filter(ImageFilter.GaussianBlur(75))
    canvas = Image.alpha_composite(canvas, ground)

    full = OUT_DIR / "北京景从_2025全员三排全家福.png"
    preview = OUT_DIR / "北京景从_2025全员三排全家福_飞书预览.jpg"
    canvas.convert("RGB").save(full, format="PNG", optimize=True)
    small = canvas.convert("RGB").resize((3840, 2160), Image.Resampling.LANCZOS)
    small.save(preview, format="JPEG", quality=92, optimize=True, progressive=True)

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
