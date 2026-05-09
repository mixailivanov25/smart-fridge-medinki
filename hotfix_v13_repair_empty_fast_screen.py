from pathlib import Path
import re
import shutil
import py_compile
from datetime import datetime

ROOT = Path(__file__).parent.resolve()
APP = ROOT / "app.py"


REQUEST_NAVIGATION_CODE = r'''
def request_navigation(target_page: str):
    """
    Безопасный переход между разделами.
    """
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
        "Стресс-тест": "🧪 Стресс-тест",
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
'''


FAST_ACTIONS_CODE = r'''
def render_fast_action_buttons():
    """
    Быстрые действия.
    """
    st.markdown("## ⚡ Быстрые действия")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("➕ Добавить еду", key="fast_add_food_repair_v13", use_container_width=True):
            request_navigation("📔 Дневник питания")

        if st.button("🧊 Холодильник", key="fast_fridge_repair_v13", use_container_width=True):
            request_navigation("🧊 Мой холодильник")

        if st.button("🗓️ Меню", key="fast_menu_repair_v13", use_container_width=True):
            request_navigation("🗓️ Меню на неделю")

        if st.button("📸 Фото и сканер", key="fast_photo_repair_v13", use_container_width=True):
            request_navigation("📸 Фото и сканер")

    with c2:
        if st.button("🛒 Добавить покупку", key="fast_shopping_repair_v13", use_container_width=True):
            request_navigation("🛒 Умные покупки")

        if st.button("⏰ Скоро испортится", key="fast_expiring_repair_v13", use_container_width=True):
            request_navigation("⏰ Скоро испортится")

        if st.button("📊 Аналитика", key="fast_analytics_repair_v13", use_container_width=True):
            request_navigation("📊 Аналитика")

        if st.button("🍳 Рецепты", key="fast_recipes_repair_v13", use_container_width=True):
            request_navigation("🍳 Рецепты")
'''


def clean_fast_screen_function(func_name: str) -> str:
    return f'''
def {func_name}():
    """
    Восстановленный быстрый экран v1.3.
    Без дублей, без кнопки обновления, с живыми часами и быстрыми действиями.
    """
    from datetime import datetime
    import streamlit.components.v1 as components

    st.markdown("""
<style>
.medinki-fast-hero {{
    padding: 26px 28px;
    border-radius: 30px;
    background: linear-gradient(135deg, #123321 0%, #246b43 100%);
    color: white;
    box-shadow: 0 18px 42px rgba(15, 23, 42, 0.14);
    margin-bottom: 22px;
}}

.medinki-fast-hero h1 {{
    color: white !important;
    margin: 0 0 10px 0;
    line-height: 1.18 !important;
}}

.medinki-fast-hero p {{
    margin: 0;
    opacity: .92;
    font-size: 1.06rem;
}}

.medinki-card-soft {{
    padding: 22px;
    border-radius: 26px;
    background: rgba(255,255,255,.92);
    border: 1px solid rgba(18, 51, 33, .10);
    box-shadow: 0 12px 30px rgba(15, 23, 42, .07);
    margin-bottom: 18px;
}}

.medinki-user-card {{
    padding: 20px;
    border-radius: 24px;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
    border: 1px solid rgba(34, 197, 94, .18);
    min-height: 150px;
}}

.medinki-pill {{
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    margin: 4px 6px 0 0;
    font-weight: 800;
    font-size: .86rem;
}}

.medinki-pill-blue {{
    background: #dbeafe;
    color: #1d4ed8;
}}

.medinki-pill-purple {{
    background: #ede9fe;
    color: #6d28d9;
}}

.medinki-pill-green {{
    background: #dcfce7;
    color: #15803d;
}}

@media (max-width: 760px) {{
    .medinki-fast-hero {{
        padding: 20px;
        border-radius: 24px;
    }}

    .medinki-fast-hero h1 {{
        font-size: 1.65rem !important;
    }}

    .medinki-card-soft {{
        padding: 16px;
        border-radius: 22px;
    }}
}}
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="medinki-fast-hero">
    <h1>🧊 Умный холодильник Мединки</h1>
    <p>Главное на сегодня: питание, покупки, холодильник, рецепты и фото-сканер.</p>
</div>
""", unsafe_allow_html=True)

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
function updateClock() {{
    const el = document.getElementById("medinki-clock");
    if (!el) return;
    const now = new Date();
    const text = now.toLocaleDateString("ru-RU", {{
        weekday: "long",
        day: "2-digit",
        month: "long"
    }}) + " · " + now.toLocaleTimeString("ru-RU");
    el.innerText = text;
}}
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
<div class="medinki-card-soft">
    <h2>👤 Активный пользователь: {{active_user}}</h2>
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

    render_fast_action_buttons()

    st.markdown("## 📌 Сегодня")
    st.info("Здесь будут меню на сегодня, срочные продукты и рекомендации. Фото-сканер доступен через быстрые действия.")
'''


