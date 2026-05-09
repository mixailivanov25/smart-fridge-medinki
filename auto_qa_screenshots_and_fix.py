from pathlib import Path
from datetime import datetime
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import py_compile
import webbrowser

ROOT = Path.cwd()
APP = ROOT / "app.py"
VISUAL_FIX = ROOT / "qa_visual_fix_v13.py"
SCREEN_DIR = ROOT / "qa_screenshots_v13"
REPORT = ROOT / "qa_report_v13.md"
URL = "http://localhost:8501"


VISUAL_FIX_CODE = r'''
import streamlit as st


def apply_qa_visual_fix_v13():
    """
    Safe visual QA fix:
    - не ломает бизнес-логику;
    - чинит обрезание заголовков;
    - улучшает sidebar;
    - прячет лишние Streamlit-элементы;
    - делает кнопки и карточки аккуратнее.
    """
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #f5f8f6 !important;
}

.block-container {
    max-width: 1320px !important;
    padding-top: 1.35rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
}

h1, h2, h3 {
    line-height: 1.22 !important;
    overflow: visible !important;
    padding-bottom: 0.15em !important;
    color: #123321 !important;
    word-break: normal !important;
}

p, div, span, label {
    word-break: normal !important;
}

a[href^="#"] {
    display: none !important;
}

.stDeployButton,
[data-testid="stToolbar"] {
    display: none !important;
}

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
    font-size: 1.12rem !important;
    line-height: 1.25 !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
    padding: 8px 10px !important;
    border-radius: 14px !important;
    margin-bottom: 3px !important;
    transition: background .15s ease !important;
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

.medinki-hero,
.medinki-card,
.medinki-page-intro,
.medinki-soft,
.medinki-user-card {
    overflow: visible !important;
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
'''


PAGES = [
    "Быстрый экран",
    "Фото и сканер",
    "Главная",
    "Семейный режим",
    "Сегодня",
    "Дневник питания",
    "Умные покупки",
    "Аналитика",
    "Мои рецепты",
    "Мой холодильник",
    "Добавить продукты",
    "Рецепты",
    "Каталог блюд",
    "Меню на неделю",
    "Список покупок",
    "Питание и цели",
    "Любимые блюда",
    "История",
    "Списания",
    "Демо-режим",
]

ERROR_PATTERNS = [
    "Traceback",
    "StreamlitAPIException",
    "SyntaxError",
    "IndentationError",
    "TypeError",
    "NameError",
    "ModuleNotFoundError",
    "ImportError",
    "OperationalError",
    "ProgrammingError",
    "Exception:",
    "Error:",
]

NOISY_PATTERNS = [
    "Подсказка для первого входа",
    "Быстро заполнить демо",
    "Откройте ссылку на телефоне",
    "Обновить данные",
    "Показать второго пользователя",
]


def log(msg):
    print(msg, flush=True)


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"qa_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    log(f"Backup saved: {target}")


def compile_py(path: Path):
    py_compile.compile(str(path), doraise=True)


def write_visual_fix_module():
    backup(VISUAL_FIX)
    VISUAL_FIX.write_text(VISUAL_FIX_CODE, encoding="utf-8")
    compile_py(VISUAL_FIX)
    log("qa_visual_fix_v13.py written.")


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


def patch_app_visual_fix():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    if "from qa_visual_fix_v13 import apply_qa_visual_fix_v13" not in text:
        lines = text.splitlines()
        idx = find_safe_insert_after_imports(text)
        lines.insert(idx, "from qa_visual_fix_v13 import apply_qa_visual_fix_v13")
        text = "\n".join(lines) + "\n"
        log("Added qa_visual_fix_v13 import.")

    if "apply_qa_visual_fix_v13()" not in text:
        m = re.search(r"st\.set_page_config\s*\((?s:.*?)\)\s*", text)

        if m:
            text = text[:m.end()] + "\napply_qa_visual_fix_v13()\n" + text[m.end():]
            log("Added apply_qa_visual_fix_v13() after st.set_page_config.")
        else:
            lines = text.splitlines()
            idx = find_safe_insert_after_imports(text)
            lines.insert(idx + 1, "apply_qa_visual_fix_v13()")
            text = "\n".join(lines) + "\n"
            log("Added apply_qa_visual_fix_v13() after imports.")

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    log("app.py syntax OK after visual fix.")


