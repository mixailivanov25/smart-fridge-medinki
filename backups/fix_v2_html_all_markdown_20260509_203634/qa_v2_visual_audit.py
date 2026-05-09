from pathlib import Path
from datetime import datetime
import ast
import html
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
import py_compile

ROOT = Path.cwd()
APP = ROOT / "app.py"
SCREEN_DIR = ROOT / "qa_v2_screenshots"
REPORT = ROOT / "qa_v2_report.md"
CONTACT = ROOT / "qa_v2_contact_sheet.html"
URL = "http://localhost:8501"

PAGES = [
    ("today", "Сегодня"),
    ("fridge", "Холодильник"),
    ("scan", "Сканер"),
    ("recipes", "Рецепты"),
    ("shopping", "Покупки"),
    ("diary", "Дневник"),
    ("analytics", "Аналитика"),
    ("settings", "Настройки"),
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
    "This app has encountered an error",
]

RAW_HTML_PATTERNS = [
    "<div",
    "</div>",
    "<h1",
    "</h1>",
    "<p>",
    "</p>",
    "<span",
    "</span>",
    "class=",
    "unsafe_allow_html",
]


def log(msg):
    print(msg, flush=True)


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"qa_v2_visual_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    log(f"Backup saved: {target}")


def clean_bom(text: str) -> str:
    return text.replace("\ufeff", "")


def is_st_markdown_call(node):
    if not isinstance(node, ast.Call):
        return False

    func = node.func

    if isinstance(func, ast.Attribute):
        if func.attr != "markdown":
            return False

        if isinstance(func.value, ast.Name) and func.value.id == "st":
            return True

    return False


def get_static_string_from_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    if isinstance(node, ast.JoinedStr):
        parts = []

        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                parts.append("{}")

        return "".join(parts)

    return ""


def looks_like_html(s: str) -> bool:
    if not s:
        return False

    markers = [
        "<div",
        "<style",
        "<a ",
        "<span",
        "<h1",
        "<h2",
        "<h3",
        "<p",
        "<img",
        "</div>",
    ]

    return any(m in s for m in markers)


def has_unsafe_kw(node):
    for kw in node.keywords:
        if kw.arg == "unsafe_allow_html":
            return True
    return False


def auto_patch_unsafe_html_markdown():
    """
    Автоматически добавляет unsafe_allow_html=True в многострочные вызовы:
        st.markdown(\"\"\"<div>...</div>\"\"\")
    если там есть HTML.
    """
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8-sig")
    text = clean_bom(text)

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        log("app.py has syntax error before QA:")
        log(str(e))
        APP.write_text(text, encoding="utf-8")
        raise

    lines = text.splitlines()

    insertions = []
    skipped_single_line = []

    for node in ast.walk(tree):
        if not is_st_markdown_call(node):
            continue

        if has_unsafe_kw(node):
            continue

        if not node.args:
            continue

        first_arg_text = get_static_string_from_node(node.args[0])

        if not looks_like_html(first_arg_text):
            continue

        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            continue

        # Многострочные вызовы безопасно патчим вставкой перед закрывающей скобкой.
        if node.end_lineno > node.lineno:
            closing_idx = node.end_lineno - 1
            closing_line = lines[closing_idx]
            closing_indent = re.match(r"\s*", closing_line).group(0)
            kw_indent = closing_indent + "    "

            # Не вставляем, если рядом уже есть unsafe.
            block_text = "\n".join(lines[node.lineno - 1:node.end_lineno])
            if "unsafe_allow_html" not in block_text:
                insertions.append((closing_idx, kw_indent + "unsafe_allow_html=True,"))
        else:
            skipped_single_line.append(node.lineno)

    for idx, line in sorted(insertions, key=lambda x: x[0], reverse=True):
        lines.insert(idx, line)

    new_text = "\n".join(lines) + "\n"

    APP.write_text(new_text, encoding="utf-8")

    try:
        py_compile.compile(str(APP), doraise=True)
    except Exception:
        log("Patch caused syntax error, restoring backup is recommended.")
        raise

    log(f"Auto-patched st.markdown HTML blocks: {len(insertions)}")

    if skipped_single_line:
        log(f"Skipped one-line HTML markdown calls: {len(skipped_single_line)}")

    return len(insertions), skipped_single_line


