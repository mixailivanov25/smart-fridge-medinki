from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
MODERN_UI = ROOT / "modern_ui_v13.py"


MODERN_UI_CODE = r'''
import streamlit as st
import streamlit.components.v1 as components


def modern_go(target_page: str):
    aliases = {
        "Быстрый экран": "📱 Быстрый экран",
        "Главная": "🏠 Главная",
        "Семейный режим": "👨‍👩‍👧 Семейный режим",
        "Сегодня": "📅 Сегодня",
        "Дневник питания": "📔 Дневник питания",
        "Добавить еду": "📔 Дневник питания",
        "Умные покупки": "🛒 Умные покупки",
        "Добавить покупку": "🛒 Умные покупки",
        "Аналитика": "📊 Аналитика",
        "Мои рецепты": "📝 Мои рецепты",
        "Мой холодильник": "🧊 Мой холодильник",
        "Холодильник": "🧊 Мой холодильник",
        "Добавить продукты": "➕ Добавить продукты",
        "Рецепты": "🍳 Рецепты",
        "Каталог блюд": "🍽️ Каталог блюд",
        "Меню": "🗓️ Меню на неделю",
        "Меню на неделю": "🗓️ Меню на неделю",
        "Список покупок": "🛒 Список покупок",
        "Питание и цели": "🎯 Питание и цели",
        "Любимые блюда": "❤️ Любимые блюда",
        "История": "📜 История",
        "Списания": "📉 Списания",
        "Демо-режим": "🧪 Демо-режим",
        "Скоро испортится": "⏰ Скоро испортится",
        "Фото и сканер": "📸 Фото и сканер",
        "Фото": "📸 Фото и сканер",
        "Сканер": "📸 Фото и сканер",
        "📸": "📸 Фото и сканер",
    }

    target_page = aliases.get(target_page, target_page)
    st.session_state["pending_navigation"] = target_page

    try:
        st.session_state["main_navigation"] = target_page
    except Exception:
        pass

    st.rerun()


def apply_modern_ui_v13():
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #f5f8f6 !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.4rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3 {
    line-height: 1.18 !important;
    overflow: visible !important;
    padding-bottom: 0.12em !important;
    color: #123321 !important;
}

a[href^="#"] {
    display: none !important;
}

.stDeployButton,
[data-testid="stToolbar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7fff9 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.15rem !important;
    line-height: 1.25 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 3px !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
}

div.stButton > button {
    border-radius: 18px !important;
    min-height: 48px !important;
    font-weight: 750 !important;
    border: 1px solid rgba(18, 51, 33, 0.12) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10) !important;
}

[data-testid="stExpander"] {
    border-radius: 20px !important;
    overflow: hidden !important;
}

.stForm {
    border-radius: 22px !important;
}

input, textarea, select {
    border-radius: 16px !important;
}

/* Карточки нового UI */
.medinki-hero {
    padding: 28px 30px;
    border-radius: 32px;
    background: linear-gradient(135deg, #123321 0%, #246b43 100%);
    color: white;
    box-shadow: 0 18px 46px rgba(15, 23, 42, 0.15);
    margin-bottom: 20px;
}

.medinki-hero h1 {
    color: white !important;
    margin: 0 0 10px 0;
}

.medinki-hero p {
    margin: 0;
    opacity: .92;
    font-size: 1.08rem;
}

.medinki-card {
    padding: 22px;
    border-radius: 26px;
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 12px 30px rgba(15,23,42,.07);
    margin-bottom: 18px;
}

.medinki-soft {
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
}

.medinki-user-card {
    padding: 20px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
    border: 1px solid rgba(34,197,94,.18);
    min-height: 150px;
}

.medinki-pill {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    margin: 4px 6px 0 0;
    font-weight: 800;
    font-size: .86rem;
}

.medinki-pill-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.medinki-pill-purple {
    background: #ede9fe;
    color: #6d28d9;
}

.medinki-pill-green {
    background: #dcfce7;
    color: #15803d;
}

@media (max-width: 760px) {
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 {
        font-size: 1.85rem !important;
    }

    h2 {
        font-size: 1.45rem !important;
    }

    h3 {
        font-size: 1.22rem !important;
    }

    .medinki-hero {
        padding: 20px;
        border-radius: 24px;
    }

    .medinki-card {
        padding: 16px;
        border-radius: 22px;
    }

    div.stButton > button {
        min-height: 52px !important;
        font-size: 1rem !important;
    }

    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 330px !important;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_v13_fast_actions():
    st.markdown("## ⚡ Быстрые действия")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("➕ Добавить еду", key="modern_fast_add_food_v13", use_container_width=True):
            modern_go("📔 Дневник питания")

        if st.button("🧊 Холодильник", key="modern_fast_fridge_v13", use_container_width=True):
            modern_go("🧊 Мой холодильник")

        if st.button("🗓️ Меню", key="modern_fast_menu_v13", use_container_width=True):
            modern_go("🗓️ Меню на неделю")

        if st.button("📸 Фото и сканер", key="modern_fast_photo_v13", use_container_width=True):
            modern_go("📸 Фото и сканер")

    with c2:
        if st.button("🛒 Добавить покупку", key="modern_fast_shopping_v13", use_container_width=True):
            modern_go("🛒 Умные покупки")

        if st.button("⏰ Скоро испортится", key="modern_fast_expiring_v13", use_container_width=True):
            modern_go("⏰ Скоро испортится")

        if st.button("📊 Аналитика", key="modern_fast_analytics_v13", use_container_width=True):
            modern_go("📊 Аналитика")

        if st.button("🍳 Рецепты", key="modern_fast_recipes_v13", use_container_width=True):
            modern_go("🍳 Рецепты")


def render_v13_clean_fast_screen():
    apply_modern_ui_v13()

    st.markdown(
        """
<div class="medinki-hero">
    <h1>🧊 Умный холодильник Мединки</h1>
    <p>Главное на сегодня: питание, покупки, холодильник, рецепты и фото-сканер.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    components.html(
        """
<div style="
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    padding: 14px 18px;
    border-radius: 22px;
    background: linear-gradient(135deg, #fff7ed 0%, #f0fdf4 100%);
    border: 1px solid rgba(18,51,33,.10);
    color: #123321;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 12px;
">
    <span>🕒 </span><span id="medinki-clock">--:--:--</span>
</div>
<script>
function updateClock() {
    const el = document.getElementById("medinki-clock");
    if (!el) return;
    const now = new Date();
    const text = now.toLocaleDateString("ru-RU", {
        weekday: "long",
        day: "2-digit",
        month: "long"
    }) + " · " + now.toLocaleTimeString("ru-RU");
    el.innerText = text;
}
updateClock();
setInterval(updateClock, 1000);
</script>
""",
        height=78,
    )

    active_user = (
        st.session_state.get("active_user")
        or st.session_state.get("current_user")
        or st.session_state.get("user")
        or "Мишка"
    )

    st.markdown(
        f"""
<div class="medinki-card medinki-soft">
    <h2>👤 Активный пользователь: {active_user}</h2>
    <p style="margin-bottom:0;color:#475569;">Быстрые действия применяются к текущему пользователю.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("## 🍽️ Калории сегодня")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
<div class="medinki-user-card">
    <h2>🐻 Мишка</h2>
    <span class="medinki-pill medinki-pill-blue">Цель: 2300 ккал</span>
    <span class="medinki-pill medinki-pill-purple">Съедено: —</span>
    <span class="medinki-pill medinki-pill-green">Осталось: —</span>
</div>
""",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
<div class="medinki-user-card">
    <h2>🌸 Мединка</h2>
    <span class="medinki-pill medinki-pill-blue">Цель: 1800 ккал</span>
    <span class="medinki-pill medinki-pill-purple">Съедено: —</span>
    <span class="medinki-pill medinki-pill-green">Осталось: —</span>
</div>
""",
            unsafe_allow_html=True,
        )

    render_v13_fast_actions()

    st.markdown("## 📌 Сегодня")
    st.markdown(
        """
<div class="medinki-card">
    <h3>🥦 Рекомендации</h3>
    <p style="color:#475569;margin-bottom:0;">
        Проверь срочные продукты, добавь еду в дневник или сфотографируй новый продукт через фото-сканер.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )
'''


