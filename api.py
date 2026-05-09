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


def edit_image(api_key: str, image_path: str, prompt: str) -> bytes:
    client = openai.OpenAI(api_key=api_key)
    png_bytes = _to_rgba_png(image_path)

    import base64
    response = client.images.edit(
        model="gpt-image-2",
        image=("image.png", png_bytes, "image/png"),
        prompt=prompt,
        n=1,
        size="1024x1024",
    )

    return base64.b64decode(response.data[0].b64_json)


def save_result(image_bytes: bytes, dest_folder: str, original_name: str):
    os.makedirs(dest_folder, exist_ok=True)
    base = os.path.splitext(original_name)[0]
    out_path = os.path.join(dest_folder, f"{base}_edited.png")
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    return out_path
