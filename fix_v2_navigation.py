from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"


NAV_CODE = r'''
def nav_url(tab):
    return f"?tab={tab}"


def set_tab(tab):
    st.session_state["tab"] = tab
    try:
        st.query_params["tab"] = tab
    except Exception:
        pass
    st.rerun()


def render_nav_styles():
    st.markdown(
        """
<style>
.v2-top-nav {
    position: sticky;
    top: 0;
    z-index: 9999;
    display: grid;
    grid-template-columns: repeat(8, minmax(0, 1fr));
    gap: 8px;
    padding: 10px;
    margin: 0 0 18px 0;
    border-radius: 24px;
    background: rgba(255,255,255,.86);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 14px 36px rgba(15,23,42,.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.v2-top-nav a,
.v2-sidebar-link,
.v2-bottom-nav a,
.v2-action-link {
    text-decoration: none !important;
}

.v2-top-nav a {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    padding: 9px 10px;
    border-radius: 17px;
    color: #123321 !important;
    font-weight: 900;
    font-size: .92rem;
    transition: all .15s ease;
    border: 1px solid transparent;
}

.v2-top-nav a:hover {
    background: rgba(34,197,94,.13);
    border-color: rgba(34,197,94,.20);
    transform: translateY(-1px);
}

.v2-top-nav a.active {
    background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(240,253,244,.96));
    border-color: rgba(34,197,94,.30);
    box-shadow: 0 8px 20px rgba(15,23,42,.07);
}

.v2-sidebar-link {
    display: block;
    padding: 10px 12px;
    margin: 5px 0;
    border-radius: 16px;
    color: #123321 !important;
    font-weight: 850;
    border: 1px solid transparent;
}

.v2-sidebar-link:hover {
    background: rgba(34,197,94,.12);
    border-color: rgba(34,197,94,.18);
}

.v2-sidebar-link.active {
    background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(240,253,244,.96));
    border-color: rgba(34,197,94,.30);
    box-shadow: 0 8px 20px rgba(15,23,42,.06);
}

.v2-action-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin: 10px 0 26px 0;
}

.v2-action-link {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 54px;
    border-radius: 20px;
    color: #123321 !important;
    font-weight: 900;
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(18,51,33,.12);
    box-shadow: 0 10px 24px rgba(15,23,42,.06);
}

.v2-action-link:hover {
    background: rgba(34,197,94,.11);
    transform: translateY(-1px);
}

.v2-bottom-nav {
    display: none;
}

@media (max-width: 900px) {
    .v2-top-nav {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        overflow-x: auto;
        position: relative;
        top: auto;
    }

    .v2-top-nav a {
        font-size: .8rem;
        min-height: 42px;
        white-space: nowrap;
    }

    .v2-action-grid {
        grid-template-columns: 1fr 1fr;
        gap: 10px;
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
        background: rgba(255,255,255,.96);
        border: 1px solid rgba(18,51,33,.12);
        box-shadow: 0 18px 48px rgba(15,23,42,.22);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        gap: 6px;
    }

    .v2-bottom-nav a {
        color: #123321 !important;
        border-radius: 18px;
        padding: 8px 4px 7px 4px;
        min-height: 48px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2px;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-weight: 900;
        font-size: 10px;
        line-height: 1.05;
    }

    .v2-bottom-nav a.active {
        background: rgba(34,197,94,.18);
    }

    .v2-bottom-nav .emoji {
        font-size: 21px;
        line-height: 1;
    }
}
</style>
""",
        unsafe_allow_html=True,
    )


def render_top_nav():
    render_nav_styles()

    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠 Сегодня"),
        ("fridge", "🧊 Холодильник"),
        ("scan", "📸 Сканер"),
        ("recipes", "🍳 Рецепты"),
        ("shopping", "🛒 Покупки"),
        ("diary", "📔 Дневник"),
        ("analytics", "📊 Аналитика"),
        ("settings", "⚙️ Настройки"),
    ]

    links = []

    for key, label in items:
        active = "active" if current == key else ""
        links.append(f'<a class="{active}" href="?tab={key}" target="_self">{label}</a>')

    st.markdown(
        f"""
<div class="v2-top-nav">
    {''.join(links)}
</div>
""",
        unsafe_allow_html=True,
    )


def bottom_nav():
    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠", "Сегодня"),
        ("fridge", "🧊", "Холод."),
        ("scan", "📸", "Сканер"),
        ("recipes", "🍳", "Рецепты"),
        ("shopping", "🛒", "Покупки"),
    ]

    links = []

    for key, emoji, label in items:
        active = "active" if current == key else ""
        links.append(
            f'<a class="{active}" href="?tab={key}" target="_self"><span class="emoji">{emoji}</span><span>{label}</span></a>'
        )

    st.markdown(
        f"""
<div class="v2-bottom-nav">
    {''.join(links)}
</div>
""",
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🥦 Умный холодильник")
        st.caption(f"{APP_VERSION} · {DEVELOPER}")
        st.markdown("---")

        current = st.session_state.get("tab", "today")

        items = [
            ("today", "🏠 Сегодня"),
            ("fridge", "🧊 Холодильник"),
            ("scan", "📸 Сканер"),
            ("recipes", "🍳 Рецепты"),
            ("shopping", "🛒 Покупки"),
            ("diary", "📔 Дневник"),
            ("analytics", "📊 Аналитика"),
            ("settings", "⚙️ Настройки"),
        ]

        html = ""

        for key, label in items:
            active = "active" if current == key else ""
            html += f'<a class="v2-sidebar-link {active}" href="?tab={key}" target="_self">{label}</a>'

        st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")

        if "user" in st.session_state:
            user = st.session_state["user"]
            st.success(f"{USERS[user]['emoji']} {user}")

            if st.button("Выйти", use_container_width=True):
                st.session_state.pop("authenticated", None)
                st.session_state.pop("user", None)
                st.rerun()


def render_action_links():
    st.markdown(
        """
<div class="v2-action-grid">
    <a class="v2-action-link" href="?tab=scan" target="_self">📸 Сканировать</a>
    <a class="v2-action-link" href="?tab=fridge" target="_self">🧊 Холодильник</a>
    <a class="v2-action-link" href="?tab=recipes" target="_self">🍳 Рецепты</a>
    <a class="v2-action-link" href="?tab=shopping" target="_self">🛒 Покупки</a>
</div>
""",
        unsafe_allow_html=True,
    )
'''