def stop_streamlit_on_8501():
    """
    Пытается остановить процесс, который держит порт 8501.
    На Windows используем PowerShell Get-NetTCPConnection.
    """
    log("Trying to stop existing Streamlit on port 8501...")

    if os.name == "nt":
        cmd = r"""
$connections = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped process $pid on port 8501"
        } catch {}
    }
}
"""
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            cwd=str(ROOT),
            check=False,
        )
    else:
        subprocess.run("lsof -ti:8501 | xargs kill -9", shell=True, check=False)

    time.sleep(1.5)


def port_open(host="127.0.0.1", port=8501):
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except Exception:
        return False


def start_streamlit():
    stop_streamlit_on_8501()

    log("Starting Streamlit...")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_CONSOLE

    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=str(ROOT),
        creationflags=creationflags,
    )

    for _ in range(50):
        if port_open():
            log("Streamlit started.")
            return True
        time.sleep(0.5)

    log("Streamlit did not start in time.")
    return False


def install_playwright():
    try:
        import playwright  # noqa
        log("Playwright already installed.")
    except Exception:
        log("Installing Playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)

    log("Ensuring Chromium is installed...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False)


def safe_name(name):
    name = name.lower()
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-zа-я0-9_\-]+", "", name, flags=re.IGNORECASE)
    return name or "page"


def read_body_text(page):
    try:
        return page.locator("body").inner_text(timeout=7000)
    except Exception as e:
        return f"__BODY_READ_ERROR__ {e}"


def detect_issues(page, tab_key, label, mode):
    issues = []
    body = read_body_text(page)

    if "__BODY_READ_ERROR__" in body:
        issues.append(body)
        return issues

    stripped = body.strip()

    if len(stripped) < 40:
        issues.append("Page body is too short/possibly empty.")

    for pattern in ERROR_PATTERNS:
        if pattern in body:
            issues.append(f"Possible error text found: {pattern}")

    raw_hits = [p for p in RAW_HTML_PATTERNS if p in body]

    if raw_hits:
        issues.append(f"Raw HTML visible on page: {', '.join(raw_hits[:8])}")

    # Проверка авторизации, которую временно отключили.
    if "PIN" in body or "PIN-код" in body or "Войти" in body:
        issues.append("Auth/Login text visible, but auth should be disabled during v2 development.")

    # Проверка верхней навигации.
    try:
        top_count = page.locator(".v2-top-nav").count()
        if top_count == 0:
            issues.append("Top navigation .v2-top-nav not found.")
    except Exception as e:
        issues.append(f"Cannot check top nav: {e}")

    # Проверка нижней навигации на mobile.
    if mode == "mobile":
        try:
            bottom = page.locator(".v2-bottom-nav")
            if bottom.count() == 0:
                issues.append("Mobile bottom nav .v2-bottom-nav not found.")
            else:
                visible = bottom.first.is_visible()
                if not visible:
                    issues.append("Mobile bottom nav exists but is not visible.")
        except Exception as e:
            issues.append(f"Cannot check bottom nav: {e}")

    # Проверка базовых ссылок навигации.
    if mode == "desktop":
        for required in ["?tab=today", "?tab=fridge", "?tab=scan", "?tab=shopping"]:
            try:
                if page.locator(f'a[href="{required}"]').count() == 0:
                    issues.append(f"Navigation link missing: {required}")
            except Exception:
                pass

    return issues


def run_qa():
    from playwright.sync_api import sync_playwright

    SCREEN_DIR.mkdir(parents=True, exist_ok=True)

    report = []
    report.append("# QA v2 visual audit")
    report.append("")
    report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"URL: {URL}")
    report.append("")

    all_issues = []

    screenshots = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Desktop
        desktop = browser.new_context(
            viewport={"width": 1440, "height": 1100},
            device_scale_factor=1,
            is_mobile=False,
            locale="ru-RU",
        )

        dpage = desktop.new_page()

        # Mobile
        mobile = browser.new_context(
            viewport={"width": 390, "height": 900},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            locale="ru-RU",
        )

        mpage = mobile.new_page()

        for idx, (tab, label) in enumerate(PAGES, start=1):
            page_url = f"{URL}/?tab={tab}"

            log(f"Checking {label}: {page_url}")

            desktop_path = SCREEN_DIR / f"{idx:02d}_{safe_name(label)}_desktop.png"
            mobile_path = SCREEN_DIR / f"{idx:02d}_{safe_name(label)}_mobile.png"

            dpage.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            dpage.wait_for_timeout(2500)
            dpage.screenshot(path=str(desktop_path), full_page=True)

            desktop_issues = detect_issues(dpage, tab, label, "desktop")

            mpage.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            mpage.wait_for_timeout(2500)
            mpage.screenshot(path=str(mobile_path), full_page=True)

            mobile_issues = detect_issues(mpage, tab, label, "mobile")

            screenshots.append((label, desktop_path, mobile_path))

            page_issues = []
            page_issues.extend([f"Desktop: {x}" for x in desktop_issues])
            page_issues.extend([f"Mobile: {x}" for x in mobile_issues])

            report.append(f"## {idx:02d}. {label}")
            report.append("")
            report.append(f"- URL: `{page_url}`")
            report.append(f"- Desktop screenshot: `{desktop_path.relative_to(ROOT)}`")
            report.append(f"- Mobile screenshot: `{mobile_path.relative_to(ROOT)}`")

            if page_issues:
                report.append("- Issues:")
                for issue in page_issues:
                    report.append(f"  - {issue}")
                    all_issues.append((label, issue))
            else:
                report.append("- Issues: none")

            report.append("")

        browser.close()

    report.append("## Summary")
    report.append("")

    if all_issues:
        report.append(f"Found issues: {len(all_issues)}")
        report.append("")
        for label, issue in all_issues:
            report.append(f"- **{label}**: {issue}")
    else:
        report.append("No critical visual/runtime issues detected.")

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    write_contact_sheet(screenshots, all_issues)

    return all_issues


