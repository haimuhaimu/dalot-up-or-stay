from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import restore_team_photo_faces as base
import refine_team_photo_faces_nongenerative as refined


OUT = base.TEAM_DIR / "诊断_33人头肩比例总览.jpg"


def main() -> None:
    image = Image.open(refined.OUT).convert("RGB")
    faces = base.detect_group_faces(base.SOURCE_GROUP)
    normalized, _ = refined.normalized_face_boxes(faces)
    columns = 6
    tile_w, tile_h = 360, 300
    rows = (len(normalized) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_w, rows * tile_h), (18, 19, 22))
    draw = ImageDraw.Draw(sheet)
    number_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30
    )
    cn_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 24)

    for index, (player, face) in enumerate(zip(base.PLAYERS, normalized, strict=True)):
        x, y, w, h = face
        left = max(0, round(x - 1.05 * w))
        right = min(image.width, round(x + 2.05 * w))
        top = max(0, round(y - 0.60 * h))
        bottom = min(image.height, round(y + 2.70 * h))
        crop = image.crop((left, top, right, bottom))
        crop = ImageOps.fit(crop, (320, 245), Image.Resampling.LANCZOS, centering=(0.5, 0.38))
        col, row = index % columns, index // columns
        x0, y0 = col * tile_w, row * tile_h
        sheet.paste(crop, (x0 + 20, y0 + 45))
        draw.text((x0 + 18, y0 + 8), player.number, font=number_font, fill=(246, 166, 35))
        draw.text((x0 + 75, y0 + 10), player.name, font=cn_font, fill=(245, 245, 245))
        draw.rectangle((x0, y0, x0 + tile_w - 1, y0 + tile_h - 1), outline=(60, 62, 68))

    sheet.save(OUT, format="JPEG", quality=95, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