REQUEST_NAVIGATION_CODE = r'''
def request_navigation(target_page: str):
    from modern_ui_v13 import modern_go
    modern_go(target_page)
'''


FAST_ACTION_WRAPPER_CODE = r'''
def render_fast_action_buttons():
    from modern_ui_v13 import render_v13_fast_actions
    render_v13_fast_actions()
'''


PAGE_INTRO_CODE = r'''
def render_page_intro(title=None, subtitle=None, icon=None, *args, **kwargs):
    if title is None:
        title = kwargs.get("title", "Умный холодильник Мединки")

    if subtitle is None:
        subtitle = kwargs.get("subtitle", "Холодильник, меню, рецепты, покупки и списание продуктов.")

    if icon is None:
        icon = kwargs.get("icon", "🥦")

    st.markdown(
        f"""
<div class="medinki-card medinki-soft">
    <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
        <div style="font-size:2.1rem;line-height:1;">{icon}</div>
        <div>
            <h1 style="margin:0;line-height:1.18;color:#123321;">{title}</h1>
            <p style="margin:8px 0 0 0;color:#475569;font-size:1.06rem;">{subtitle}</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
'''


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"auto_rebuild_ui_v13_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def compile_py(path: Path):
    py_compile.compile(str(path), doraise=True)


def write_modern_ui_module():
    backup(MODERN_UI)
    MODERN_UI.write_text(MODERN_UI_CODE, encoding="utf-8")
    compile_py(MODERN_UI)
    print("modern_ui_v13.py written.")


