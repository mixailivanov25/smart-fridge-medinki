from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
POLISH = ROOT / "ui_polish_v13_1.py"


POLISH_CODE = r'''
import streamlit as st


def apply_ui_polish_v13_1():
    """
    Дополнительная визуальная полировка v1.3.1:
    - убирает ощущение дублей иконок;
    - чинит тёмный текст на тёмных карточках;
    - улучшает mobile;
    - делает таблицы аккуратнее;
    - полирует sidebar.
    """
    st.markdown(
        """
<style>
/* ===== Global polish ===== */

html, body, [data-testid="stAppViewContainer"] {
    background: #f5f8f6 !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
}

/* Заголовки без обрезаний */
h1, h2, h3 {
    line-height: 1.18 !important;
    overflow: visible !important;
    padding-bottom: 0.12em !important;
    color: #0b2f20 !important;
    letter-spacing: -0.02em;
}

p {
    line-height: 1.55 !important;
}

/* Скрыть якоря Streamlit возле заголовков */
a[href^="#"] {
    display: none !important;
}

/* Скрыть служебные элементы Streamlit */
.stDeployButton,
[data-testid="stToolbar"] {
    display: none !important;
}

/* ===== Sidebar ===== */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f4fff8 0%, #ffffff 100%) !important;
    border-right: 1px solid rgba(18, 51, 33, 0.08) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.05rem !important;
    line-height: 1.22 !important;
}

/* Навигация более похожа на меню, а не на дешёвые radio */
[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 14px !important;
    padding: 8px 10px !important;
    margin-bottom: 4px !important;
    transition: background .15s ease, transform .15s ease !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(34, 197, 94, 0.10) !important;
    transform: translateX(1px);
}

/* Прячем кружки radio аккуратно, оставляем текст */
[data-testid="stSidebar"] input[type="radio"] {
    display: none !important;
}

/* ===== Buttons ===== */

div.stButton > button {
    border-radius: 18px !important;
    min-height: 48px !important;
    font-weight: 750 !important;
    border: 1px solid rgba(18, 51, 33, 0.12) !important;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.055) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}

div.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 12px 26px rgba(15, 23, 42, 0.10) !important;
}

/* ===== Cards ===== */

.medinki-hero,
.medinki-card,
.medinki-page-intro,
.medinki-soft,
.medinki-user-card,
.medinki-intro-card {
    overflow: visible !important;
}

/* Тёмные hero-карточки: весь текст белый */
.medinki-hero,
.medinki-hero * {
    color: white !important;
}

/* Если тёмный зелёный задан inline-стилем */
div[style*="background: linear-gradient"][style*="#123321"] *,
div[style*="background:linear-gradient"][style*="#123321"] *,
div[style*="background: linear-gradient"][style*="#246b43"] *,
div[style*="background:linear-gradient"][style*="#246b43"] * {
    color: white !important;
}

/* Новая карточка intro */
.medinki-intro-card {
    padding: 18px 22px;
    border-radius: 24px;
    background: rgba(255,255,255,.92);
    border: 1px solid rgba(18,51,33,.10);
    box-shadow: 0 10px 26px rgba(15,23,42,.055);
    margin: 12px 0 20px 0;
}

.medinki-intro-card h1 {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0 !important;
    font-size: clamp(1.75rem, 3.2vw, 2.7rem) !important;
}

.medinki-intro-icon {
    display: inline-flex;
    flex: 0 0 auto;
    font-size: 1.95rem;
    line-height: 1;
}

.medinki-intro-card p {
    margin: 10px 0 0 0 !important;
    color: #475569 !important;
    font-size: 1.04rem !important;
}

/* Таблицы аккуратнее */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-radius: 16px !important;
    overflow: auto !important;
}

/* Footer выглядит компактнее */
div[style*="версия v1."] {
    border-radius: 18px !important;
}

/* ===== Mobile ===== */

@media (max-width: 760px) {
    .block-container {
        padding-top: .85rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    h1 {
        font-size: 1.65rem !important;
        line-height: 1.18 !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.15rem !important;
    }

    .medinki-hero {
        padding: 20px !important;
        border-radius: 24px !important;
        margin-bottom: 14px !important;
    }

    .medinki-hero h1 {
        font-size: 1.8rem !important;
    }

    .medinki-card,
    .medinki-user-card {
        padding: 16px !important;
        border-radius: 22px !important;
    }

    .medinki-intro-card {
        padding: 16px !important;
        border-radius: 22px !important;
        margin: 10px 0 16px 0 !important;
    }

    .medinki-intro-card h1 {
        font-size: 1.55rem !important;
        gap: 9px !important;
    }

    .medinki-intro-icon {
        font-size: 1.45rem !important;
    }

    .medinki-intro-card p {
        font-size: .96rem !important;
    }

    div.stButton > button {
        min-height: 50px !important;
        font-size: .98rem !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        font-size: .82rem !important;
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
'''


