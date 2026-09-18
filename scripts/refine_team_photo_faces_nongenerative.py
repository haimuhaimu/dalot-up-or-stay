from __future__ import annotations

from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import restore_team_photo_faces as base


OUT = base.TEAM_DIR / "北京景从_2025真人全家福_33人_无重绘融合优化版_4K.png"
OUT_NATIVE = base.TEAM_DIR / "北京景从_2025真人全家福_33人_无重绘融合优化版.png"
OUT_PREVIEW = base.TEAM_DIR / "北京景从_2025真人全家福_33人_无重绘融合优化版_预览.jpg"
OUT_COMPARE = base.TEAM_DIR / "诊断_无重绘融合优化_前后对比.jpg"


def normalized_face_boxes(
    faces: list[tuple[int, int, int, int]],
) -> tuple[list[tuple[int, int, int, int]], list[float]]:
    result: list[tuple[int, int, int, int]] = []
    scales: list[float] = []
    start = 0
    for count in base.ROW_COUNTS:
        row = faces[start : start + count]
        median = float(np.median([w for _, _, w, _ in row]))
        for x, y, w, h in row:
            # Pull only the outliers toward their row median. The clamp guarantees that
            # no identity crop is enlarged or reduced by more than eight percent.
            desired = 0.42 * w + 0.58 * median
            scale = float(np.clip(desired / w, 0.92, 1.08))
            new_w = max(1, round(w * scale))
            new_h = max(1, round(h * scale))
            center_x = x + w / 2
            chin_y = y + h
            new_x = round(center_x - new_w / 2)
            new_y = round(chin_y - new_h)
            result.append((new_x, new_y, new_w, new_h))
            scales.append(scale)
        start += count
    return result, scales


