from pathlib import Path
import re
import shutil
from datetime import datetime

ROOT = Path(__file__).parent.resolve()


def backup_file(path: Path):
    if not path.exists():
        return
    backup_dir = ROOT / "backups" / f"backup_v13_photo_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_dir / path.name)


def ensure_requirement(package_name: str):
    req = ROOT / "requirements.txt"
    if not req.exists():
        req.write_text("", encoding="utf-8")

    text = req.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    normalized = [line.split("==")[0].split(">=")[0].lower() for line in lines]

    if package_name.lower() not in normalized:
        lines.append(package_name)
        req.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_media_utils():
    path = ROOT / "media_utils.py"
    backup_file(path)

    path.write_text(
        r'''
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
'''.strip()
        + "\n",
        encoding="utf-8",
    )


def write_media_schema():
    path = ROOT / "media_schema.py"
    backup_file(path)

    path.write_text(
        r'''
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

import streamlit as st
from sqlalchemy import create_engine, text


_ENGINE = None


def _get_secret(name: str, default=None):
    try:
        if hasattr(st, "secrets") and name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


def get_media_engine():
    """
    Подключение к той же базе, что и приложение.
    В облаке берём DATABASE_URL из Streamlit Secrets.
    Локально, если DATABASE_URL нет, используем SQLite.
    """
    global _ENGINE

    if _ENGINE is not None:
        return _ENGINE

    database_url = _get_secret("DATABASE_URL")

    if not database_url:
        database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        # Локальный fallback. Если в основном проекте используется другое имя SQLite,
        # это влияет только на новый медиа-раздел.
        database_url = "sqlite:///smart_fridge.db"

    _ENGINE = create_engine(database_url, pool_pre_ping=True)
    return _ENGINE


def _is_postgres(engine) -> bool:
    return engine.dialect.name.startswith("postgres")


def ensure_media_schema():
    """
    Создаёт таблицу медиа-материалов и пытается добавить image_data
    к основным таблицам, если они существуют.
    """
    engine = get_media_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS app_media_assets (
                entity_type VARCHAR(64) NOT NULL,
                entity_name VARCHAR(255) NOT NULL,
                image_data TEXT,
                mime VARCHAR(64) DEFAULT 'image/jpeg',
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (entity_type, entity_name)
            )
        """))

        if _is_postgres(engine):
            optional_alters = [
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS image_data TEXT",
                "ALTER TABLE products ADD COLUMN IF NOT EXISTS image_comment TEXT",
                "ALTER TABLE custom_recipes ADD COLUMN IF NOT EXISTS image_data TEXT",
                "ALTER TABLE custom_recipes ADD COLUMN IF NOT EXISTS image_comment TEXT",
            ]
            for sql in optional_alters:
                try:
                    conn.execute(text(sql))
                except Exception:
                    # Таблицы может ещё не быть — не критично.
                    pass
        else:
            # SQLite не поддерживает ADD COLUMN IF NOT EXISTS во всех версиях.
            for table_name in ["products", "custom_recipes"]:
                try:
                    cols = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                    col_names = {row[1] for row in cols}
                    if "image_data" not in col_names:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN image_data TEXT"))
                    if "image_comment" not in col_names:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN image_comment TEXT"))
                except Exception:
                    pass


def save_media_asset(entity_type: str, entity_name: str, image_data: str, comment: str = ""):
    ensure_media_schema()
    engine = get_media_engine()

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO app_media_assets
                    (entity_type, entity_name, image_data, comment, updated_at)
                VALUES
                    (:entity_type, :entity_name, :image_data, :comment, CURRENT_TIMESTAMP)
                ON CONFLICT (entity_type, entity_name)
                DO UPDATE SET
                    image_data = excluded.image_data,
                    comment = excluded.comment,
                    updated_at = CURRENT_TIMESTAMP
            """),
            {
                "entity_type": entity_type,
                "entity_name": entity_name,
                "image_data": image_data,
                "comment": comment,
            },
        )


def load_media_assets(entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_media_schema()
    engine = get_media_engine()

    with engine.begin() as conn:
        if entity_type:
            rows = conn.execute(
                text("""
                    SELECT entity_type, entity_name, image_data, comment, updated_at
                    FROM app_media_assets
                    WHERE entity_type = :entity_type
                    ORDER BY updated_at DESC
                """),
                {"entity_type": entity_type},
            ).mappings().all()
        else:
            rows = conn.execute(
                text("""
                    SELECT entity_type, entity_name, image_data, comment, updated_at
                    FROM app_media_assets
                    ORDER BY updated_at DESC
                """)
            ).mappings().all()

    return [dict(row) for row in rows]


def insert_product_from_scan(
    name: str,
    quantity: float,
    unit: str,
    calories_per_100g: float,
    category: str,
    expiration_date,
    image_data: Optional[str] = None,
):
    """
    Добавляет распознанный продукт в таблицу products.
    Ожидаем стандартную структуру проекта:
    name, quantity, unit, calories_per_100g, category, expiration_date, created_at.
    """
    ensure_media_schema()
    engine = get_media_engine()

    exp_value = None
    if expiration_date:
        exp_value = str(expiration_date)

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO products
                    (name, quantity, unit, calories_per_100g, category, expiration_date, created_at, image_data)
                VALUES
                    (:name, :quantity, :unit, :calories_per_100g, :category, :expiration_date, CURRENT_TIMESTAMP, :image_data)
            """),
            {
                "name": name,
                "quantity": quantity,
                "unit": unit,
                "calories_per_100g": calories_per_100g,
                "category": category,
                "expiration_date": exp_value,
                "image_data": image_data,
            },
        )


def get_optional_openai_key():
    return _get_secret("OPENAI_API_KEY", "")
'''.strip()
        + "\n",
        encoding="utf-8",
    )


