from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from build_team_family_portrait_fused import foreground_mask


ROOT = Path(__file__).resolve().parents[1]
TEAM_DIR = ROOT / "output" / "team_photo" / "real_family_photo"
SOURCE_GROUP = TEAM_DIR / "北京景从_2025真人全家福_33人_紧凑修正版_4K.png"
OUTPUT_4K = TEAM_DIR / "北京景从_2025真人全家福_33人_定妆照脸修复版_4K.png"
OUTPUT_NATIVE = TEAM_DIR / "北京景从_2025真人全家福_33人_定妆照脸修复版.png"
OUTPUT_PREVIEW = TEAM_DIR / "北京景从_2025真人全家福_33人_定妆照脸修复版_预览.jpg"
OUTPUT_LAYOUT = TEAM_DIR / "诊断_33人脸位映射.png"
OUTPUT_COMPARE = TEAM_DIR / "诊断_33人脸修复对照.jpg"

PORTRAITS = ROOT / "output" / "player_portraits"
EXTRA_PORTRAITS = ROOT / "output" / "extra_player_portraits"
CUTOUTS = ROOT / "output" / "team_photo" / "player_cutouts_fused"
FACE_CUTOUT_CACHE = ROOT / "output" / "team_photo" / "face_restore_cutouts"


@dataclass(frozen=True)
class Player:
    filename: str
    name: str
    number: str
    extra: bool = False

    @property
    def path(self) -> Path:
        folder = EXTRA_PORTRAITS if self.extra else PORTRAITS
        return folder / self.filename


# The ordering is deliberately identical to the fixed three-row team-photo layout.
PLAYERS = [
    # Back row: 12
    Player("01_王泽隆_26.png", "王泽隆", "26"),
    Player("02_陈海洋_12.png", "陈海洋", "12"),
    Player("03_赵贝_19.png", "赵贝", "19"),
    Player("07_王华辰_9.png", "王华辰", "9"),
    Player("04_顾晓然_22.png", "顾晓然", "22"),
    Player("05_武健宇_23.png", "武健宇", "23"),
    Player("06_袁涛_2.png", "袁涛", "2"),
    Player("08_汪栩_14.png", "汪栩", "14"),
    Player("09_李彬扬_6.png", "李彬扬", "6"),
    Player("10_霍永强_11.png", "霍永强", "11"),
    Player("11_王星宸_20.png", "王星宸", "20"),
    Player("12_张亮_27.png", "张亮", "27"),
    # Middle row: 11
    Player("13_詹子愚_36.png", "詹子愚", "36"),
    Player("14_陈全_4.png", "陈全", "4"),
    Player("22_邓欢_7.png", "邓欢", "7"),
    Player("15_吴树杰_30.png", "吴树杰", "30"),
    Player("16_唐慧_5.png", "唐慧", "5"),
    Player("17_蔡至钧_56.png", "蔡至钧", "56"),
    Player("18_张天颢_21.png", "张天颢", "21"),
    Player("19_张鑫_28.png", "张鑫", "28"),
    Player("20_范中昱_10.png", "范中昱", "10"),
    Player("21_么智鹏_17.png", "么智鹏", "17"),
    Player("23_王頔正树_39.png", "王頔正树", "39"),
    # Front row: 10
    Player("24_张忠浩_8.png", "张忠浩", "8"),
    Player("25_郭磊_1.png", "郭磊", "1"),
    Player("26_费子铭_32.png", "费子铭", "32"),
    Player("27_马雪峰_96.png", "马雪峰", "96"),
    Player("28_田晟玨_25.png", "田晟玨", "25"),
    Player("29_崔斯腾_99.png", "崔斯腾", "99"),
    Player("30_赵航_86.png", "赵航", "86"),
    Player("13_时元斌.png", "时元斌", "13", True),
    Player("29_张聪.png", "张聪", "29", True),
    Player("16_张曈叶.png", "张瞳叶", "16", True),
]

ROW_COUNTS = (12, 11, 10)
ROW_DETECTION = (
    # name, y0, y1, scale factor, neighbours, expected count
    ("back", 250, 620, 1.07, 8, 12),
    ("middle", 650, 1020, 1.07, 8, 11),
    ("front", 1000, 1380, 1.07, 6, 10),
)


def cascade() -> cv2.CascadeClassifier:
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    if detector.empty():
        raise RuntimeError("Unable to load OpenCV's frontal-face detector")
    return detector