PAGE_INTRO_CODE = r'''
def render_page_intro(title=None, subtitle=None, icon=None, *args, **kwargs):
    """
    Полированный intro-блок страницы v1.3.1.

    Главное отличие:
    - иконка теперь не отдельной строкой, а внутри заголовка;
    - на телефоне не создаёт визуальный дубль;
    - работает со старыми вызовами render_page_intro().
    """
    if title is None:
        title = kwargs.get("title", "Умный холодильник Мединки")

    if subtitle is None:
        subtitle = kwargs.get(
            "subtitle",
            "Холодильник, меню, рецепты, покупки и списание продуктов."
        )

    if icon is None:
        icon = kwargs.get("icon", "🥦")

    icon_html = ""
    if icon:
        icon_html = f'<span class="medinki-intro-icon">{icon}</span>'

    st.markdown(
        f"""
<div class="medinki-intro-card">
    <h1>{icon_html}<span>{title}</span></h1>
    <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )
'''


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"ui_polish_v13_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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


def write_polish_module():
    backup(POLISH)
    POLISH.write_text(POLISH_CODE, encoding="utf-8")
    compile_py(POLISH)
    print("ui_polish_v13_1.py written.")


def remove_duplicate_polish_calls(text: str) -> str:
    lines = []
    removed = 0

    for line in text.splitlines():
        if line.strip() == "apply_ui_polish_v13_1()":
            removed += 1
            continue
        lines.append(line)

    if removed:
        print(f"Removed duplicate apply_ui_polish_v13_1() calls: {removed}")

    return "\n".join(lines) + "\n"


def ensure_polish_import(text: str) -> str:
    # Убираем дубли импорта.
    lines = []
    removed = 0

    for line in text.splitlines():
        if line.strip() == "from ui_polish_v13_1 import apply_ui_polish_v13_1":
            removed += 1
            continue
        lines.append(line)

    text = "\n".join(lines) + "\n"

    insert_idx = find_safe_insert_after_imports(text)
    lines = text.splitlines()
    lines.insert(insert_idx, "from ui_polish_v13_1 import apply_ui_polish_v13_1")

    print("Ensured ui_polish_v13_1 import.")
    return "\n".join(lines) + "\n"


def ensure_polish_call(text: str) -> str:
    insert_pos = find_set_page_config_end(text)

    if insert_pos is not None:
        text = text[:insert_pos] + "apply_ui_polish_v13_1()\n" + text[insert_pos:]
        print("Inserted apply_ui_polish_v13_1() after st.set_page_config().")
        return text

    # Если set_page_config нет — перед первой функцией.
    m = re.search(r"(?m)^def\s+", text)
    if m:
        text = text[:m.start()] + "apply_ui_polish_v13_1()\n\n" + text[m.start():]
        print("Inserted apply_ui_polish_v13_1() before first function.")
        return text

    lines = text.splitlines()
    idx = find_safe_insert_after_imports(text)
    lines.insert(idx, "apply_ui_polish_v13_1()")
    print("Inserted apply_ui_polish_v13_1() after imports.")
    return "\n".join(lines) + "\n"


def replace_render_page_intro(text: str) -> str:
    pattern = r'(?ms)^def\s+render_page_intro\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'

    new_text, count = re.subn(
        pattern,
        PAGE_INTRO_CODE.strip() + "\n\n",
        text,
        count=1,
    )

    if count:
        print("render_page_intro() replaced with polished version.")
        return new_text

    lines = text.splitlines()
    idx = find_safe_insert_after_imports(text)
    lines[idx:idx] = [""] + PAGE_INTRO_CODE.strip().splitlines() + [""]
    print("render_page_intro() added.")
    return "\n".join(lines) + "\n"


def update_version_text(text: str) -> str:
    replacements = {
        "версия v1.2": "версия v1.3",
        "v1.2 · Иванов Михаил": "v1.3 · Иванов Михаил",
        "v1.2 • Иванов Михаил": "v1.3 • Иванов Михаил",
        "v1.2": "v1.3",
    }

    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)

    print("Version text updated to v1.3 where found.")
    return text


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = remove_duplicate_polish_calls(text)
    text = ensure_polish_import(text)
    text = replace_render_page_intro(text)
    text = update_version_text(text)
    text = ensure_polish_call(text)

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    print("app.py syntax OK.")


def main():
    print("=== UI polish v1.3.1 ===")

    write_polish_module()
    patch_app()

    print()
    print("Готово ✅")
    print("Исправлено:")
    print("- иконка intro больше не отдельной строкой;")
    print("- тёмные зелёные карточки получили белый текст;")
    print("- mobile-отступы и заголовки стали компактнее;")
    print("- sidebar стал аккуратнее;")
    print("- таблицы стали лучше на телефоне;")
    print("- версия в интерфейсе обновлена до v1.3.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
