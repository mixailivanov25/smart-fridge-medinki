from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"


CUSTOM_SIDEBAR_CODE = r"""
def custom_sidebar_html():
    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠", "Сегодня"),
        ("fridge", "🧊", "Холодильник"),
        ("scan", "📸", "Сканер"),
        ("recipes", "🍳", "Рецепты"),
        ("shopping", "🛒", "Покупки"),
        ("diary", "📔", "Дневник"),
        ("analytics", "📊", "Аналитика"),
        ("settings", "⚙️", "Настройки"),
    ]

    links = ""

    for key, emoji, label in items:
        active = "active" if current == key else ""
        links += f'''
<a class="v2-app-side-link {active}" href="?tab={key}" target="_self">
    <span class="v2-app-side-emoji">{emoji}</span>
    <span>{label}</span>
</a>
'''

    user = st.session_state.get("user", "Мишка")
    info = USERS.get(user, USERS["Мишка"])

    return f'''
<aside class="v2-app-sidebar">
    <div class="v2-app-brand">
        <div class="v2-app-brand-icon">🥦</div>
        <div>
            <div class="v2-app-brand-title">Умный холодильник</div>
            <div class="v2-app-brand-subtitle">Мединки</div>
        </div>
    </div>

    <div class="v2-app-nav">
        {links}
    </div>

    <div class="v2-app-user">
        <div class="v2-app-user-title">{info["emoji"]} {user}</div>
        <div class="v2-app-user-subtitle">активный пользователь</div>
    </div>

    <div class="v2-app-version">{APP_VERSION} · {DEVELOPER}</div>
</aside>
'''


def render_app_shell(content_func):
    shell = custom_sidebar_html()

    st.markdown(
        f'''
<div class="v2-app-shell">
    {shell}
    <main class="v2-app-main">
''',
        unsafe_allow_html=True,
    )

    content_func()

    st.markdown(
        '''
    </main>
</div>
''',
        unsafe_allow_html=True,
    )
"""


RENDER_APP_CODE = r"""
def render_app():
    apply_design()
    init_state()
    bottom_nav()

    tab = st.session_state.get("tab", "today")

    def _content():
        top_nav()

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

    render_app_shell(_content)
"""


CSS_APPEND = r"""
/* ===== Custom desktop app shell ===== */

[data-testid="stSidebar"] {
    display: none !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 100% !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-top: 0 !important;
}

.v2-app-shell {
    display: grid;
    grid-template-columns: 292px minmax(0, 1fr);
    min-height: 100vh;
}

.v2-app-sidebar {
    position: sticky;
    top: 0;
    height: 100vh;
    padding: 24px 20px;
    background:
        radial-gradient(circle at top left, rgba(34,197,94,.13), transparent 34%),
        linear-gradient(180deg, #f4fff8 0%, #ffffff 100%);
    border-right: 1px solid rgba(18,51,33,.08);
    display: flex;
    flex-direction: column;
    gap: 22px;
}

.v2-app-main {
    min-width: 0;
    padding: 26px 34px 7rem 34px;
}

.v2-app-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 8px 18px 8px;
    border-bottom: 1px solid rgba(18,51,33,.10);
}

.v2-app-brand-icon {
    font-size: 32px;
    line-height: 1;
}

.v2-app-brand-title {
    font-weight: 950;
    color: #10281c;
    font-size: 1.05rem;
    line-height: 1.05;
}

.v2-app-brand-subtitle {
    color: #647067;
    font-weight: 750;
    margin-top: 2px;
}

.v2-app-nav {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.v2-app-side-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 12px;
    border-radius: 17px;
    color: #123321 !important;
    text-decoration: none !important;
    font-weight: 850;
    border: 1px solid transparent;
    transition: all .15s ease;
}

.v2-app-side-link:hover {
    background: rgba(34,197,94,.12);
    border-color: rgba(34,197,94,.18);
    transform: translateX(2px);
}

.v2-app-side-link.active {
    background: linear-gradient(135deg, rgba(34,197,94,.22), rgba(240,253,244,.96));
    border-color: rgba(34,197,94,.30);
    box-shadow: 0 8px 20px rgba(15,23,42,.06);
}

.v2-app-side-emoji {
    font-size: 1.15rem;
    width: 24px;
    text-align: center;
}

.v2-app-user {
    margin-top: auto;
    padding: 14px;
    border-radius: 20px;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
    border: 1px solid rgba(34,197,94,.18);
    box-shadow: 0 10px 24px rgba(15,23,42,.055);
}

.v2-app-user-title {
    font-weight: 950;
    color: #10281c;
}

.v2-app-user-subtitle {
    color: #647067;
    font-size: .86rem;
    margin-top: 2px;
}

.v2-app-version {
    font-size: .78rem;
    color: #647067;
    font-weight: 700;
    padding: 0 4px;
}

@media (max-width: 900px) {
    .v2-app-shell {
        display: block;
    }

    .v2-app-sidebar {
        display: none;
    }

    .v2-app-main {
        padding: .95rem 1rem 7rem 1rem;
    }

    .block-container {
        padding: 0 !important;
    }
}
"""


def backup(path: Path):
    backup_dir = ROOT / "backups" / f"custom_sidebar_v2_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    if path.exists():
        target = backup_dir / path.name
        shutil.copy2(path, target)
        print(f"Backup saved: {target}")


def replace_function(text: str, func_name: str, code: str) -> str:
    pattern = rf'(?ms)^def\s+{re.escape(func_name)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'

    new_text, count = re.subn(
        pattern,
        code.strip() + "\n\n",
        text,
        count=1,
    )

    if count:
        print(f"Replaced {func_name}()")
        return new_text

    print(f"{func_name}() not found, appended.")
    return text.rstrip() + "\n\n" + code.strip() + "\n"


def insert_shell_functions(text: str) -> str:
    for fn in ["custom_sidebar_html", "render_app_shell"]:
        pattern = rf'(?ms)^def\s+{re.escape(fn)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'
        text = re.sub(pattern, "", text, count=1)

    m = re.search(r'(?m)^def\s+render_app\s*\(', text)

    if m:
        text = text[:m.start()] + CUSTOM_SIDEBAR_CODE.strip() + "\n\n" + text[m.start():]
    else:
        text += "\n\n" + CUSTOM_SIDEBAR_CODE.strip() + "\n"

    print("Inserted custom sidebar functions.")
    return text


def append_css_to_apply_design(text: str) -> str:
    if "v2-app-shell" in text:
        print("Custom sidebar CSS already present.")
        return text

    idx = text.find("</style>")

    if idx == -1:
        print("Could not find </style>, appending CSS separately.")
        extra = f'''
st.markdown("""
<style>
{CSS_APPEND}
</style>
""", unsafe_allow_html=True)
'''
        return text + "\n\n" + extra

    text = text[:idx] + "\n" + CSS_APPEND + "\n" + text[idx:]
    print("Inserted custom sidebar CSS.")
    return text


def main():
    if not APP.exists():
        print("app.py not found")
        raise SystemExit(1)

    print("=== Add custom desktop sidebar v2 fixed ===")

    backup(APP)

    text = APP.read_text(encoding="utf-8-sig").replace("\ufeff", "")

    text = append_css_to_apply_design(text)
    text = insert_shell_functions(text)
    text = replace_function(text, "render_app", RENDER_APP_CODE)

    APP.write_text(text, encoding="utf-8")

    py_compile.compile(str(APP), doraise=True)
    print("app.py syntax OK ✅")

    print()
    print("Готово ✅")
    print("Добавлена собственная левая панель v2.")
    print("Стандартный Streamlit sidebar скрыт.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()