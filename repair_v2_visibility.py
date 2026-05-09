from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys
import socket
import time
import webbrowser
import os

ROOT = Path.cwd()
APP = ROOT / "app.py"
V2 = ROOT / "v2_foundation.py"

V2_PAGE = "🌟 Новый интерфейс v2"


MINIMAL_V2_CODE = r'''
import streamlit as st
import streamlit.components.v1 as components

V2_PAGE = "🌟 Новый интерфейс v2"


def v2_set_page(tab: str):
    st.session_state["v2_tab"] = tab
    st.rerun()


def apply_v2_design():
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fbf8 0%, #f3f7f4 100%) !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.15rem !important;
    padding-bottom: 6.5rem !important;
}

h1, h2, h3 {
    color: #10281c !important;
    line-height: 1.15 !important;
    letter-spacing: -0.035em !important;
    overflow: visible !important;
}

a[href^="#"], .stDeployButton, [data-testid="stToolbar"] {
    display: none !important;
}

.v2-hero {
    border-radius: 34px;
    padding: 30px;
    background:
        radial-gradient(circle at top right, rgba(255,255,255,.22), transparent 28%),
        linear-gradient(135deg, #123321 0%, #1f6b43 100%);
    color: white;
    box-shadow: 0 24px 58px rgba(15,23,42,.18);
    margin-bottom: 18px;
}

.v2-hero h1 {
    color: white !important;
    margin: 0 0 10px 0 !important;
    font-size: clamp(2rem, 4vw, 3.5rem) !important;
}

.v2-hero p {
    color: rgba(255,255,255,.92) !important;
    margin: 0 !important;
    font-size: 1.08rem;
}

.v2-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

.v2-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.v2-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.v2-card {
    border-radius: 28px;
    padding: 22px;
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 18px 42px rgba(15,23,42,.09);
    margin-bottom: 16px;
}

.v2-card-soft {
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
}

.v2-card-warm {
    background: linear-gradient(135deg, #fff7ed 0%, #fff 48%, #fdf2f8 100%);
}

.v2-metric {
    font-size: 2.15rem;
    font-weight: 950;
    color: #10281c;
    letter-spacing: -.04em;
}

.v2-label {
    color: #647067;
    font-weight: 650;
    margin-top: 4px;
}

.v2-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 11px;
    border-radius: 999px;
    margin: 4px 5px 0 0;
    font-weight: 850;
    font-size: .86rem;
}

.v2-chip-green { background: #dcfce7; color: #166534; }
.v2-chip-blue { background: #dbeafe; color: #1d4ed8; }
.v2-chip-purple { background: #ede9fe; color: #6d28d9; }
.v2-chip-orange { background: #ffedd5; color: #c2410c; }

.v2-photo-placeholder {
    height: 150px;
    border-radius: 22px;
    background:
        radial-gradient(circle at top right, rgba(236,72,153,.20), transparent 35%),
        linear-gradient(135deg, #fff7ed 0%, #fdf2f8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3.2rem;
    margin-bottom: 14px;
}

.v2-bottom-nav {
    display: none;
}

@media (max-width: 900px) {
    .block-container {
        padding: .95rem 1rem 6.8rem 1rem !important;
    }

    .v2-grid-4,
    .v2-grid-3,
    .v2-grid-2 {
        grid-template-columns: 1fr !important;
        gap: 14px;
    }

    .v2-hero {
        border-radius: 26px;
        padding: 22px;
    }

    .v2-card {
        border-radius: 24px;
        padding: 18px;
    }

    .v2-bottom-nav {
        position: fixed;
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        left: 10px;
        right: 10px;
        bottom: 10px;
        z-index: 2147483647;
        padding: 8px;
        border-radius: 26px;
        background: rgba(255,255,255,.95);
        border: 1px solid rgba(18,51,33,.12);
        box-shadow: 0 18px 48px rgba(15,23,42,.20);
        backdrop-filter: blur(16px);
        gap: 6px;
    }

    .v2-bottom-nav button {
        border: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        min-height: 48px !important;
        font-size: 0.78rem !important;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def process_v2_query_navigation():
    try:
        tab = st.query_params.get("v2tab", None)
    except Exception:
        tab = None

    if isinstance(tab, list):
        tab = tab[0] if tab else None

    if tab in {"today", "fridge", "scan", "recipes", "shopping"}:
        st.session_state["v2_tab"] = tab


def render_v2_bottom_nav():
    st.markdown('<div class="v2-bottom-nav">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🏠 Сегодня", key="v2_mob_today", use_container_width=True):
            v2_set_page("today")
    with c2:
        if st.button("🧊 Холод.", key="v2_mob_fridge", use_container_width=True):
            v2_set_page("fridge")
    with c3:
        if st.button("📸 Сканер", key="v2_mob_scan", use_container_width=True):
            v2_set_page("scan")
    with c4:
        if st.button("🍳 Рецепты", key="v2_mob_recipes", use_container_width=True):
            v2_set_page("recipes")
    with c5:
        if st.button("🛒 Покупки", key="v2_mob_shopping", use_container_width=True):
            v2_set_page("shopping")
    st.markdown("</div>", unsafe_allow_html=True)


def render_v2_today():
    st.markdown(
        """
<div class="v2-hero">
    <h1>🧊 Сегодня у Мединки</h1>
    <p>Главное на одном экране: питание, холодильник, покупки, рецепты и фото-сканер.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="v2-grid-4">
    <div class="v2-card"><div class="v2-metric">12</div><div class="v2-label">продуктов дома</div></div>
    <div class="v2-card"><div class="v2-metric">2</div><div class="v2-label">требуют внимания</div></div>
    <div class="v2-card"><div class="v2-metric">1</div><div class="v2-label">блюдо можно приготовить</div></div>
    <div class="v2-card"><div class="v2-metric">3604</div><div class="v2-label">ккал в запасах</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("## ⚡ Быстрые действия")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📸 Сканировать", use_container_width=True, key="v2_action_scan"):
            v2_set_page("scan")
    with c2:
        if st.button("🧊 Холодильник", use_container_width=True, key="v2_action_fridge"):
            v2_set_page("fridge")
    with c3:
        if st.button("🍳 Рецепты", use_container_width=True, key="v2_action_recipes"):
            v2_set_page("recipes")
    with c4:
        if st.button("🛒 Покупки", use_container_width=True, key="v2_action_shopping"):
            v2_set_page("shopping")

    st.markdown("## 🍽️ Питание сегодня")

    st.markdown(
        """
<div class="v2-grid-2">
    <div class="v2-card v2-card-soft">
        <h2>🐻 Мишка</h2>
        <span class="v2-chip v2-chip-green">2300 ккал/день</span>
        <span class="v2-chip v2-chip-blue">съедено: 320</span>
        <span class="v2-chip v2-chip-purple">осталось: 1980</span>
    </div>
    <div class="v2-card v2-card-soft">
        <h2>🌸 Мединка</h2>
        <span class="v2-chip v2-chip-green">1800 ккал/день</span>
        <span class="v2-chip v2-chip-blue">съедено: 0</span>
        <span class="v2-chip v2-chip-purple">осталось: 1800</span>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_v2_fridge():
    st.markdown('<div class="v2-hero"><h1>🧊 Холодильник</h1><p>Карточки продуктов, сроки годности и быстрые действия.</p></div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="v2-grid-3">
    <div class="v2-card"><div class="v2-photo-placeholder">🍊</div><h2>Апельсин</h2><span class="v2-chip v2-chip-green">1 шт</span><span class="v2-chip v2-chip-blue">47 ккал</span></div>
    <div class="v2-card"><div class="v2-photo-placeholder">🥩</div><h2>Фарш</h2><span class="v2-chip v2-chip-green">500 г</span><span class="v2-chip v2-chip-orange">скоро</span></div>
    <div class="v2-card"><div class="v2-photo-placeholder">🥕</div><h2>Морковь</h2><span class="v2-chip v2-chip-green">4 шт</span><span class="v2-chip v2-chip-blue">41 ккал</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_v2_scan():
    st.markdown('<div class="v2-hero"><h1>📸 Сканер продуктов</h1><p>Фото продукта → распознавание → подтверждение → холодильник.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="v2-card v2-card-warm"><h2>AI Vision Scanner</h2><p>В следующем шаге подключим распознавание названия, срока годности, калорий и категории.</p><span class="v2-chip v2-chip-purple">камера</span><span class="v2-chip v2-chip-blue">AI</span></div>', unsafe_allow_html=True)


def render_v2_recipes():
    st.markdown('<div class="v2-hero"><h1>🍳 Рецепты и меню</h1><p>Красивые карточки блюд, фото, калории и готовка в один клик.</p></div>', unsafe_allow_html=True)
    st.markdown(
        """
<div class="v2-grid-3">
    <div class="v2-card"><div class="v2-photo-placeholder">🍳</div><h2>Омлет</h2><p>Нежный завтрак.</p><span class="v2-chip v2-chip-green">320 ккал</span></div>
    <div class="v2-card"><div class="v2-photo-placeholder">🍗</div><h2>Курица с рисом</h2><p>Сытное блюдо.</p><span class="v2-chip v2-chip-green">560 ккал</span></div>
    <div class="v2-card"><div class="v2-photo-placeholder">🥣</div><h2>Овсянка</h2><p>Быстрый завтрак.</p><span class="v2-chip v2-chip-green">350 ккал</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_v2_shopping():
    st.markdown('<div class="v2-hero"><h1>🛒 Покупки</h1><p>Что купить, что куплено и что перенести в холодильник.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="v2-card"><h2>Нужно купить</h2><p>Курица · 1050 г</p><p>Молоко · 250 мл</p><span class="v2-chip v2-chip-orange">для рецептов</span></div>', unsafe_allow_html=True)


def render_v2_app():
    apply_v2_design()
    process_v2_query_navigation()
    render_v2_bottom_nav()

    tab = st.session_state.get("v2_tab", "today")

    nav_cols = st.columns(5)
    labels = [
        ("today", "🏠 Сегодня"),
        ("fridge", "🧊 Холодильник"),
        ("scan", "📸 Сканер"),
        ("recipes", "🍳 Рецепты"),
        ("shopping", "🛒 Покупки"),
    ]

    for col, (key, label) in zip(nav_cols, labels):
        with col:
            if st.button(label, use_container_width=True, key=f"v2_top_nav_{key}"):
                v2_set_page(key)

    if tab == "fridge":
        render_v2_fridge()
    elif tab == "scan":
        render_v2_scan()
    elif tab == "recipes":
        render_v2_recipes()
    elif tab == "shopping":
        render_v2_shopping()
    else:
        render_v2_today()
'''


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"repair_v2_visibility_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def compile_py(path: Path):
    py_compile.compile(str(path), doraise=True)


