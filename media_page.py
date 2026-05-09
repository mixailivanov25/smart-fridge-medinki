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