def write_media_page():
    path = ROOT / "media_page.py"
    backup_file(path)

    path.write_text(
        r'''
from datetime import date, timedelta, datetime

import streamlit as st

from media_utils import image_file_to_data_url, recognize_product_with_openai, normalize_ai_product_result
from media_schema import (
    ensure_media_schema,
    save_media_asset,
    load_media_assets,
    insert_product_from_scan,
    get_optional_openai_key,
)


def apply_photo_design_css():
    st.markdown(
        """
<style>
:root {
    --medinki-bg-1: #fff7ed;
    --medinki-bg-2: #fdf2f8;
    --medinki-card: rgba(255,255,255,0.78);
    --medinki-border: rgba(255,255,255,0.9);
    --medinki-shadow: 0 14px 34px rgba(15,23,42,0.12);
    --medinki-pink: #ec4899;
    --medinki-orange: #f97316;
    --medinki-green: #22c55e;
}

.medinki-hero {
    padding: 22px 22px;
    border-radius: 28px;
    background:
        radial-gradient(circle at top left, rgba(251,146,60,0.35), transparent 34%),
        radial-gradient(circle at bottom right, rgba(236,72,153,0.32), transparent 36%),
        linear-gradient(135deg, #fff7ed 0%, #fdf2f8 100%);
    box-shadow: var(--medinki-shadow);
    border: 1px solid rgba(255,255,255,0.9);
    margin-bottom: 18px;
    animation: medinkiFadeUp .45s ease-out both;
}

.medinki-hero h1 {
    margin: 0;
    font-size: 2.0rem;
    line-height: 1.1;
}

.medinki-hero p {
    margin: 10px 0 0 0;
    color: #475569;
    font-size: 1.02rem;
}

.medinki-card {
    padding: 18px;
    border-radius: 24px;
    background: var(--medinki-card);
    border: 1px solid var(--medinki-border);
    box-shadow: 0 10px 26px rgba(15,23,42,0.08);
    backdrop-filter: blur(10px);
    margin-bottom: 14px;
    transition: transform .18s ease, box-shadow .18s ease;
    animation: medinkiFadeUp .5s ease-out both;
}

.medinki-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 36px rgba(15,23,42,0.13);
}

.medinki-badge {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(236,72,153,0.10);
    color: #be185d;
    font-weight: 700;
    font-size: .86rem;
    margin: 3px 5px 3px 0;
}

.medinki-pulse {
    display: inline-block;
    animation: medinkiPulse 1.8s infinite;
}

@keyframes medinkiFadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes medinkiPulse {
    0% {
        transform: scale(1);
        filter: drop-shadow(0 0 0 rgba(236,72,153,0.0));
    }
    50% {
        transform: scale(1.05);
        filter: drop-shadow(0 0 10px rgba(236,72,153,0.25));
    }
    100% {
        transform: scale(1);
        filter: drop-shadow(0 0 0 rgba(236,72,153,0.0));
    }
}

div.stButton > button {
    border-radius: 999px !important;
    border: 0 !important;
    background: linear-gradient(135deg, #fb923c 0%, #ec4899 100%) !important;
    color: white !important;
    font-weight: 800 !important;
    box-shadow: 0 10px 24px rgba(236,72,153,0.22);
    transition: transform .16s ease, box-shadow .16s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px) scale(1.01);
    box-shadow: 0 14px 30px rgba(236,72,153,0.28);
}

@media (max-width: 720px) {
    .medinki-hero {
        padding: 18px;
        border-radius: 22px;
    }

    .medinki-hero h1 {
        font-size: 1.55rem;
    }

    .medinki-card {
        padding: 15px;
        border-radius: 20px;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
<div class="medinki-hero">
    <h1><span class="medinki-pulse">📸</span> Фото и сканер продуктов</h1>
    <p>
        Фотографируй продукты с телефона, добавляй картинки блюдам и постепенно превращай
        холодильник Мединки в красивое семейное приложение.
    </p>
    <div style="margin-top:12px;">
        <span class="medinki-badge">камера телефона</span>
        <span class="medinki-badge">фото продуктов</span>
        <span class="medinki-badge">фото рецептов</span>
        <span class="medinki-badge">AI-распознавание</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_product_scanner():
    st.markdown('<div class="medinki-card">', unsafe_allow_html=True)
    st.subheader("📷 Сфотографировать продукт")

    st.caption(
        "Можно сделать фото прямо с телефона. Если задан OPENAI_API_KEY, приложение попробует "
        "само определить название, категорию, количество, калории и срок годности."
    )

    source = st.radio(
        "Источник фото",
        ["Камера", "Загрузить файл"],
        horizontal=True,
        key="photo_source_v13",
    )

    uploaded = None
    if source == "Камера":
        uploaded = st.camera_input("Сделать фото продукта", key="camera_product_v13")
    else:
        uploaded = st.file_uploader(
            "Загрузить фото продукта",
            type=["png", "jpg", "jpeg", "webp"],
            key="upload_product_v13",
        )

    image_data = None
    if uploaded is not None:
        image_data = image_file_to_data_url(uploaded)
        st.image(image_data, caption="Фото продукта", use_container_width=True)

        col_ai, col_reset = st.columns(2)

        with col_ai:
            if st.button("✨ Распознать продукт", key="recognize_product_v13"):
                api_key = get_optional_openai_key()
                if not api_key:
                    st.warning(
                        "OPENAI_API_KEY не задан. Фото сохранится, но автоматическое распознавание пока недоступно."
                    )
                    st.session_state["scan_ai_result_v13"] = normalize_ai_product_result({})
                else:
                    with st.spinner("Распознаю продукт по фото..."):
                        try:
                            result = recognize_product_with_openai(image_data, api_key)
                            st.session_state["scan_ai_result_v13"] = result
                            st.success("Готово. Проверь данные перед добавлением.")
                        except Exception as e:
                            st.error(f"Не удалось распознать фото: {e}")
                            st.session_state["scan_ai_result_v13"] = normalize_ai_product_result({})

        with col_reset:
            if st.button("🧹 Очистить распознавание", key="clear_ai_scan_v13"):
                st.session_state.pop("scan_ai_result_v13", None)
                st.rerun()

    ai = st.session_state.get("scan_ai_result_v13", normalize_ai_product_result({}))

    st.markdown("### ✅ Подтвердить данные продукта")

    default_exp = date.today() + timedelta(days=7)
    if ai.get("expiration_date"):
        try:
            default_exp = date.fromisoformat(ai["expiration_date"])
        except Exception:
            pass

    with st.form("add_scanned_product_form_v13"):
        name = st.text_input("Название", value=ai.get("name", "Новый продукт"))
        category = st.text_input("Категория", value=ai.get("category", "Другое"))

        c1, c2 = st.columns(2)
        with c1:
            quantity = st.number_input(
                "Количество",
                min_value=0.0,
                value=float(ai.get("quantity", 1.0) or 1.0),
                step=0.1,
            )
        with c2:
            unit = st.selectbox(
                "Единица",
                ["шт", "г", "кг", "мл", "л", "упак.", "банка", "бут."],
                index=0 if ai.get("unit") not in ["г", "кг", "мл", "л", "упак.", "банка", "бут."] else ["шт", "г", "кг", "мл", "л", "упак.", "банка", "бут."].index(ai.get("unit")),
            )

        c3, c4 = st.columns(2)
        with c3:
            calories = st.number_input(
                "Калории на 100 г",
                min_value=0.0,
                value=float(ai.get("calories_per_100g", 0.0) or 0.0),
                step=1.0,
            )
        with c4:
            expiration_date = st.date_input("Срок годности", value=default_exp)

        comment = st.text_area(
            "Комментарий / что распознано",
            value=ai.get("description", ""),
            height=80,
        )

        submitted = st.form_submit_button("🧊 Добавить в холодильник")

    if submitted:
        try:
            insert_product_from_scan(
                name=name,
                quantity=quantity,
                unit=unit,
                calories_per_100g=calories,
                category=category,
                expiration_date=expiration_date,
                image_data=image_data,
            )

            if image_data:
                save_media_asset(
                    entity_type="product",
                    entity_name=name,
                    image_data=image_data,
                    comment=comment,
                )

            st.success(f"Продукт «{name}» добавлен в холодильник ✅")
            st.balloons()
        except Exception as e:
            st.error(f"Не удалось добавить продукт. Ошибка: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_photo_library():
    st.markdown('<div class="medinki-card">', unsafe_allow_html=True)
    st.subheader("🖼️ Добавить фото блюду, рецепту или продукту")

    entity_type_label = st.selectbox(
        "К чему добавить фото?",
        [
            "Блюдо из каталога",
            "Свой рецепт",
            "Продукт из каталога",
            "Продукт в холодильнике",
            "Другое",
        ],
        key="media_entity_type_label_v13",
    )

    entity_type_map = {
        "Блюдо из каталога": "dish",
        "Свой рецепт": "custom_recipe",
        "Продукт из каталога": "catalog_product",
        "Продукт в холодильнике": "product",
        "Другое": "other",
    }

    entity_type = entity_type_map[entity_type_label]

    entity_name = st.text_input(
        "Название",
        placeholder="Например: Борщ, Омлет, Молоко, Куриная грудка...",
        key="media_entity_name_v13",
    )

    uploaded = st.file_uploader(
        "Фото",
        type=["png", "jpg", "jpeg", "webp"],
        key="media_photo_upload_v13",
    )

    image_data = None
    if uploaded is not None:
        image_data = image_file_to_data_url(uploaded)
        st.image(image_data, caption=entity_name or "Новое фото", use_container_width=True)

    comment = st.text_area("Комментарий", height=70, key="media_comment_v13")

    if st.button("💾 Сохранить фото", key="save_media_asset_v13"):
        if not entity_name.strip():
            st.warning("Нужно указать название.")
        elif not image_data:
            st.warning("Нужно загрузить фото.")
        else:
            try:
                save_media_asset(
                    entity_type=entity_type,
                    entity_name=entity_name.strip(),
                    image_data=image_data,
                    comment=comment,
                )
                st.success("Фото сохранено ✅")
            except Exception as e:
                st.error(f"Не удалось сохранить фото: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_gallery():
    st.markdown('<div class="medinki-card">', unsafe_allow_html=True)
    st.subheader("🌈 Галерея Мединки")

    filter_label = st.selectbox(
        "Показать",
        ["Все", "Блюда", "Свои рецепты", "Продукты каталога", "Продукты холодильника", "Другое"],
        key="gallery_filter_v13",
    )

    filter_map = {
        "Все": None,
        "Блюда": "dish",
        "Свои рецепты": "custom_recipe",
        "Продукты каталога": "catalog_product",
        "Продукты холодильника": "product",
        "Другое": "other",
    }

    assets = load_media_assets(filter_map[filter_label])

    if not assets:
        st.info("Пока нет сохранённых фото. Добавь первое фото выше.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    cols = st.columns(2)
    for i, item in enumerate(assets):
        with cols[i % 2]:
            st.markdown(
                f"""
<div style="
    border-radius:22px;
    padding:12px;
    margin-bottom:14px;
    background:linear-gradient(135deg, rgba(255,255,255,.95), rgba(255,247,237,.86));
    box-shadow:0 10px 24px rgba(15,23,42,.08);
    border:1px solid rgba(255,255,255,.9);
">
    <div style="font-weight:900;font-size:1.05rem;margin-bottom:6px;">{item.get("entity_name", "")}</div>
    <div style="font-size:.82rem;color:#64748b;margin-bottom:8px;">{item.get("entity_type", "")}</div>
</div>
""",
                unsafe_allow_html=True,
            )
            if item.get("image_data"):
                st.image(item["image_data"], use_container_width=True)
            if item.get("comment"):
                st.caption(item["comment"])

    st.markdown("</div>", unsafe_allow_html=True)


def render_design_preview():
    st.markdown('<div class="medinki-card">', unsafe_allow_html=True)
    st.subheader("✨ Новый стиль интерфейса")

    st.write(
        "Это первая версия нового визуального языка приложения: мягкие карточки, "
        "тёплые семейные цвета, анимации и более удобный мобильный интерфейс."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
<div class="medinki-card">
    <h3>🧊 Холодильник</h3>
    <p>Карточки продуктов с фото, сроками и быстрыми действиями.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
<div class="medinki-card">
    <h3>🍳 Рецепты</h3>
    <p>Красивые обложки блюд, история, калории и готовка в один клик.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
<div class="medinki-card">
    <h3>📱 Телефон</h3>
    <p>Фото продукта → распознавание → добавление в холодильник.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_media_page():
    ensure_media_schema()
    apply_photo_design_css()
    render_header()

    tabs = st.tabs(
        [
            "📷 Скан продукта",
            "🖼️ Фото блюд и продуктов",
            "🌈 Галерея",
            "✨ Дизайн",
        ]
    )

    with tabs[0]:
        render_product_scanner()

    with tabs[1]:
        render_photo_library()

    with tabs[2]:
        render_gallery()

    with tabs[3]:
        render_design_preview()
'''.strip()
        + "\n",
        encoding="utf-8",
    )


