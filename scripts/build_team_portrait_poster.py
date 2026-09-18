from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_DIR = ROOT / "output" / "player_portraits"
EXTRA_PORTRAIT_DIR = ROOT / "output" / "extra_player_portraits"
OUTPUT_DIR = ROOT / "output" / "team_photo"
BACKGROUND = Path(
    "/Users/bytedance/.codex/generated_images/"
    "01a03265-47a0-7d21-acd1-6475b8fe4fc8/"
    "exec-031414bd-8c3f-4317-b42d-c690b1ebdaca.png"
)
CREST = Path(
    "/var/folders/vk/j68mt4bd4gj4cnlphg13n8yw0000gn/T/"
    "codex-clipboard-219ce363-6937-4371-89e1-31253179c2b4.jpg"
)

BASE_ROSTER = [
    ("01_王泽隆_26.png", "王泽隆", "26"),
    ("02_陈海洋_12.png", "陈海洋", "12"),
    ("03_赵贝_19.png", "赵贝", "19"),
    ("04_顾晓然_22.png", "顾晓然", "22"),
    ("05_武健宇_23.png", "武健宇", "23"),
    ("06_袁涛_2.png", "袁涛", "2"),
    ("07_王华辰_9.png", "王华辰", "9"),
    ("08_汪栩_14.png", "汪栩", "14"),
    ("09_李彬扬_6.png", "李彬扬", "6"),
    ("10_霍永强_11.png", "霍永强", "11"),
    ("11_王星宸_20.png", "王星宸", "20"),
    ("12_张亮_27.png", "张亮", "27"),
    ("13_詹子愚_36.png", "詹子愚", "36"),
    ("14_陈全_4.png", "陈全", "4"),
    ("15_吴树杰_30.png", "吴树杰", "30"),
    ("16_唐慧_5.png", "唐慧", "5"),
    ("17_蔡至钧_56.png", "蔡至钧", "56"),
    ("18_张天颢_21.png", "张天颢", "21"),
    ("19_张鑫_28.png", "张鑫", "28"),
    ("20_范中昱_10.png", "范中昱", "10"),
    ("21_么智鹏_17.png", "么智鹏", "17"),
    ("22_邓欢_7.png", "邓欢", "7"),
    ("23_王頔正树_39.png", "王頔正树", "39"),
    ("24_张忠浩_8.png", "张忠浩", "8"),
    ("25_郭磊_1.png", "郭磊", "1"),
    ("26_费子铭_32.png", "费子铭", "32"),
    ("27_马雪峰_96.png", "马雪峰", "96"),
    ("28_田晟玨_25.png", "田晟玨", "25"),
    ("29_崔斯腾_99.png", "崔斯腾", "99"),
    ("30_赵航_86.png", "赵航", "86"),
]

EXTRA_ROSTER = [
    ("13_时元斌.png", "时元斌", "13"),
    ("29_张聪.png", "张聪", "29"),
    # Use the latest spelling supplied by the user; keep the existing source filename.
    ("16_张曈叶.png", "张瞳叶", "16"),
]

# Per-player framing corrections requested for the team poster only.
# Values below 1 reveal more of the portrait; values above 1 enlarge it.
PORTRAIT_SCALE = {
    "15_吴树杰_30.png": 0.88,
    "25_郭磊_1.png": 0.88,
    "14_陈全_4.png": 1.07,
}

W, H = 7680, 4320
CARD_W, CARD_H = 620, 783
GAP_X, GAP_Y = 20, 42
GRID_Y = 1270

CN_FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
EN_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS, centering=(0.5, 0.45))


def portrait_path(filename: str) -> Path:
    base = PORTRAIT_DIR / filename
    if base.exists():
        return base
    return EXTRA_PORTRAIT_DIR / filename


