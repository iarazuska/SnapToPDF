from PIL import Image
import os


def convert_to_pdf(image_paths, output_path):
    if not image_paths:
        return False, "No hay imágenes para convertir"

    images = []
    try:
        for path in image_paths:
            img = Image.open(path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)

        first, rest = images[0], images[1:]
        first.save(output_path, format="PDF", save_all=True, append_images=rest)
        return True, None
    except Exception as e:
        return False, str(e)


def get_image_info(path):
    try:
        with Image.open(path) as img:
            width, height = img.size
            size_bytes = os.path.getsize(path)
            return {
                "width": width,
                "height": height,
                "size": format_size(size_bytes),
                "format": img.format
            }
    except Exception:
        return None


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / 1024**2:.1f} MB"


SUPPORTED_FORMATS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff")


def is_image(path):
    return path.lower().endswith(SUPPORTED_FORMATS)