def find_safe_insert_after_imports(text: str) -> int:
    lines = text.splitlines()
    insert_idx = 0
    depth = 0
    in_imports = False

    def delta(line):
        cleaned = re.sub(r'".*?"', '""', line)
        cleaned = re.sub(r"'.*?'", "''", cleaned)
        return (
            cleaned.count("(")
            + cleaned.count("[")
            + cleaned.count("{")
            - cleaned.count(")")
            - cleaned.count("]")
            - cleaned.count("}")
        )

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            if i == insert_idx:
                insert_idx = i + 1
            continue

        is_import = stripped.startswith("import ") or stripped.startswith("from ")

        if is_import and depth == 0:
            in_imports = True
            depth += delta(line)
            insert_idx = i + 1
            if depth <= 0:
                depth = 0
            continue

        if in_imports and depth > 0:
            depth += delta(line)
            insert_idx = i + 1
            if depth <= 0:
                depth = 0
            continue

        if is_import and depth == 0:
            insert_idx = i + 1
            continue

        break

    return insert_idx


def ensure_import_and_css_call(text: str) -> str:
    if "from modern_ui_v13 import apply_modern_ui_v13, render_v13_clean_fast_screen" not in text:
        lines = text.splitlines()
        idx = find_safe_insert_after_imports(text)
        lines.insert(idx, "from modern_ui_v13 import apply_modern_ui_v13, render_v13_clean_fast_screen")
        text = "\n".join(lines) + "\n"
        print("Added modern_ui_v13 import.")

    if "apply_modern_ui_v13()" not in text:
        m = re.search(r"st\.set_page_config\s*\((?s:.*?)\)\s*", text)
        if m:
            text = text[:m.end()] + "\napply_modern_ui_v13()\n" + text[m.end():]
            print("Added apply_modern_ui_v13() after st.set_page_config.")
        else:
            lines = text.splitlines()
            idx = find_safe_insert_after_imports(text)
            lines.insert(idx + 1, "apply_modern_ui_v13()")
            text = "\n".join(lines) + "\n"
            print("Added apply_modern_ui_v13() after imports.")

    return text


def replace_function(text: str, func_name: str, code: str) -> str:
    pattern = rf'(?ms)^def\s+{re.escape(func_name)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'
    new_text, count = re.subn(pattern, code.strip() + "\n\n", text, count=1)

    if count:
        print(f"Replaced {func_name}().")
        return new_text

    text += "\n\n" + code.strip() + "\n"
    print(f"Added {func_name}().")
    return text


def ensure_pending_navigation_before_widget(text: str) -> str:
    if '"pending_navigation" in st.session_state' in text or "'pending_navigation' in st.session_state" in text:
        return text

    lines = text.splitlines()
    key_idx = None

    for i, line in enumerate(lines):
        if "main_navigation" in line and "key" in line:
            key_idx = i
            break

    if key_idx is None:
        print("main_navigation widget not found, skip pending block.")
        return text

    start_idx = key_idx
    markers = ["st.sidebar.radio", "st.sidebar.selectbox", "st.radio", "st.selectbox", "option_menu"]

    for i in range(key_idx, max(-1, key_idx - 50), -1):
        if any(marker in lines[i] for marker in markers):
            start_idx = i
            break

    indent = re.match(r"\s*", lines[start_idx]).group(0)
    block = [
        f'{indent}# Применяем переходы от быстрых кнопок ДО создания виджета меню.',
        f'{indent}if "pending_navigation" in st.session_state:',
        f'{indent}    st.session_state["main_navigation"] = st.session_state.pop("pending_navigation")',
        "",
    ]

    lines[start_idx:start_idx] = block
    print("Added pending_navigation block.")
    return "\n".join(lines) + "\n"