def portrait_background(size: tuple[int, int]) -> Image.Image:
    """Build a neutral studio backdrop for portraits intentionally framed smaller."""
    background = Image.new("RGB", size, (11, 12, 14))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse(
        (-size[0] // 4, -size[1] // 5, size[0] * 5 // 4, size[1] * 4 // 5),
        fill=(92, 92, 92, 95),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(max(size) // 5))
    return Image.alpha_composite(background.convert("RGBA"), glow).convert("RGB")


def frame_portrait(image: Image.Image, size: tuple[int, int], scale: float = 1.0) -> Image.Image:
    """Frame a portrait without redrawing it, allowing controlled subject scale."""
    image = image.convert("RGB")
    target_w, target_h = size
    source_w, source_h = image.size
    cover_scale = max(target_w / source_w, target_h / source_h)
    resize_scale = cover_scale * scale
    resized = image.resize(
        (max(1, round(source_w * resize_scale)), max(1, round(source_h * resize_scale))),
        Image.Resampling.LANCZOS,
    )

    if scale >= 1:
        left = max(0, (resized.width - target_w) // 2)
        top = max(0, round((resized.height - target_h) * 0.45))
        return resized.crop((left, top, left + target_w, top + target_h))

    background = portrait_background(size)
    x = (target_w - resized.width) // 2
    y = round((target_h - resized.height) * 0.45)
    feather = max(14, round(min(resized.size) * 0.035))
    alpha = Image.new("L", resized.size, 0)
    ImageDraw.Draw(alpha).rectangle(
        (feather, feather, resized.width - feather - 1, resized.height - feather - 1),
        fill=255,
    )
    alpha = alpha.filter(ImageFilter.GaussianBlur(feather))
    background.paste(resized, (x, y), alpha)
    return background


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=radius, fill=255)
    return mask


def text_center(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill, stroke=0):
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    x = xy[0] - (box[2] - box[0]) // 2
    y = xy[1] - (box[3] - box[1]) // 2 - box[1]
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill="#000000")


def render_poster(
    roster: list[tuple[str, str, str]],
    row_counts: list[int],
    output_name: str,
    preview_name: str,
    footer_text: str,
) -> None:
    expected = sum(row_counts)
    missing = [filename for filename, _, _ in roster if not portrait_path(filename).exists()]
    assert len(roster) == expected
    assert not missing, f"Missing portraits: {missing}"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bg = fit_cover(Image.open(BACKGROUND), (W, H))
    bg = ImageEnhance.Brightness(bg).enhance(0.62)
    bg = ImageEnhance.Contrast(bg).enhance(1.1)
    canvas = bg.convert("RGBA")

    # Readability overlays retain the generated black-and-gold atmosphere.
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle((0, 0, W, 1180), fill=(0, 0, 0, 112))
    sd.rectangle((0, 1120, W, H), fill=(0, 0, 0, 62))
    shade = shade.filter(ImageFilter.GaussianBlur(20))
    canvas = Image.alpha_composite(canvas, shade)

    # Official crest is used directly, never re-rendered.
    crest = Image.open(CREST).convert("RGB")
    crest = ImageOps.fit(crest, (730, 730), Image.Resampling.LANCZOS)
    crest_mask = Image.new("L", crest.size, 0)
    ImageDraw.Draw(crest_mask).ellipse((8, 8, 721, 721), fill=255)
    crest_layer = Image.new("RGBA", crest.size, (0, 0, 0, 0))
    crest_layer.paste(crest, (0, 0), crest_mask)
    canvas.alpha_composite(crest_layer, (360, 260))

    draw = ImageDraw.Draw(canvas)
    gold = "#F6A623"
    title_cn = ImageFont.truetype(CN_FONT, 260)
    title_en = ImageFont.truetype(EN_FONT, 118)
    subtitle = ImageFont.truetype(EN_FONT, 74)
    text_center(draw, (W // 2 + 330, 430), "北京景从", title_cn, "#FFFFFF", 3)
    text_center(draw, (W // 2 + 330, 710), "BEIJING JINGCONG FC", title_en, gold, 2)
    text_center(draw, (W // 2 + 330, 890), "2025  ·  TEAM PORTRAIT", subtitle, "#DADADA")
    draw.rounded_rectangle((1380, 1040, W - 620, 1054), radius=7, fill=gold)

    name_font = ImageFont.truetype(CN_FONT, 50)
    number_font = ImageFont.truetype(EN_FONT, 55)
    card_mask = rounded_mask((CARD_W, CARD_H), 28)

    roster_index = 0
    for row, row_count in enumerate(row_counts):
        row_width = row_count * CARD_W + (row_count - 1) * GAP_X
        row_x = (W - row_width) // 2
        for col in range(row_count):
            filename, name, number = roster[roster_index]
            roster_index += 1
            x = row_x + col * (CARD_W + GAP_X)
            y = GRID_Y + row * (CARD_H + GAP_Y)

            scale = PORTRAIT_SCALE.get(filename, 1.0)
            portrait = frame_portrait(Image.open(portrait_path(filename)), (CARD_W, CARD_H), scale)
            card = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
            card.paste(portrait, (0, 0), card_mask)

            # Dark identity strip with exact roster number and name.
            strip_h = 105
            strip = Image.new("RGBA", (CARD_W, strip_h), (7, 8, 10, 212))
            card.alpha_composite(strip, (0, CARD_H - strip_h))
            cd = ImageDraw.Draw(card)
            cd.text((30, CARD_H - 89), number, font=number_font, fill=gold)
            name_box = cd.textbbox((0, 0), name, font=name_font)
            cd.text(
                (CARD_W - 30 - (name_box[2] - name_box[0]), CARD_H - 83),
                name,
                font=name_font,
                fill="#FFFFFF",
            )
            cd.rounded_rectangle(
                (2, 2, CARD_W - 3, CARD_H - 3),
                radius=28,
                outline=(246, 166, 35, 225),
                width=5,
            )

            shadow = Image.new("RGBA", (CARD_W + 42, CARD_H + 42), (0, 0, 0, 0))
            shd = ImageDraw.Draw(shadow)
            shd.rounded_rectangle((18, 18, CARD_W + 18, CARD_H + 18), radius=32, fill=(0, 0, 0, 150))
            shadow = shadow.filter(ImageFilter.GaussianBlur(16))
            canvas.alpha_composite(shadow, (x - 18, y - 12))
            canvas.alpha_composite(card, (x, y))

    assert roster_index == expected

    footer_font = ImageFont.truetype(CN_FONT, 54)
    text_center(draw, (W // 2, H - 145), footer_text, footer_font, "#C8C8C8")

    out = OUTPUT_DIR / output_name
    canvas.convert("RGB").save(out, quality=96, optimize=True)

    preview = OUTPUT_DIR / preview_name
    preview_image = canvas.convert("RGB").resize((3840, 2160), Image.Resampling.LANCZOS)
    preview_image.save(preview, format="JPEG", quality=91, optimize=True, progressive=True)

    assert out.exists() and out.stat().st_size > 1_000_000
    assert preview.exists() and 500_000 < preview.stat().st_size < 10_000_000
    with Image.open(out) as check:
        assert check.size == (W, H)
    with Image.open(preview) as check:
        assert check.size == (3840, 2160)
    print(out)
    print(f"players={len(roster)} size={W}x{H} bytes={out.stat().st_size}")
    print(preview)
    print(f"preview=3840x2160 bytes={preview.stat().st_size}")


def main() -> None:
    assert len(BASE_ROSTER) == 30
    assert len(EXTRA_ROSTER) == 3

    roster_31 = BASE_ROSTER + EXTRA_ROSTER[:1]
    render_poster(
        roster_31,
        [10, 11, 10],
        "北京景从_2025全员定妆照大合影.png",
        "北京景从_2025全员定妆照大合影_飞书预览.jpg",
        "三十一人完整阵容 · 官方定妆照",
    )

    roster_33 = BASE_ROSTER + EXTRA_ROSTER
    render_poster(
        roster_33,
        [11, 11, 11],
        "北京景从_2025全员定妆照大合影_33人版.png",
        "北京景从_2025全员定妆照大合影_33人版_飞书预览.jpg",
        "三十三人完整阵容 · 官方定妆照",
    )


if __name__ == "__main__":
    main()
