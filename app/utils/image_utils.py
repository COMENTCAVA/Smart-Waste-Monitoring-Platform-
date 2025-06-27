import pillow_heif
pillow_heif.register_heif_opener()
from PIL import Image as PILImage

def compress_image(path: str, quality: int = 85) -> None:
    with PILImage.open(path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(path, optimize=True, quality=quality)