def ensure_v2_module():
    if V2.exists():
        try:
            compile_py(V2)
            print("v2_foundation.py exists and syntax OK.")
            return
        except Exception:
            print("v2_foundation.py exists but broken, rewriting minimal version.")

    backup(V2)
    V2.write_text(MINIMAL_V2_CODE, encoding="utf-8")
    compile_py(V2)
    print("v2_foundation.py written.")


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


def find_matching(text: str, start_idx: int, open_ch: str, close_ch: str):
    depth = 0
    in_str = None
    triple = False
    escape = False

    i = start_idx
    while i < len(text):
        ch = text[i]

        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif triple and text.startswith(in_str * 3, i):
                i += 2
                in_str = None
                triple = False
            elif not triple and ch == in_str:
                in_str = None
            i += 1
            continue

        if text.startswith('"""', i):
            in_str = '"'
            triple = True
            i += 3
            continue

        if text.startswith("'''", i):
            in_str = "'"
            triple = True
            i += 3
            continue

        if ch in ("'", '"'):
            in_str = ch
            triple = False
            i += 1
            continue

        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return -1


def container_has_pages(block: str):
    markers = ["Быстрый экран", "Главная", "Холодильник", "Рецепты", "Меню", "Аналитика"]
    return sum(1 for m in markers if m in block) >= 2


