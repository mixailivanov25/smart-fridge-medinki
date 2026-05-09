import base64
import io
import json
from datetime import date
from typing import Optional, Dict, Any

from PIL import Image


def image_file_to_data_url(uploaded_file, max_size=(1200, 1200), quality=85) -> Optional[str]:
    """
    Превращает изображение из st.file_uploader / st.camera_input в data URL.
    Храним компактно: JPEG base64.
    """
    if uploaded_file is None:
        return None

    raw = uploaded_file.getvalue()
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.thumbnail(max_size)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)

    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def normalize_ai_product_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Аккуратно нормализуем ответ AI, чтобы не ломать форму.
    """
    if not isinstance(data, dict):
        data = {}

    def get_str(key, default=""):
        value = data.get(key, default)
        if value is None:
            return default
        return str(value).strip()

    def get_float(key, default=0.0):
        try:
            return float(data.get(key, default) or default)
        except Exception:
            return default

    return {
        "name": get_str("name", "Новый продукт"),
        "category": get_str("category", "Другое"),
        "quantity": get_float("quantity", 1.0),
        "unit": get_str("unit", "шт"),
        "calories_per_100g": get_float("calories_per_100g", 0.0),
        "expiration_date": get_str("expiration_date", ""),
        "description": get_str("description", ""),
        "confidence": get_float("confidence", 0.0),
    }


def recognize_product_with_openai(image_data_url: str, api_key: str) -> Dict[str, Any]:
    """
    Распознаёт продукт по фото через OpenAI Vision.
    Если OPENAI_API_KEY не задан — эта функция не используется.
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    prompt = """
Ты помощник семейного приложения 'Умный холодильник Мединки'.

По фотографии продукта попробуй определить:
- название продукта на русском;
- категорию;
- количество или вес, если видно;
- единицу измерения: г, кг, мл, л, шт;
- калории на 100 г, если это можно предположить;
- срок годности в формате YYYY-MM-DD, если он явно виден;
- короткое описание;
- confidence от 0 до 1.

Если точных данных нет — ставь разумную оценку, но не выдумывай дату срока годности.
Если срок годности не виден, expiration_date должен быть пустой строкой.

Ответ строго JSON:
{
  "name": "...",
  "category": "...",
  "quantity": 1,
  "unit": "шт",
  "calories_per_100g": 0,
  "expiration_date": "",
  "description": "...",
  "confidence": 0.0
}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "Ты аккуратный AI-сканер продуктов. Отвечай только валидным JSON.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        },
                    },
                ],
            },
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content
    parsed = json.loads(raw)
    return normalize_ai_product_result(parsed)