def write_contact_sheet(screenshots, issues):
    cards = []

    issue_map = {}
    for label, issue in issues:
        issue_map.setdefault(label, []).append(issue)

    for label, desktop_path, mobile_path in screenshots:
        issues_html = ""

        if label in issue_map:
            issues_html = "<ul>" + "".join(
                f"<li>{html.escape(x)}</li>" for x in issue_map[label]
            ) + "</ul>"
        else:
            issues_html = "<p class='ok'>No issues detected</p>"

        cards.append(
            f"""
<section class="page">
    <h2>{html.escape(label)}</h2>
    <div class="issues">{issues_html}</div>
    <div class="shots">
        <div>
            <h3>Desktop</h3>
            <img src="{desktop_path.as_posix()}" />
        </div>
        <div>
            <h3>Mobile</h3>
            <img src="{mobile_path.as_posix()}" />
        </div>
    </div>
</section>
"""
        )

    content = f"""
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>QA v2 visual contact sheet</title>
<style>
body {{
    margin: 0;
    padding: 28px;
    background: #f5f8f6;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: #10281c;
}}
h1 {{
    font-size: 34px;
    margin-bottom: 8px;
}}
.page {{
    background: white;
    border: 1px solid rgba(18,51,33,.12);
    border-radius: 24px;
    padding: 22px;
    margin: 22px 0;
    box-shadow: 0 12px 32px rgba(15,23,42,.08);
}}
.shots {{
    display: grid;
    grid-template-columns: 1fr 360px;
    gap: 18px;
    align-items: start;
}}
img {{
    width: 100%;
    border-radius: 16px;
    border: 1px solid rgba(18,51,33,.12);
}}
.ok {{
    color: #166534;
    font-weight: 800;
}}
li {{
    color: #b91c1c;
    font-weight: 700;
    margin: 4px 0;
}}
@media (max-width: 1000px) {{
    .shots {{
        grid-template-columns: 1fr;
    }}
}}
</style>
</head>
<body>
<h1>QA v2 visual contact sheet</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
{''.join(cards)}
</body>
</html>
"""

    CONTACT.write_text(content, encoding="utf-8")


def main():
    log("=== QA v2 visual audit ===")

    patched, skipped = auto_patch_unsafe_html_markdown()

    install_playwright()

    start_streamlit()

    time.sleep(3)

    issues = run_qa()

    log("")
    log(f"Report: {REPORT}")
    log(f"Screenshots: {SCREEN_DIR}")
    log(f"Contact sheet: {CONTACT}")

    if issues:
        log("")
        log(f"Found issues: {len(issues)}")
        log("Open qa_v2_report.md and qa_v2_contact_sheet.html")
    else:
        log("")
        log("No critical issues detected.")

    webbrowser.open(str(CONTACT))
    webbrowser.open(str(REPORT))


if __name__ == "__main__":
    main()