def replace_fast_screen_route(text: str) -> str:
    lines = text.splitlines()
    changed = False
    i = 0

    while i < len(lines):
        line = lines[i]

        if "page" in line and "Быстрый экран" in line and line.strip().endswith(":"):
            indent = re.match(r"\s*", line).group(0)
            body_indent = indent + "    "

            j = i + 1
            while j < len(lines):
                stripped = lines[j].strip()

                if stripped and not lines[j].startswith(body_indent):
                    break

                j += 1

            lines[i + 1:j] = [body_indent + "render_v13_clean_fast_screen()"]
            changed = True
            print("Fast screen route replaced with clean UI.")
            i = j
            continue

        i += 1

    if not changed:
        print("Fast screen route not found. No route replacement.")

    return "\n".join(lines) + "\n"


def cleanup_bad_texts(text: str) -> str:
    replacements = {
        "Кто входит?": "Вход в приложение",
        "Выберите пользователя и введите PIN-код.": "Введите логин и PIN-код.",
        "Пользователь": "Логин",
        "Быстрый мобильный экран": "Главное на сегодня",
        "Самые нужные действия на одном экране: калории, меню на сегодня, холодильник, покупки и срочные продукты.": "Калории, меню, покупки, холодильник и срочные продукты — всё в одном месте.",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Удаляем одиночные строки с лишними подсказками/телефоном, не трогая большие блоки.
    remove_needles = [
        "Подсказка для первого входа",
        "временные значения",
        "1111",
        "2222",
        "Откройте ссылку на телефоне",
        "добавьте на главный экран",
        "Быстро заполнить демо-данными",
        "Быстро заполнить демо",
        "Обновить данные",
        "🔄 Обновить данные",
    ]

    new_lines = []
    removed = 0

    for line in text.splitlines():
        if any(n in line for n in remove_needles):
            removed += 1
            continue
        new_lines.append(line)

    if removed:
        print(f"Removed noisy UI lines: {removed}")

    return "\n".join(new_lines) + "\n"


def ensure_photo_route(text: str) -> str:
    if "render_media_page()" in text:
        return text

    if "from media_page import render_media_page" not in text:
        lines = text.splitlines()
        idx = find_safe_insert_after_imports(text)
        lines.insert(idx, "from media_page import render_media_page")
        text = "\n".join(lines) + "\n"
        print("Added media_page import.")

    patterns = [
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']🏠\s*Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\'][^"\']+["\']\s*:',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            indent = m.group(1)
            route = f'{indent}elif page in ("📸 Фото и сканер", "Фото и сканер", "📸"):\n{indent}    render_media_page()\n'
            text = text[:m.start()] + route + text[m.start():]
            print("Added photo scanner route.")
            return text

    return text


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = ensure_import_and_css_call(text)
    text = replace_function(text, "request_navigation", REQUEST_NAVIGATION_CODE)
    text = replace_function(text, "render_fast_action_buttons", FAST_ACTION_WRAPPER_CODE)
    text = replace_function(text, "render_page_intro", PAGE_INTRO_CODE)
    text = ensure_pending_navigation_before_widget(text)
    text = replace_fast_screen_route(text)
    text = cleanup_bad_texts(text)
    text = ensure_photo_route(text)

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    print("app.py syntax OK.")


def main():
    print("=== Auto rebuild UI v1.3 ===")

    write_modern_ui_module()
    patch_app()

    print()
    print("Готово ✅")
    print("UI обновлён:")
    print("- новый быстрый экран;")
    print("- рабочие быстрые кнопки;")
    print("- живые часы без кнопки обновления;")
    print("- оба пользователя сразу;")
    print("- более аккуратный sidebar;")
    print("- фото-сканер в быстрых действиях;")
    print("- исправлены заголовки и обрезания текста.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