RENDER_APP_CODE = r'''
def render_app():
    apply_design()
    init_tab()
    bottom_nav()
    render_sidebar()
    render_top_nav()

    tab = st.session_state.get("tab", "today")

    if tab == "fridge":
        page_fridge()
    elif tab == "scan":
        page_scan()
    elif tab == "recipes":
        page_recipes()
    elif tab == "shopping":
        page_shopping()
    elif tab == "diary":
        page_diary()
    elif tab == "analytics":
        page_analytics()
    elif tab == "settings":
        page_settings()
    else:
        page_today()
'''


def backup(path: Path):
    backup_dir = ROOT / "backups" / f"fix_v2_navigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def replace_function(text: str, name: str, code: str) -> str:
    pattern = rf'(?ms)^def\s+{re.escape(name)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|\Z)'
    new_text, count = re.subn(pattern, code.strip() + "\n\n", text, count=1)

    if count:
        print(f"Replaced {name}()")
        return new_text

    print(f"Added {name}()")
    return text + "\n\n" + code.strip() + "\n"


def patch_page_today_actions(text: str) -> str:
    """
    Заменяем блок быстрых кнопок в page_today на HTML-ссылки.
    Если точечно не получится — просто добавим render_action_links()
    после заголовка '## ⚡ Быстрые действия'.
    """
    if "render_action_links()" in text:
        return text

    needle = 'st.markdown("## ⚡ Быстрые действия")'

    if needle in text:
        text = text.replace(
            needle,
            'st.markdown("## ⚡ Быстрые действия")\n\n    render_action_links()',
            1,
        )
        print("Inserted action links into page_today()")
    else:
        print("Could not find quick actions heading")

    return text


def main():
    if not APP.exists():
        print("app.py not found")
        raise SystemExit(1)

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    # Удаляем старые версии функций и добавляем новые.
    for fn in ["nav_url", "set_tab", "render_nav_styles", "render_top_nav", "bottom_nav", "render_sidebar", "render_action_links"]:
        pattern = rf'(?ms)^def\s+{re.escape(fn)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|\Z)'
        text = re.sub(pattern, "", text, count=1)

    # Вставляем NAV_CODE перед render_app или перед main.
    m = re.search(r'(?m)^def\s+render_app\s*\(', text)
    if m:
        text = text[:m.start()] + NAV_CODE.strip() + "\n\n" + text[m.start():]
    else:
        m = re.search(r'(?m)^def\s+main\s*\(', text)
        if m:
            text = text[:m.start()] + NAV_CODE.strip() + "\n\n" + text[m.start():]
        else:
            text += "\n\n" + NAV_CODE.strip() + "\n"

    text = replace_function(text, "render_app", RENDER_APP_CODE)
    text = patch_page_today_actions(text)

    APP.write_text(text, encoding="utf-8")

    py_compile.compile(str(APP), doraise=True)
    print("app.py syntax OK ✅")

    print()
    print("Готово ✅")
    print("Навигация заменена на кликабельные ссылки.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
