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