def detect_group_faces(image_path: Path) -> list[tuple[int, int, int, int]]:
    bgr = cv2.imread(str(image_path))
    if bgr is None:
        raise FileNotFoundError(image_path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    detector = cascade()
    all_faces: list[tuple[int, int, int, int]] = []

    for row_name, y0, y1, scale_factor, neighbours, expected in ROW_DETECTION:
        faces = detector.detectMultiScale(
            gray[y0:y1],
            scaleFactor=scale_factor,
            minNeighbors=neighbours,
            minSize=(70, 70),
            maxSize=(200, 200),
        )
        row_faces = [
            (int(x), int(y + y0), int(w), int(h))
            for x, y, w, h in faces
            if w >= 90
        ]
        row_faces.sort(key=lambda box: box[0])
        if len(row_faces) != expected:
            raise RuntimeError(
                f"{row_name} row: expected {expected} faces, found {len(row_faces)}: "
                f"{row_faces}"
            )
        all_faces.extend(row_faces)

    if len(all_faces) != len(PLAYERS):
        raise RuntimeError(f"Expected {len(PLAYERS)} faces, found {len(all_faces)}")
    return all_faces


def detect_source_face(path: Path) -> tuple[int, int, int, int]:
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise FileNotFoundError(path)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    faces = cascade().detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=6,
        minSize=(120, 120),
        maxSize=(600, 600),
    )
    if len(faces) == 0:
        raise RuntimeError(f"No source face detected: {path.name}")
    x, y, w, h = max(faces, key=lambda box: int(box[2]) * int(box[3]))
    return int(x), int(y), int(w), int(h)