def patch_app_py():
    path = ROOT / "app.py"

    if not path.exists():
        print("app.py не найден. Файлы медиа-раздела созданы, но app.py не пропатчен.")
        return

    backup_file(path)

    text = path.read_text(encoding="utf-8")

    # 1. Добавляем импорт.
    if "from media_page import render_media_page" not in text:
        # Вставляем после import streamlit as st, если есть.
        if re.search(r"^import streamlit as st\s*$", text, flags=re.MULTILINE):
            text = re.sub(
                r"^import streamlit as st\s*$",
                "import streamlit as st\nfrom media_page import render_media_page",
                text,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            text = "from media_page import render_media_page\n" + text

    # 2. Добавляем пункт меню рядом с быстрым экраном.
    # Пытаемся аккуратно вставить в список страниц.
    menu_variants = [
        '"📱 Быстрый экран"',
        "'📱 Быстрый экран'",
        '"Быстрый экран"',
        "'Быстрый экран'",
    ]

    if "📸 Фото и сканер" not in text:
        inserted = False
        for variant in menu_variants:
            if variant in text:
                replacement = variant + ',\n        "📸 Фото и сканер"'
                text = text.replace(variant, replacement, 1)
                inserted = True
                break

        if not inserted:
            print("Не удалось автоматически добавить пункт меню. Добавь вручную: 📸 Фото и сканер")

    # 3. Добавляем обработчик страницы.
    if "render_media_page()" not in text:
        route_inserted = False

        # Частый вариант:
        # if page == "Быстрый экран":
        #     ...
        # elif page == "Главная":
        pattern = r'(\nelif\s+page\s*==\s*[\'"]Главная[\'"]\s*:)'
        if re.search(pattern, text):
            text = re.sub(
                pattern,
                '\nelif page in ("📸 Фото и сканер", "Фото и сканер"):\n    render_media_page()\n\\1',
                text,
                count=1,
            )
            route_inserted = True

        # Если есть эмодзи у Главной.
        if not route_inserted:
            pattern = r'(\nelif\s+page\s*==\s*[\'"]🏠 Главная[\'"]\s*:)'
            if re.search(pattern, text):
                text = re.sub(
                    pattern,
                    '\nelif page in ("📸 Фото и сканер", "Фото и сканер"):\n    render_media_page()\n\\1',
                    text,
                    count=1,
                )
                route_inserted = True

        # Если вообще не нашли, пробуем перед Демо-режимом.
        if not route_inserted:
            pattern = r'(\nelif\s+page\s*==\s*[\'"]🧪 Демо-режим[\'"]\s*:)'
            if re.search(pattern, text):
                text = re.sub(
                    pattern,
                    '\nelif page in ("📸 Фото и сканер", "Фото и сканер"):\n    render_media_page()\n\\1',
                    text,
                    count=1,
                )
                route_inserted = True

        if not route_inserted:
            print(
                "Не удалось автоматически добавить обработчик страницы. "
                "Нужно добавить в роутинг app.py:\n"
                'elif page in ("📸 Фото и сканер", "Фото и сканер"):\n'
                "    render_media_page()"
            )

    path.write_text(text, encoding="utf-8")


def main():
    print("=== upgrade_to_v13_photo_design.py ===")
    print("Добавляем фото, сканер продуктов и новый визуальный раздел...")

    ensure_requirement("Pillow")
    ensure_requirement("openai")

    write_media_utils()
    write_media_schema()
    write_media_page()
    patch_app_py()

    print()
    print("Готово ✅")
    print()
    print("Что добавлено:")
    print("- media_utils.py")
    print("- media_schema.py")
    print("- media_page.py")
    print("- новый раздел: 📸 Фото и сканер")
    print("- зависимости: Pillow, openai")
    print()
    print("Дальше запусти:")
    print("python -m pip install -r requirements.txt")
    print("python -m streamlit run app.py")
    print()
    print("Для AI-распознавания добавь в Streamlit Secrets:")
    print('OPENAI_API_KEY = "..."')
    print()
    print("Если без OPENAI_API_KEY — фото и ручное добавление продукта всё равно работают.")


if __name__ == "__main__":
    main()