def force_add_v2_to_menu(text: str):
    """
    ВАЖНО: не проверяем V2_PAGE глобально.
    Проверяем именно конкретный список/словарь меню.
    """
    added = False

    markers = [
        '"📱 Быстрый экран"',
        "'📱 Быстрый экран'",
        '"Быстрый экран"',
        "'Быстрый экран'",
    ]

    for marker in markers:
        search = 0

        while True:
            idx = text.find(marker, search)
            if idx == -1:
                break

            search = idx + len(marker)

            list_start = text.rfind("[", 0, idx)
            dict_start = text.rfind("{", 0, idx)

            # Список
            if list_start != -1 and list_start > dict_start:
                list_end = find_matching(text, list_start, "[", "]")
                if list_end != -1:
                    block = text[list_start:list_end + 1]
                    if container_has_pages(block) and V2_PAGE not in block:
                        line_end = text.find("\n", idx)
                        if line_end == -1:
                            line_end = idx + len(marker)
                        line_start = text.rfind("\n", 0, idx) + 1
                        indent = re.match(r"\s*", text[line_start:idx]).group(0)
                        text = text[:line_end] + f'\n{indent}"{V2_PAGE}",' + text[line_end:]
                        print("Added v2 page to list menu.")
                        return text

            # Словарь
            if dict_start != -1 and dict_start > list_start:
                dict_end = find_matching(text, dict_start, "{", "}")
                if dict_end != -1:
                    block = text[dict_start:dict_end + 1]
                    if container_has_pages(block) and V2_PAGE not in block:
                        local = re.search(
                            r'(?m)^(\s*)(["\'](?:📱\s*)?Быстрый экран["\']\s*:\s*.+?,?\s*)$',
                            block,
                        )
                        if local:
                            insert_pos = dict_start + local.end(0)
                            indent = local.group(1)
                            text = text[:insert_pos] + f'\n{indent}"{V2_PAGE}": "stars",' + text[insert_pos:]
                            print("Added v2 page to dict menu.")
                            return text

    print("Could not find menu container for v2. Will add direct URL fallback.")
    return text


