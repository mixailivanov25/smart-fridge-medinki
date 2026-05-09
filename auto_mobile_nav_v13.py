from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
MOBILE_NAV = ROOT / "mobile_nav_v13.py"


MOBILE_NAV_CODE = r'''
import streamlit as st
from urllib.parse import quote


NAV_ALIASES = {
    "fast": "📱 Быстрый экран",
    "home": "🏠 Главная",
    "fridge": "🧊 Мой холодильник",
    "photo": "📸 Фото и сканер",
    "shopping": "🛒 Умные покупки",
    "analytics": "📊 Аналитика",
    "diary": "📔 Дневник питания",
    "recipes": "🍳 Рецепты",
    "menu": "🗓️ Меню на неделю",
}


def process_mobile_nav_v13():
    """
    Обрабатывает переходы из нижней мобильной навигации.

    Ссылки вида:
        ?go=home
        ?go=fridge
        ?go=photo

    превращаются в установку main_navigation.
    """
    try:
        go = st.query_params.get("go", None)
    except Exception:
        go = None

    if isinstance(go, list):
        go = go[0] if go else None

    if not go:
        return

    target = NAV_ALIASES.get(str(go).strip())

    if not target:
        return

    # Чтобы query param не перетирал выбор из sidebar на каждом rerun.
    last = st.session_state.get("_last_mobile_nav_go_v13")

    if last == go:
        return

    st.session_state["_last_mobile_nav_go_v13"] = go
    st.session_state["pending_navigation"] = target

    try:
        st.session_state["main_navigation"] = target
    except Exception:
        pass


def apply_modern_sidebar_and_mobile_nav_v13():
    """
    Современный вид sidebar + нижняя мобильная навигация.
    """
    st.markdown(
        """
<style>
/* ===== Modern sidebar nav ===== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(34, 197, 94, .10), transparent 34%),
        linear-gradient(180deg, #f4fff8 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08) !important;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
}

/* Прячем radio-кружки */
[data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] {
    display: none !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    position: absolute !important;
}

/* Убираем контейнеры кружков в разных версиях Streamlit */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child:has(input[type="radio"]) {
    display: none !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    min-height: 38px !important;
    border-radius: 16px !important;
    padding: 9px 12px !important;
    margin: 0 !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: #123321 !important;
    font-weight: 650 !important;
    transition:
        background .16s ease,
        transform .16s ease,
        box-shadow .16s ease,
        border-color .16s ease !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
    border-color: rgba(34, 197, 94, 0.14) !important;
    transform: translateX(2px) !important;
}

/* Активный пункт через :has */
[data-testid="stSidebar"] [role="radiogroup"] label:has(input[type="radio"]:checked) {
    background: linear-gradient(135deg, rgba(34,197,94,.20), rgba(240,253,244,.95)) !important;
    border-color: rgba(34,197,94,.28) !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.06) !important;
    color: #0b2f20 !important;
}

/* Если Streamlit рисует пустой круг не input-ом */
[data-testid="stSidebar"] [role="radiogroup"] svg {
    display: none !important;
}

/* Sidebar title compact */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    line-height: 1.18 !important;
}

/* ===== Bottom mobile navigation ===== */

.medinki-bottom-nav-v13 {
    display: none;
}

@media (max-width: 760px) {
    .block-container {
        padding-bottom: 6.2rem !important;
    }

    .medinki-bottom-nav-v13 {
        position: fixed;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        left: 10px;
        right: 10px;
        bottom: 10px;
        z-index: 999999;
        padding: 8px;
        border-radius: 26px;
        background: rgba(255,255,255,.92);
        border: 1px solid rgba(18, 51, 33, .10);
        box-shadow: 0 18px 44px rgba(15,23,42,.18);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        gap: 6px;
    }

    .medinki-bottom-nav-v13 a {
        text-decoration: none !important;
        color: #123321 !important;
        border-radius: 20px;
        padding: 8px 4px 7px 4px;
        min-height: 46px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 800;
        font-size: 10px;
        line-height: 1.05;
        transition: background .15s ease, transform .15s ease;
    }

    .medinki-bottom-nav-v13 a:hover {
        background: rgba(34,197,94,.12);
        transform: translateY(-1px);
    }

    .medinki-bottom-nav-v13 .nav-emoji {
        font-size: 20px;
        line-height: 1;
    }

    .medinki-bottom-nav-v13 .nav-text {
        white-space: nowrap;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_bottom_mobile_nav_v13():
    """
    Фиксированная нижняя мобильная навигация.
    На desktop скрыта через CSS.
    """
    items = [
        ("home", "🏠", "Главная"),
        ("fridge", "🧊", "Холод."),
        ("photo", "📸", "Фото"),
        ("shopping", "🛒", "Покупки"),
        ("analytics", "📊", "Аналит."),
    ]

    links = []

    for key, emoji, label in items:
        href = f"?go={quote(key)}"
        links.append(
            f"""
<a href="{href}" target="_self">
    <span class="nav-emoji">{emoji}</span>
    <span class="nav-text">{label}</span>
</a>
"""
        )

    html = f"""
<div class="medinki-bottom-nav-v13">
    {''.join(links)}
</div>
"""

    st.markdown(html, unsafe_allow_html=True)
'''


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"mobile_nav_v13_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def compile_py(path: Path):
    py_compile.compile(str(path), doraise=True)


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


