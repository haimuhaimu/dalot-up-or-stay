from pathlib import Path

from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PHOTO_DIR = ROOT / "output" / "team_photo" / "real_family_photo"
SOURCE = PHOTO_DIR / "北京景从_2025真人全家福_33人_最终版.png"
COMPACT = PHOTO_DIR / "北京景从_2025真人全家福_紧凑版_缺16_中间稿.png"
OUTPUT = PHOTO_DIR / "北京景从_2025真人全家福_33人_紧凑修正版.png"
OUTPUT_4K = PHOTO_DIR / "北京景从_2025真人全家福_33人_紧凑修正版_4K.png"
PREVIEW = PHOTO_DIR / "北京景从_2025真人全家福_33人_紧凑修正版_4K预览.jpg"

# The generative compaction pass removed seated number 16 but left the correct
# compact slot in front of number 39. Restore that local source region from the
# verified 33-person original. It contains number 16, his chair, and number 39
# immediately behind him; keeping both together preserves natural occlusion.
PATCH_BOX = (1360, 300, 1625, 850)
FEATHER = 24


def feather_mask(size: tuple[int, int], feather: int) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    inner = Image.new("L", (width - feather * 2, height - feather * 2), 255)
    mask.paste(inner, (feather, feather))
    return mask.filter(ImageFilter.GaussianBlur(feather / 2))


def main() -> None:
    assert SOURCE.exists() and COMPACT.exists()
    source = Image.open(SOURCE).convert("RGB")
    compact = Image.open(COMPACT).convert("RGB")
    assert source.size == compact.size == (1672, 941)

    patch = source.crop(PATCH_BOX)
    mask = feather_mask(patch.size, FEATHER)
    compact.paste(patch, PATCH_BOX[:2], mask)
    compact.save(OUTPUT, format="PNG", optimize=True)

    high = compact.resize((3840, 2160), Image.Resampling.LANCZOS)
    high = high.filter(ImageFilter.UnsharpMask(radius=1.2, percent=75, threshold=3))
    high.save(OUTPUT_4K, format="PNG", optimize=True)
    high.save(PREVIEW, format="JPEG", quality=93, optimize=True, progressive=True)

    assert OUTPUT.stat().st_size > 1_000_000
    assert OUTPUT_4K.stat().st_size > 5_000_000
    assert PREVIEW.stat().st_size > 500_000
    print(OUTPUT)
    print(OUTPUT_4K)
    print(PREVIEW)


if __name__ == "__main__":
    main()