def ensure_import(text: str):
    import_line = "from v2_foundation import render_v2_app"

    lines = []
    removed = 0

    for line in text.splitlines():
        if line.strip().startswith("from v2_foundation import"):
            removed += 1
            continue
        lines.append(line)

    text = "\n".join(lines) + "\n"

    idx = find_safe_insert_after_imports(text)
    lines = text.splitlines()
    lines.insert(idx, import_line)

    print("Ensured v2 import.")
    return "\n".join(lines) + "\n"


def ensure_direct_url_fallback(text: str):
    marker = "AUTO_V2_DIRECT_ACCESS_START"

    if marker in text:
        return text

    block = f'''
# AUTO_V2_DIRECT_ACCESS_START
try:
    _v2_direct = st.query_params.get("v2", None)
    if isinstance(_v2_direct, list):
        _v2_direct = _v2_direct[0] if _v2_direct else None
    if str(_v2_direct) == "1":
        render_v2_app()
        st.stop()
except Exception:
    pass
# AUTO_V2_DIRECT_ACCESS_END

'''

    # Лучше после st.set_page_config, если есть.
    m = re.search(r"st\.set_page_config\s*\((?s:.*?)\)\s*", text)
    if m:
        text = text[:m.end()] + "\n" + block + text[m.end():]
        print("Added direct v2 URL fallback after st.set_page_config.")
        return text

    # Иначе перед первой функцией.
    m = re.search(r"(?m)^def\s+", text)
    if m:
        text = text[:m.start()] + block + text[m.start():]
        print("Added direct v2 URL fallback before first function.")
        return text

    idx = find_safe_insert_after_imports(text)
    lines = text.splitlines()
    lines[idx:idx] = block.strip().splitlines()
    print("Added direct v2 URL fallback after imports.")
    return "\n".join(lines) + "\n"


def ensure_v2_route(text: str):
    if "render_v2_app()" in text and "AUTO_V2_DIRECT_ACCESS_START" not in text:
        # Может быть уже route, но не факт. Не выходим.
        pass

    if f'page in ("{V2_PAGE}", "Новый интерфейс v2", "v2")' in text:
        return text

    patterns = [
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']🏠\s*Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\']Главная["\']\s*:',
        r'(?m)^(\s*)elif\s+page\s*==\s*["\'][^"\']+["\']\s*:',
    ]

    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            indent = m.group(1)
            route = f'{indent}elif page in ("{V2_PAGE}", "Новый интерфейс v2", "v2"):\n{indent}    render_v2_app()\n'
            text = text[:m.start()] + route + text[m.start():]
            print("Added v2 route.")
            return text

    print("Could not add normal v2 route. Direct URL fallback will work.")
    return text


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = ensure_import(text)
    text = force_add_v2_to_menu(text)
    text = ensure_v2_route(text)
    text = ensure_direct_url_fallback(text)

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    print("app.py syntax OK.")


def is_port_open(host="127.0.0.1", port=8501):
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except Exception:
        return False


def start_streamlit():
    if is_port_open():
        print("Streamlit already running.")
        webbrowser.open("http://localhost:8501/?v2=1")
        return

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_CONSOLE

    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=str(ROOT),
        creationflags=creationflags,
    )

    for _ in range(30):
        if is_port_open():
            print("Streamlit started.")
            webbrowser.open("http://localhost:8501/?v2=1")
            return
        time.sleep(0.5)

    print("Open manually: http://localhost:8501/?v2=1")


def main():
    print("=== Repair v2 visibility ===")

    ensure_v2_module()
    patch_app()

    print()
    print("Готово ✅")
    print()
    print("Проверь два варианта:")
    print("1. В левом меню должен появиться пункт: 🌟 Новый интерфейс v2")
    print("2. Если вдруг меню всё ещё не покажет пункт, открой прямую ссылку:")
    print("   http://localhost:8501/?v2=1")
    print()
    print("Запускаю приложение и открываю прямую ссылку v2...")
    print()

    start_streamlit()


if __name__ == "__main__":
    main()