def find_set_page_config_end(text: str):
    start = text.find("st.set_page_config")
    if start == -1:
        return None

    paren = text.find("(", start)
    if paren == -1:
        return None

    depth = 0
    in_string = None
    triple = False
    escape = False

    i = paren

    while i < len(text):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif triple and text.startswith(in_string * 3, i):
                i += 2
                in_string = None
                triple = False
            elif not triple and ch == in_string:
                in_string = None

            i += 1
            continue

        if text.startswith('"""', i):
            in_string = '"'
            triple = True
            i += 3
            continue

        if text.startswith("'''", i):
            in_string = "'"
            triple = True
            i += 3
            continue

        if ch in ("'", '"'):
            in_string = ch
            triple = False
            i += 1
            continue

        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                line_end = text.find("\n", i)
                if line_end == -1:
                    return i + 1
                return line_end + 1

        i += 1

    return None


def write_mobile_nav_module():
    backup(MOBILE_NAV)
    MOBILE_NAV.write_text(MOBILE_NAV_CODE, encoding="utf-8")
    compile_py(MOBILE_NAV)
    print("mobile_nav_v13.py written.")


def remove_existing_calls(text: str) -> str:
    remove_exact = {
        "apply_modern_sidebar_and_mobile_nav_v13()",
        "process_mobile_nav_v13()",
        "render_bottom_mobile_nav_v13()",
    }

    lines = []
    removed = 0

    for line in text.splitlines():
        if line.strip() in remove_exact:
            removed += 1
            continue
        lines.append(line)

    if removed:
        print(f"Removed duplicate mobile nav calls: {removed}")

    return "\n".join(lines) + "\n"


def ensure_import(text: str) -> str:
    import_line = (
        "from mobile_nav_v13 import "
        "apply_modern_sidebar_and_mobile_nav_v13, "
        "process_mobile_nav_v13, "
        "render_bottom_mobile_nav_v13"
    )

    # Удаляем старые импорты этого модуля.
    lines = []
    removed = 0

    for line in text.splitlines():
        if line.strip().startswith("from mobile_nav_v13 import"):
            removed += 1
            continue
        lines.append(line)

    text = "\n".join(lines) + "\n"

    idx = find_safe_insert_after_imports(text)
    lines = text.splitlines()
    lines.insert(idx, import_line)

    print("Ensured mobile_nav_v13 import.")
    return "\n".join(lines) + "\n"


def insert_calls_after_config(text: str) -> str:
    calls = (
        "apply_modern_sidebar_and_mobile_nav_v13()\n"
        "process_mobile_nav_v13()\n"
        "render_bottom_mobile_nav_v13()\n"
    )

    insert_pos = find_set_page_config_end(text)

    if insert_pos is not None:
        text = text[:insert_pos] + calls + text[insert_pos:]
        print("Inserted mobile nav calls after st.set_page_config().")
        return text

    # Если set_page_config нет — перед первой функцией.
    m = re.search(r"(?m)^def\s+", text)

    if m:
        text = text[:m.start()] + calls + "\n" + text[m.start():]
        print("Inserted mobile nav calls before first function.")
        return text

    idx = find_safe_insert_after_imports(text)
    lines = text.splitlines()
    lines[idx:idx] = calls.strip().splitlines()
    print("Inserted mobile nav calls after imports.")
    return "\n".join(lines) + "\n"


def ensure_pending_navigation_block(text: str) -> str:
    """
    На всякий случай убеждаемся, что pending_navigation применяется
    до создания виджета main_navigation.
    """
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
    markers = [
        "st.sidebar.radio",
        "st.sidebar.selectbox",
        "st.radio",
        "st.selectbox",
        "option_menu",
    ]

    for i in range(key_idx, max(-1, key_idx - 60), -1):
        if any(marker in lines[i] for marker in markers):
            start_idx = i
            break

    indent = re.match(r"\s*", lines[start_idx]).group(0)

    block = [
        f'{indent}# Применяем переходы от мобильной/быстрой навигации ДО создания меню.',
        f'{indent}if "pending_navigation" in st.session_state:',
        f'{indent}    st.session_state["main_navigation"] = st.session_state.pop("pending_navigation")',
        "",
    ]

    lines[start_idx:start_idx] = block
    print("Inserted pending_navigation block before main navigation widget.")

    return "\n".join(lines) + "\n"


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = remove_existing_calls(text)
    text = ensure_import(text)
    text = insert_calls_after_config(text)
    text = ensure_pending_navigation_block(text)

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    print("app.py syntax OK.")


def main():
    print("=== Modern sidebar + bottom mobile nav v1.3 ===")

    write_mobile_nav_module()
    patch_app()

    print()
    print("Готово ✅")
    print("Добавлено:")
    print("- современный левый sidebar без radio-кружков;")
    print("- активный пункт меню в виде зелёной карточки;")
    print("- нижняя мобильная навигация;")
    print("- переходы: Главная, Холодильник, Фото, Покупки, Аналитика.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
