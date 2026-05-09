from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"


MAIN_CODE = r'''
def main():
    """
    Временно отключенная авторизация для активной разработки v2.

    Сейчас приложение сразу открывается без PIN.
    Пользователь по умолчанию: Мишка.

    Авторизацию вернём в конце, когда закончим дизайн, каталоги,
    фото, сканер и основную логику.
    """
    ensure_schema()
    seed_if_empty()

    if "user" not in st.session_state:
        st.session_state["user"] = "Мишка"

    st.session_state["authenticated"] = True

    render_app()
'''


SIDEBAR_CODE = r'''
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

        user = st.session_state.get("user", "Мишка")
        info = USERS.get(user, USERS["Мишка"])

        st.markdown(
            f"""
<div class="v2-card v2-card-soft" style="padding:14px;border-radius:18px;margin-top:10px;">
    <b>{info["emoji"]} Активный пользователь</b><br>
    <span style="color:#647067;">{user}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.caption("PIN и авторизация временно отключены до финальной сборки.")
'''


def backup(path: Path):
    backup_dir = ROOT / "backups" / f"disable_auth_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name

    if path.exists():
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


def remove_direct_auth_calls(text: str) -> str:
    """
    На всякий случай убираем отдельные вызовы require_auth(),
    если они вдруг были не только внутри main().
    """
    lines = []
    removed = 0

    for line in text.splitlines():
        stripped = line.strip()

        if stripped == "require_auth()":
            removed += 1
            continue

        lines.append(line)

    if removed:
        print(f"Removed direct require_auth() calls: {removed}")

    return "\n".join(lines) + "\n"


def ensure_no_login_default_problem(text: str) -> str:
    """
    Если где-то остались проверки authenticated до main,
    делаем безопасную инициализацию после импортов/st.set_page_config.
    """
    marker = "AUTO_AUTH_DISABLED_V2_START"

    if marker in text:
        return text

    block = '''
# AUTO_AUTH_DISABLED_V2_START
# Авторизация временно отключена на период разработки v2.
try:
    st.session_state["authenticated"] = True
    if "user" not in st.session_state:
        st.session_state["user"] = "Мишка"
except Exception:
    pass
# AUTO_AUTH_DISABLED_V2_END

'''

    m = re.search(r"st\.set_page_config\s*\((?s:.*?)\)\s*", text)

    if m:
        text = text[:m.end()] + "\n" + block + text[m.end():]
        print("Added auth-disabled bootstrap after st.set_page_config.")
        return text

    # fallback перед первой функцией
    m = re.search(r"(?m)^def\s+", text)

    if m:
        text = text[:m.start()] + block + text[m.start():]
        print("Added auth-disabled bootstrap before first function.")
        return text

    return block + text


def main():
    if not APP.exists():
        print("app.py not found")
        raise SystemExit(1)

    print("=== Disable auth temporarily for v2 development ===")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = remove_direct_auth_calls(text)
    text = replace_function(text, "render_sidebar", SIDEBAR_CODE)
    text = replace_function(text, "main", MAIN_CODE)
    text = ensure_no_login_default_problem(text)

    APP.write_text(text, encoding="utf-8")

    py_compile.compile(str(APP), doraise=True)
    print("app.py syntax OK ✅")

    print()
    print("Готово ✅")
    print("Авторизация и PIN временно отключены.")
    print("Приложение будет сразу открываться в новом интерфейсе.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