def inner_face_mask(
    image_size: tuple[int, int],
    face: tuple[int, int, int, int],
    blur: float = 0,
) -> Image.Image:
    x, y, w, h = face
    mask = Image.new("L", image_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (
            x + round(0.10 * w),
            y + round(0.08 * h),
            x + round(0.90 * w),
            y + round(0.96 * h),
        ),
        fill=255,
    )
    # Include only the central neck band, leaving hair, clothing, and background intact.
    draw.polygon(
        [
            (x + round(0.35 * w), y + round(0.78 * h)),
            (x + round(0.65 * w), y + round(0.78 * h)),
            (x + round(0.68 * w), y + round(1.25 * h)),
            (x + round(0.32 * w), y + round(1.25 * h)),
        ],
        fill=255,
    )
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def median_lab(
    rgb: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    pixels = lab[mask > 160]
    if len(pixels) < 100:
        raise RuntimeError("Not enough face pixels for local colour matching")
    return np.median(pixels, axis=0).astype(np.float32)


def match_skin_colour(
    head: Image.Image,
    local_face: tuple[int, int, int, int],
    reference: Image.Image,
    reference_face: tuple[int, int, int, int],
    strength: float = 0.78,
    luminance_limit: float = 20,
    chroma_limit: float = 9,
) -> tuple[Image.Image, float, float]:
    head = head.convert("RGBA")
    head_rgb = np.asarray(head.convert("RGB"), dtype=np.uint8)
    head_alpha = np.asarray(head.getchannel("A"), dtype=np.uint8)
    source_mask_img = inner_face_mask(head.size, local_face)
    source_mask = np.minimum(np.asarray(source_mask_img), head_alpha)

    ref_rgb = np.asarray(reference.convert("RGB"), dtype=np.uint8)
    ref_mask = np.asarray(inner_face_mask(reference.size, reference_face))

    source_median = median_lab(head_rgb, source_mask)
    target_median = median_lab(ref_rgb, ref_mask)
    before_delta = float(np.linalg.norm(source_median - target_median))

    # Match only local skin colour. Limit channel movement to preserve real texture
    # and prevent the operation from behaving like a synthetic face filter.
    delta = np.clip(
        target_median - source_median,
        (-luminance_limit, -chroma_limit, -chroma_limit),
        (luminance_limit, chroma_limit, chroma_limit),
    )
    delta *= strength

    lab = cv2.cvtColor(head_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    soft_mask = np.asarray(inner_face_mask(head.size, local_face, blur=5.0), dtype=np.float32)
    soft_mask *= head_alpha.astype(np.float32) / 255.0
    weight = (soft_mask / 255.0)[..., None]
    lab = np.clip(lab + weight * delta[None, None, :], 0, 255).astype(np.uint8)
    adjusted_rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    adjusted = Image.fromarray(adjusted_rgb, "RGB").convert("RGBA")
    adjusted.putalpha(head.getchannel("A"))

    adjusted_median = median_lab(adjusted_rgb, source_mask)
    after_delta = float(np.linalg.norm(adjusted_median - target_median))
    return adjusted, before_delta, after_delta


def restore_without_redrawing() -> tuple[Image.Image, list[float], list[float], list[float]]:
    reference = Image.open(base.SOURCE_GROUP).convert("RGBA")
    original_faces = base.detect_group_faces(base.SOURCE_GROUP)
    target_faces, scales = normalized_face_boxes(original_faces)
    result = reference.copy()
    before_deltas: list[float] = []
    after_deltas: list[float] = []

    for index, (player, reference_face, target_face) in enumerate(
        zip(base.PLAYERS, original_faces, target_faces, strict=True)
    ):
        source = Image.open(player.path).convert("RGBA")
        source.putalpha(base.alpha_for_player(player, source))
        detected_source_face = base.detect_source_face(player.path)
        source_box = base.expanded_head_box(detected_source_face, source.size)
        target_box = base.expanded_head_box(target_face, result.size)

        head = source.crop(source_box)
        target_size = (target_box[2] - target_box[0], target_box[3] - target_box[1])
        head = head.resize(target_size, Image.Resampling.LANCZOS)

        local_face = (
            target_face[0] - target_box[0],
            target_face[1] - target_box[1],
            target_face[2],
            target_face[3],
        )
        head, before, after = match_skin_colour(
            head,
            local_face,
            reference,
            reference_face,
        )
        before_deltas.append(before)
        after_deltas.append(after)

        row = base.row_for_index(index)
        head.putalpha(base.soften_head_alpha(head.getchannel("A"), row))
        result.alpha_composite(head, (target_box[0], target_box[1]))

    return result, scales, before_deltas, after_deltas


def make_comparison(before: Image.Image, after: Image.Image) -> None:
    before_small = before.resize((960, 540), Image.Resampling.LANCZOS).convert("RGB")
    after_small = after.resize((960, 540), Image.Resampling.LANCZOS).convert("RGB")
    canvas = Image.new("RGB", (1920, 540), (0, 0, 0))
    canvas.paste(before_small, (0, 0))
    canvas.paste(after_small, (960, 0))
    canvas.save(OUT_COMPARE, format="JPEG", quality=94, optimize=True)


def verify(
    reference: Image.Image,
    result: Image.Image,
    scales: list[float],
    before_deltas: list[float],
    after_deltas: list[float],
) -> None:
    assert result.size == (3840, 2160)
    assert len(scales) == len(before_deltas) == len(after_deltas) == 33
    assert min(scales) >= 0.92 and max(scales) <= 1.08
    assert float(np.mean(after_deltas)) < float(np.mean(before_deltas))

    faces = base.detect_group_faces(base.SOURCE_GROUP)
    allowed = np.zeros((reference.height, reference.width), dtype=bool)
    normalized, _ = normalized_face_boxes(faces)
    for face in normalized:
        left, top, right, bottom = base.expanded_head_box(face, reference.size)
        allowed[top:bottom, left:right] = True
    before = np.asarray(reference.convert("RGB"))
    after = np.asarray(result.convert("RGB"))
    changed = np.max(np.abs(after.astype(np.int16) - before.astype(np.int16)), axis=2) > 0
    assert not np.any(changed[~allowed])


def main() -> None:
    reference = Image.open(base.SOURCE_GROUP).convert("RGBA")
    prior = Image.open(base.OUTPUT_4K).convert("RGBA")
    result, scales, before_deltas, after_deltas = restore_without_redrawing()
    verify(reference, result, scales, before_deltas, after_deltas)

    result.convert("RGB").save(OUT, format="PNG", optimize=True)
    result.resize((1672, 941), Image.Resampling.LANCZOS).convert("RGB").save(
        OUT_NATIVE, format="PNG", optimize=True
    )
    result.resize((1920, 1080), Image.Resampling.LANCZOS).convert("RGB").save(
        OUT_PREVIEW, format="JPEG", quality=94, optimize=True, progressive=True
    )
    make_comparison(prior, result)

    print("method=non-generative source-pixel compositing")
    print(f"players={len(base.PLAYERS)} rows={base.ROW_COUNTS}")
    print(f"head_scale_range={min(scales):.3f}..{max(scales):.3f}")
    print(f"skin_delta_mean={np.mean(before_deltas):.2f}->{np.mean(after_deltas):.2f}")
    print(f"skin_delta_max={np.max(before_deltas):.2f}->{np.max(after_deltas):.2f}")
    print(f"saved={OUT}")
    print(f"saved={OUT_NATIVE}")
    print(f"saved={OUT_PREVIEW}")
    print(f"comparison={OUT_COMPARE}")


if __name__ == "__main__":
    main()