def expanded_head_box(
    face: tuple[int, int, int, int], image_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    x, y, w, h = face
    image_w, image_h = image_size
    left = max(0, round(x - 0.23 * w))
    top = max(0, round(y - 0.45 * h))
    right = min(image_w, round(x + w + 0.23 * w))
    bottom = min(image_h, round(y + h + 0.26 * h))
    return left, top, right, bottom


def alpha_for_player(player: Player, source: Image.Image) -> Image.Image:
    prefix = player.filename.split("_", 1)[0] + "_"
    matches = sorted(CUTOUTS.glob(prefix + "*.png")) if not player.extra else []
    if matches:
        cutout = Image.open(matches[0]).convert("RGBA")
        if cutout.size == source.size:
            return cutout.getchannel("A")

    FACE_CUTOUT_CACHE.mkdir(parents=True, exist_ok=True)
    cached = FACE_CUTOUT_CACHE / player.filename
    if cached.exists() and cached.stat().st_mtime >= player.path.stat().st_mtime:
        return Image.open(cached).convert("L")
    alpha = foreground_mask(source)
    alpha.save(cached, format="PNG", optimize=True)
    return alpha


def grade_head(head: Image.Image, row: int) -> Image.Image:
    alpha = head.getchannel("A")
    rgb = head.convert("RGB")
    rgb = ImageEnhance.Brightness(rgb).enhance((0.94, 0.97, 0.99)[row])
    rgb = ImageEnhance.Contrast(rgb).enhance((0.95, 0.97, 0.98)[row])
    rgb = ImageEnhance.Color(rgb).enhance((0.92, 0.95, 0.97)[row])
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def soften_head_alpha(alpha: Image.Image, row: int) -> Image.Image:
    array = np.asarray(alpha, dtype=np.float32) / 255.0
    height, _ = array.shape
    # Preserve every facial pixel; taper only the final neck band into the existing jersey.
    start = round(height * 0.78)
    if start < height:
        fade = np.linspace(1.0, 0.0, height - start, dtype=np.float32)[:, None]
        array[start:, :] *= fade
    softened = Image.fromarray(np.uint8(np.clip(array * 255.0, 0, 255)), "L")
    return softened.filter(ImageFilter.GaussianBlur((1.4, 1.15, 0.95)[row]))


def row_for_index(index: int) -> int:
    if index < ROW_COUNTS[0]:
        return 0
    if index < ROW_COUNTS[0] + ROW_COUNTS[1]:
        return 1
    return 2


def restore_faces(
    group: Image.Image,
    group_faces: list[tuple[int, int, int, int]],
) -> tuple[Image.Image, list[tuple[Player, Image.Image, tuple[int, int, int, int]]]]:
    result = group.convert("RGBA")
    comparisons: list[tuple[Player, Image.Image, tuple[int, int, int, int]]] = []

    for index, (player, target_face) in enumerate(zip(PLAYERS, group_faces, strict=True)):
        source = Image.open(player.path).convert("RGBA")
        source_alpha = alpha_for_player(player, source)
        source.putalpha(source_alpha)
        source_face = detect_source_face(player.path)
        source_box = expanded_head_box(source_face, source.size)
        target_box = expanded_head_box(target_face, result.size)

        head = source.crop(source_box)
        target_w = target_box[2] - target_box[0]
        target_h = target_box[3] - target_box[1]
        head = head.resize((target_w, target_h), Image.Resampling.LANCZOS)

        row = row_for_index(index)
        head = grade_head(head, row)
        head.putalpha(soften_head_alpha(head.getchannel("A"), row))
        result.alpha_composite(head, (target_box[0], target_box[1]))
        comparisons.append((player, source.crop(source_box), target_box))

    return result, comparisons


def draw_layout(
    group: Image.Image,
    faces: list[tuple[int, int, int, int]],
) -> None:
    diagnostic = group.convert("RGBA")
    overlay = Image.new("RGBA", diagnostic.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 38)
    for player, face in zip(PLAYERS, faces, strict=True):
        x, y, w, h = face
        head = expanded_head_box(face, diagnostic.size)
        draw.rectangle(head, outline=(0, 255, 100, 230), width=4)
        draw.rectangle((x, y, x + w, y + h), outline=(255, 210, 0, 230), width=3)
        label = player.number
        label_box = draw.textbbox((0, 0), label, font=font, stroke_width=2)
        label_w = label_box[2] - label_box[0] + 18
        draw.rounded_rectangle(
            (head[0], head[1] - 48, head[0] + label_w, head[1]),
            radius=7,
            fill=(0, 0, 0, 190),
        )
        draw.text(
            (head[0] + 9, head[1] - 46),
            label,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=2,
            stroke_fill=(0, 0, 0, 255),
        )
    diagnostic = Image.alpha_composite(diagnostic, overlay)
    diagnostic.save(OUTPUT_LAYOUT, format="PNG", optimize=True)


def make_comparison_sheet(
    restored: Image.Image,
    comparisons: list[tuple[Player, Image.Image, tuple[int, int, int, int]]],
) -> None:
    columns = 6
    tile_w, tile_h = 360, 220
    rows = (len(comparisons) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_w, rows * tile_h), (20, 21, 24))
    draw = ImageDraw.Draw(sheet)
    number_font = ImageFont.truetype(
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", 28
    )
    cn_font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 24)

    for index, (player, source_head, target_box) in enumerate(comparisons):
        col, row = index % columns, index // columns
        x0, y0 = col * tile_w, row * tile_h
        draw.rectangle((x0, y0, x0 + tile_w - 1, y0 + tile_h - 1), outline=(58, 60, 66))

        source_thumb = ImageOps.contain(source_head.convert("RGB"), (150, 155), Image.Resampling.LANCZOS)
        target_crop = restored.crop(target_box).convert("RGB")
        target_thumb = ImageOps.contain(target_crop, (150, 155), Image.Resampling.LANCZOS)
        sheet.paste(source_thumb, (x0 + 15 + (150 - source_thumb.width) // 2, y0 + 50))
        sheet.paste(target_thumb, (x0 + 195 + (150 - target_thumb.width) // 2, y0 + 50))
        draw.text((x0 + 14, y0 + 10), player.number, font=number_font, fill=(246, 166, 35))
        draw.text((x0 + 70, y0 + 13), player.name, font=cn_font, fill=(245, 245, 245))
        draw.text((x0 + 26, y0 + 193), "定妆照", font=cn_font, fill=(175, 177, 184))
        draw.text((x0 + 232, y0 + 193), "合影", font=cn_font, fill=(175, 177, 184))

    sheet.save(OUTPUT_COMPARE, format="JPEG", quality=94, optimize=True)


def verify_output(
    original: Image.Image,
    restored: Image.Image,
    faces: list[tuple[int, int, int, int]],
) -> None:
    if original.size != (3840, 2160) or restored.size != original.size:
        raise RuntimeError(f"Unexpected image size: {original.size} -> {restored.size}")
    if len(faces) != 33 or len(PLAYERS) != 33:
        raise RuntimeError("The output must contain exactly 33 mapped faces")

    before = np.asarray(original.convert("RGB"), dtype=np.int16)
    after = np.asarray(restored.convert("RGB"), dtype=np.int16)
    difference = np.max(np.abs(after - before), axis=2)
    allowed = np.zeros(difference.shape, dtype=bool)
    for face in faces:
        left, top, right, bottom = expanded_head_box(face, original.size)
        allowed[top:bottom, left:right] = True
    if np.any(difference[~allowed] != 0):
        raise RuntimeError("Pixels outside the 33 head regions were modified")
    if np.count_nonzero(difference[allowed] > 4) < 33 * 4000:
        raise RuntimeError("Too few face-region pixels changed; restoration may have failed")


def main() -> None:
    missing = [str(player.path) for player in PLAYERS if not player.path.exists()]
    if missing:
        raise FileNotFoundError("Missing player portraits:\n" + "\n".join(missing))

    group = Image.open(SOURCE_GROUP).convert("RGBA")
    faces = detect_group_faces(SOURCE_GROUP)
    draw_layout(group, faces)
    restored, comparisons = restore_faces(group, faces)
    verify_output(group, restored, faces)

    restored.convert("RGB").save(OUTPUT_4K, format="PNG", optimize=True)
    restored.resize((1672, 941), Image.Resampling.LANCZOS).convert("RGB").save(
        OUTPUT_NATIVE, format="PNG", optimize=True
    )
    restored.resize((1920, 1080), Image.Resampling.LANCZOS).convert("RGB").save(
        OUTPUT_PREVIEW, format="JPEG", quality=94, optimize=True, progressive=True
    )
    make_comparison_sheet(restored, comparisons)

    print(f"mapped_faces={len(faces)} rows={ROW_COUNTS}")
    print(f"saved={OUTPUT_4K}")
    print(f"saved={OUTPUT_NATIVE}")
    print(f"saved={OUTPUT_PREVIEW}")
    print(f"diagnostic={OUTPUT_LAYOUT}")
    print(f"comparison={OUTPUT_COMPARE}")


if __name__ == "__main__":
    main()
