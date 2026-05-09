import io
import os
import openai
from PIL import Image


def _to_rgba_png(image_path: str) -> bytes:
    with Image.open(image_path) as img:
        size = min(img.width, img.height)
        left = (img.width - size) // 2
        top = (img.height - size) // 2
        img = img.crop((left, top, left + size, top + size))
        img = img.resize((1024, 1024), Image.LANCZOS)
        img = img.convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


def edit_image(api_key: str, image_path: str, prompt: str, model: str = "gpt-image-2") -> bytes:
    client = openai.OpenAI(api_key=api_key)
    png_bytes = _to_rgba_png(image_path)

    import base64
    response = client.images.edit(
        model=model,
        image=("image.png", png_bytes, "image/png"),
        prompt=prompt,
        n=1,
        size="1024x1024",
    )

    return base64.b64decode(response.data[0].b64_json)


FORMAT_MAP = {
    "PNG": ("png", "PNG"),
    "JPEG": ("jpg", "JPEG"),
    "WEBP": ("webp", "WEBP"),
}


def save_result(image_bytes: bytes, dest_folder: str, original_name: str, fmt: str = "PNG"):
    os.makedirs(dest_folder, exist_ok=True)
    base = os.path.splitext(original_name)[0]
    ext, pil_fmt = FORMAT_MAP.get(fmt, ("png", "PNG"))
    out_path = os.path.join(dest_folder, f"{base}_edited.{ext}")

    with Image.open(io.BytesIO(image_bytes)) as img:
        if pil_fmt == "JPEG":
            img = img.convert("RGB")
        img.save(out_path, format=pil_fmt)

    return out_path
