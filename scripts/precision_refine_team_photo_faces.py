from __future__ import annotations

from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import restore_team_photo_faces as base
import refine_team_photo_faces_nongenerative as refined


OUT = base.TEAM_DIR / "北京景从_2025真人全家福_33人_逐人精修版_4K.png"
OUT_NATIVE = base.TEAM_DIR / "北京景从_2025真人全家福_33人_逐人精修版.png"
OUT_PREVIEW = base.TEAM_DIR / "北京景从_2025真人全家福_33人_逐人精修版_预览.jpg"

# Manual, identity-safe refinements derived from the head-and-shoulder review grid.
# Values affect only the pasted portrait crop; no face pixels are synthesized.
PERSON_SCALE = {
    "23": 1.03,
    "2": 1.03,
    "6": 1.04,
    "20": 1.02,
    "4": 0.97,
    "30": 1.05,
    "21": 0.96,
    "28": 1.03,
    "17": 0.94,
    "39": 0.95,
    "8": 0.95,
    "1": 0.92,
    "99": 1.05,
    "86": 1.05,
    "13": 0.97,
    "29": 0.95,
    "16": 0.93,
}

COLOUR_STRENGTH = {
    "16": (1.00, 30, 13),
    "6": (0.92, 24, 10),
    "20": (0.88, 24, 10),
    "25": (0.88, 24, 10),
    "27": (0.86, 22, 10),
}


def personalized_face_boxes(
    faces: list[tuple[int, int, int, int]],
) -> tuple[list[tuple[int, int, int, int]], list[float]]:
    normalized, normalized_scales = refined.normalized_face_boxes(faces)
    result: list[tuple[int, int, int, int]] = []
    final_scales: list[float] = []
    for player, face, row_scale in zip(
        base.PLAYERS, normalized, normalized_scales, strict=True
    ):
        x, y, w, h = face
        manual = PERSON_SCALE.get(player.number, 1.0)
        new_w = max(1, round(w * manual))
        new_h = max(1, round(h * manual))
        center_x = x + w / 2
        chin_y = y + h
        result.append(
            (
                round(center_x - new_w / 2),
                round(chin_y - new_h),
                new_w,
                new_h,
            )
        )
        final_scales.append(row_scale * manual)
    return result, final_scales


def add_contact_shadow(
    canvas: Image.Image,
    face: tuple[int, int, int, int],
    head_box: tuple[int, int, int, int],
) -> None:
    x, y, w, h = face
    left, top, right, bottom = head_box
    local = Image.new("L", (right - left, bottom - top), 0)
    draw = ImageDraw.Draw(local)
    draw.ellipse(
        (
            x - left + round(0.23 * w),
            y - top + round(0.82 * h),
            x - left + round(0.77 * w),
            y - top + round(1.22 * h),
        ),
        fill=28,
    )
    local = local.filter(ImageFilter.GaussianBlur(8))
    shadow = Image.new("RGBA", local.size, (0, 0, 0, 0))
    shadow.putalpha(local)
    canvas.alpha_composite(shadow, (left, top))


def build() -> tuple[Image.Image, list[float], list[float], list[float]]:
    reference = Image.open(base.SOURCE_GROUP).convert("RGBA")
    original_faces = base.detect_group_faces(base.SOURCE_GROUP)
    target_faces, scales = personalized_face_boxes(original_faces)
    result = reference.copy()
    before_deltas: list[float] = []
    after_deltas: list[float] = []

    for index, (player, reference_face, target_face) in enumerate(
        zip(base.PLAYERS, original_faces, target_faces, strict=True)
    ):
        source = Image.open(player.path).convert("RGBA")
        source.putalpha(base.alpha_for_player(player, source))
        source_face = base.detect_source_face(player.path)
        source_box = base.expanded_head_box(source_face, source.size)
        target_box = base.expanded_head_box(target_face, result.size)
        head = source.crop(source_box).resize(
            (target_box[2] - target_box[0], target_box[3] - target_box[1]),
            Image.Resampling.LANCZOS,
        )
        local_face = (
            target_face[0] - target_box[0],
            target_face[1] - target_box[1],
            target_face[2],
            target_face[3],
        )
        strength, luminance, chroma = COLOUR_STRENGTH.get(
            player.number, (0.82, 22, 10)
        )
        head, before, after = refined.match_skin_colour(
            head,
            local_face,
            reference,
            reference_face,
            strength=strength,
            luminance_limit=luminance,
            chroma_limit=chroma,
        )
        before_deltas.append(before)
        after_deltas.append(after)

        add_contact_shadow(result, target_face, target_box)
        row = base.row_for_index(index)
        head.putalpha(base.soften_head_alpha(head.getchannel("A"), row))
        result.alpha_composite(head, (target_box[0], target_box[1]))

    return result, scales, before_deltas, after_deltas


def verify(
    reference: Image.Image,
    result: Image.Image,
    scales: list[float],
    before_deltas: list[float],
    after_deltas: list[float],
) -> None:
    assert result.size == (3840, 2160)
    assert len(scales) == len(before_deltas) == len(after_deltas) == 33
    assert min(scales) >= 0.87 and max(scales) <= 1.15
    assert float(np.mean(after_deltas)) < float(np.mean(before_deltas))

    faces = base.detect_group_faces(base.SOURCE_GROUP)
    targets, _ = personalized_face_boxes(faces)
    allowed = np.zeros((reference.height, reference.width), dtype=bool)
    for face in targets:
        left, top, right, bottom = base.expanded_head_box(face, reference.size)
        allowed[top:bottom, left:right] = True
    original = np.asarray(reference.convert("RGB"), dtype=np.int16)
    edited = np.asarray(result.convert("RGB"), dtype=np.int16)
    changed = np.max(np.abs(edited - original), axis=2) > 0
    assert not np.any(changed[~allowed])


def main() -> None:
    reference = Image.open(base.SOURCE_GROUP).convert("RGBA")
    result, scales, before, after = build()
    verify(reference, result, scales, before, after)
    result.convert("RGB").save(OUT, format="PNG", optimize=True)
    result.resize((1672, 941), Image.Resampling.LANCZOS).convert("RGB").save(
        OUT_NATIVE, format="PNG", optimize=True
    )
    result.resize((1920, 1080), Image.Resampling.LANCZOS).convert("RGB").save(
        OUT_PREVIEW, format="JPEG", quality=94, optimize=True, progressive=True
    )
    print("method=per-player non-generative pixel refinement")
    print(f"manual_players={len(PERSON_SCALE)} of {len(base.PLAYERS)}")
    print(f"scale_range={min(scales):.3f}..{max(scales):.3f}")
    print(f"skin_delta_mean={np.mean(before):.2f}->{np.mean(after):.2f}")
    print(f"skin_delta_max={np.max(before):.2f}->{np.max(after):.2f}")
    print(f"saved={OUT}")


if __name__ == "__main__":
    main()