def install_playwright():
    try:
        import playwright  # noqa
        log("Playwright already installed.")
    except Exception:
        log("Installing Playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)

    log("Installing Chromium for Playwright if needed...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)


def port_open(host="127.0.0.1", port=8501):
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except Exception:
        return False


def start_streamlit():
    if port_open():
        log("Streamlit already running.")
        return None

    log("Starting Streamlit...")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_CONSOLE

    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=str(ROOT),
        creationflags=creationflags,
    )

    for _ in range(60):
        if port_open():
            log("Streamlit started.")
            return proc
        time.sleep(0.5)

    log("Streamlit did not start in time.")
    return proc


def safe_name(name: str):
    name = name.lower()
    repl = {
        " ": "_",
        "/": "_",
        "\\": "_",
        ":": "_",
        "?": "",
        "*": "",
        '"': "",
        "<": "",
        ">": "",
        "|": "",
    }
    for a, b in repl.items():
        name = name.replace(a, b)

    # Убираем emoji и прочее, оставляем буквы/цифры/_/-
    name = re.sub(r"[^a-zа-я0-9_\-]+", "", name, flags=re.IGNORECASE)
    return name.strip("_") or "page"


def try_login(page):
    """
    Пытаемся войти стандартным PIN.
    Если уже вошли — ничего не делаем.
    """
    try:
        body = page.locator("body").inner_text(timeout=3000)
    except Exception:
        return

    if "PIN" not in body and "Войти" not in body and "Вход" not in body:
        return

    log("Login screen detected, trying default PIN...")

    try:
        # password или обычный input
        inputs = page.locator("input")
        count = inputs.count()

        if count:
            # Обычно PIN-поле последнее.
            inputs.nth(count - 1).fill("1111")

        # Нажать Войти
        candidates = [
            page.get_by_role("button", name=re.compile("Войти", re.IGNORECASE)),
            page.get_by_text("Войти", exact=False),
        ]

        clicked = False
        for loc in candidates:
            try:
                loc.first.click(timeout=3000)
                clicked = True
                break
            except Exception:
                pass

        if clicked:
            page.wait_for_timeout(2500)
            log("Login attempt done.")
        else:
            log("Could not click login button.")
    except Exception as e:
        log(f"Login attempt failed: {e}")


def click_page(page, page_name: str):
    """
    Пытается кликнуть пункт навигации в sidebar.
    Возвращает True/False.
    """
    selectors = [
        '[data-testid="stSidebar"]',
        'body',
    ]

    for sel in selectors:
        try:
            area = page.locator(sel)
            loc = area.get_by_text(page_name, exact=False)
            if loc.count() > 0:
                loc.first.click(timeout=5000)
                page.wait_for_timeout(1800)
                return True
        except Exception:
            pass

    return False


def collect_issues(page, page_name, mode):
    issues = []

    try:
        body = page.locator("body").inner_text(timeout=5000)
    except Exception as e:
        return [f"Cannot read body text: {e}"]

    for pattern in ERROR_PATTERNS:
        if pattern in body:
            issues.append(f"Possible error text found: {pattern}")

    for pattern in NOISY_PATTERNS:
        if pattern in body:
            issues.append(f"Noisy old UI text found: {pattern}")

    if page_name == "Быстрый экран":
        count = body.count("Быстрый экран")
        if count > 2:
            issues.append(f"Repeated 'Быстрый экран' text count: {count}")

    if len(body.strip()) < 50:
        issues.append("Page body looks too short/empty.")

    return issues


def run_qa():
    from playwright.sync_api import sync_playwright

    SCREEN_DIR.mkdir(parents=True, exist_ok=True)

    report_lines = []
    report_lines.append("# QA report v1.3")
    report_lines.append("")
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append(f"URL: {URL}")
    report_lines.append("")

    all_issues = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            viewport={"width": 1440, "height": 1100},
            device_scale_factor=1,
            is_mobile=False,
            locale="ru-RU",
        )

        page = context.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        try_login(page)

        # Скрин входа/первого экрана
        page.screenshot(path=str(SCREEN_DIR / "00_initial_desktop.png"), full_page=True)

        report_lines.append("## Pages")
        report_lines.append("")

        for idx, page_name in enumerate(PAGES, start=1):
            log(f"Checking page: {page_name}")

            # Всегда возвращаем desktop viewport перед кликом по sidebar.
            page.set_viewport_size({"width": 1440, "height": 1100})
            page.wait_for_timeout(500)

            clicked = click_page(page, page_name)

            desktop_file = SCREEN_DIR / f"{idx:02d}_{safe_name(page_name)}_desktop.png"
            mobile_file = SCREEN_DIR / f"{idx:02d}_{safe_name(page_name)}_mobile.png"

            page.screenshot(path=str(desktop_file), full_page=True)
            desktop_issues = collect_issues(page, page_name, "desktop")

            page.set_viewport_size({"width": 390, "height": 900})
            page.wait_for_timeout(900)
            page.screenshot(path=str(mobile_file), full_page=True)
            mobile_issues = collect_issues(page, page_name, "mobile")

            page_issues = []
            if not clicked:
                page_issues.append("Could not click/open page from navigation.")

            page_issues.extend([f"Desktop: {x}" for x in desktop_issues])
            page_issues.extend([f"Mobile: {x}" for x in mobile_issues])

            report_lines.append(f"### {idx:02d}. {page_name}")
            report_lines.append("")
            report_lines.append(f"- Opened from navigation: {'yes' if clicked else 'no'}")
            report_lines.append(f"- Desktop screenshot: `{desktop_file.relative_to(ROOT)}`")
            report_lines.append(f"- Mobile screenshot: `{mobile_file.relative_to(ROOT)}`")

            if page_issues:
                report_lines.append("- Issues:")
                for issue in page_issues:
                    report_lines.append(f"  - {issue}")
                    all_issues.append((page_name, issue))
            else:
                report_lines.append("- Issues: none")

            report_lines.append("")

        browser.close()

    report_lines.append("## Summary")
    report_lines.append("")

    if all_issues:
        report_lines.append(f"Found issues: {len(all_issues)}")
        report_lines.append("")
        for page_name, issue in all_issues:
            report_lines.append(f"- **{page_name}**: {issue}")
    else:
        report_lines.append("No critical issues detected by automated QA.")

    REPORT.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    log("")
    log(f"QA report saved: {REPORT}")
    log(f"Screenshots saved: {SCREEN_DIR}")

    return all_issues


def main():
    log("=== Auto QA screenshots and safe UI fix v1.3 ===")

    write_visual_fix_module()
    patch_app_visual_fix()
    install_playwright()
    start_streamlit()

    # Даём приложению чуть прогреться.
    time.sleep(3)

    issues = run_qa()

    log("")
    if issues:
        log(f"QA completed with issues: {len(issues)}")
        log("Open qa_report_v13.md and qa_screenshots_v13.")
    else:
        log("QA completed without critical issues.")

    webbrowser.open(URL)
    webbrowser.open(str(REPORT))


if __name__ == "__main__":
    main()