def backup_file(path: Path):
    backup_dir = ROOT / "backups" / f"hotfix_v13_repair_empty_fast_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / path.name
    shutil.copy2(path, backup_path)
    print(f"Backup saved: {backup_path}")


def try_compile(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, e


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


def ensure_request_navigation(text: str) -> str:
    pattern = r'\n*def\s+request_navigation\s*\([^)]*\)\s*:\n.*?^\s*st\.rerun\(\)\s*\n?'
    new_text, count = re.subn(
        pattern,
        "\n\n" + REQUEST_NAVIGATION_CODE.strip() + "\n\n",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )

    if count:
        print(f"Replaced request_navigation(): {count}")
        return new_text

    lines = text.splitlines()
    insert_idx = find_safe_insert_after_imports(text)
    lines[insert_idx:insert_idx] = [""] + REQUEST_NAVIGATION_CODE.strip().splitlines() + [""]
    print("Inserted request_navigation()")
    return "\n".join(lines) + "\n"


def replace_function(text: str, func_name: str, new_func_code: str) -> tuple[str, bool]:
    pattern = rf'(?ms)^def\s+{re.escape(func_name)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'
    new_text, count = re.subn(pattern, new_func_code.strip() + "\n\n", text)

    if count:
        return new_text, True

    return text, False


def ensure_fast_actions(text: str) -> str:
    text, replaced = replace_function(text, "render_fast_action_buttons", FAST_ACTIONS_CODE)

    if replaced:
        print("Replaced render_fast_action_buttons()")
        return text

    text += "\n\n" + FAST_ACTIONS_CODE.strip() + "\n"
    print("Added render_fast_action_buttons()")
    return text


def def_line_info(line: str):
    m = re.match(r'^(\s*)def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*:\s*(#.*)?$', line)
    if not m:
        return None
    return len(m.group(1)), m.group(2)


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def find_empty_defs(text: str):
    lines = text.splitlines()
    empty = []

    for i, line in enumerate(lines):
        info = def_line_info(line)
        if not info:
            continue

        indent, name = info

        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
            j += 1

        if j >= len(lines):
            empty.append((i, name, indent))
            continue

        next_indent = line_indent(lines[j])

        if next_indent <= indent:
            empty.append((i, name, indent))

    return empty


def repair_empty_defs(text: str) -> tuple[str, list[str]]:
    lines = text.splitlines()
    empty = find_empty_defs(text)

    if not empty:
        print("No empty functions found.")
        return text, []

    fixed_names = []

    # Вставляем снизу вверх, чтобы индексы не съезжали.
    for i, name, indent in reversed(empty):
        fixed_names.append(name)

        lower = name.lower()
        is_fast_like = (
            "fast" in lower
            or "quick" in lower
            or "mobile" in lower
            or name in ["render_fast_screen", "render_quick_screen", "render_fast_page", "render_quick_page"]
        )

        body_indent = " " * (indent + 4)

        if is_fast_like and name.startswith("render_"):
            body = [
                body_indent + 'st.warning("Быстрый экран был автоматически восстановлен. Перезагрузите страницу, если видите это сообщение.")',
                body_indent + "render_fast_action_buttons()",
            ]
        else:
            body = [body_indent + "pass"]

        lines[i + 1:i + 1] = body
        print(f"Repaired empty function: {name}")

    return "\n".join(lines) + "\n", list(reversed(fixed_names))


def find_route_fast_screen_function(text: str):
    """
    Пытаемся понять, какая функция вызывается для страницы Быстрый экран.
    """
    m = re.search(
        r'(?s)page\s*(?:==|in)\s*[^:\n]*Быстрый экран[^:\n]*:\s*\n(?P<body>.*?)(?=\n\s*elif\s+page|\n\s*else\s*:|\n\s*if\s+page|\Z)',
        text,
    )

    if not m:
        return None

    body = m.group("body")

    candidates = re.findall(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(', body, flags=re.MULTILINE)

    ignore = {
        "st",
        "print",
        "len",
        "str",
        "int",
        "float",
        "list",
        "dict",
    }

    for c in candidates:
        if c not in ignore and c.startswith("render_"):
            return c

    return None


def replace_fast_screen_candidates(text: str, repaired_names: list[str]) -> str:
    candidates = [
        "render_fast_screen",
        "render_quick_screen",
        "render_fast_page",
        "render_quick_page",
        "render_mobile_fast_screen",
        "render_fast_mobile_screen",
        "render_quick_mobile_screen",
    ]

    route_func = find_route_fast_screen_function(text)
    if route_func:
        candidates.insert(0, route_func)

    for name in repaired_names:
        lower = name.lower()
        if name.startswith("render_") and ("fast" in lower or "quick" in lower or "mobile" in lower):
            candidates.insert(0, name)

    seen = set()
    ordered = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            ordered.append(c)

    replaced_any = False

    for name in ordered:
        if re.search(rf'(?m)^def\s+{re.escape(name)}\s*\(', text):
            text, replaced = replace_function(text, name, clean_fast_screen_function(name))
            if replaced:
                print(f"Replaced fast screen function with clean version: {name}")
                replaced_any = True
                break

    if not replaced_any:
        # Если функции быстрого экрана вообще не нашли — добавим render_fast_screen.
        text += "\n\n" + clean_fast_screen_function("render_fast_screen").strip() + "\n"
        print("Added clean render_fast_screen()")

    return text


def ensure_pending_navigation_block(text: str) -> str:
    if '"pending_navigation" in st.session_state' in text or "'pending_navigation' in st.session_state" in text:
        return text

    lines = text.splitlines()
    key_idx = None

    for i, line in enumerate(lines):
        if "main_navigation" in line and "key" in line:
            key_idx = i
            break

    if key_idx is None:
        print("WARNING: main_navigation widget not found.")
        return text

    start_idx = key_idx
    widget_markers = [
        "st.sidebar.radio",
        "st.sidebar.selectbox",
        "st.radio",
        "st.selectbox",
        "option_menu",
    ]

    for i in range(key_idx, max(-1, key_idx - 50), -1):
        if any(marker in lines[i] for marker in widget_markers):
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
    print("Inserted pending_navigation block before navigation widget.")
    return "\n".join(lines) + "\n"


def remove_refresh_button_blocks(text: str) -> str:
    """
    Аккуратно удаляем только сами блоки кнопки обновления, не тело всей функции.
    """
    lines = text.splitlines()
    out = []
    i = 0
    removed = 0

    while i < len(lines):
        line = lines[i]

        if "Обновить данные" in line or "🔄 Обновить данные" in line:
            base_indent = line_indent(line)

            # Если это строка if st.button(...), удаляем её вложенный блок.
            if "st.button" in line or line.strip().startswith("if "):
                removed += 1
                i += 1

                while i < len(lines):
                    if not lines[i].strip():
                        i += 1
                        continue

                    if line_indent(lines[i]) <= base_indent:
                        break

                    i += 1

                continue

            # Иначе удаляем только строку.
            removed += 1
            i += 1
            continue

        out.append(line)
        i += 1

    if removed:
        print(f"Removed refresh button lines/blocks: {removed}")

    return "\n".join(out) + "\n"


def main():
    if not APP.exists():
        print("app.py not found")
        return

    print("=== hotfix_v13_repair_empty_fast_screen.py ===")

    backup_file(APP)

    text = APP.read_text(encoding="utf-8")

    text = ensure_request_navigation(text)
    text = ensure_fast_actions(text)
    text = ensure_pending_navigation_block(text)

    # Сначала ремонтируем пустые функции, чтобы ушла IndentationError.
    text, repaired_names = repair_empty_defs(text)

    # Потом полностью заменяем быстрый экран на чистую версию.
    text = replace_fast_screen_candidates(text, repaired_names)

    # Аккуратно убираем кнопку обновления, если она ещё осталась.
    text = remove_refresh_button_blocks(text)

    APP.write_text(text, encoding="utf-8")

    ok, err = try_compile(APP)

    if ok:
        print()
        print("Готово ✅")
        print("app.py снова синтаксически корректен.")
        print("Быстрый экран восстановлен в чистом виде.")
        print()
        print("Теперь запусти:")
        print("python -m streamlit run app.py")
    else:
        print()
        print("Синтаксис всё ещё сломан ❌")
        print(err)
        print()
        print("Пришли, пожалуйста, строки app.py примерно 940-990.")


if __name__ == "__main__":
    main()