from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
QA = ROOT / "qa_v2_visual_audit.py"


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"fix_v2_html_all_markdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def find_matching_paren(text: str, open_idx: int):
    depth = 0
    in_string = None
    triple = False
    escape = False

    i = open_idx

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
                return i

        i += 1

    return -1


def line_indent_at(text: str, idx: int):
    line_start = text.rfind("\n", 0, idx) + 1
    line = text[line_start:idx]
    return re.match(r"\s*", line).group(0)


def add_unsafe_to_call(text: str, call_start: int, close_idx: int):
    """
    Добавляет unsafe_allow_html=True перед закрывающей скобкой вызова.
    """
    segment = text[call_start:close_idx + 1]

    if "unsafe_allow_html" in segment:
        segment = segment.replace("unsafe_allow_html=False", "unsafe_allow_html=True")
        return text[:call_start] + segment + text[close_idx + 1:], 0

    # Ищем последний значимый символ перед закрывающей скобкой.
    j = close_idx - 1
    while j > call_start and text[j].isspace():
        j -= 1

    need_comma = text[j] != ","
    indent = line_indent_at(text, close_idx)

    if need_comma:
        insertion = f",\n{indent}    unsafe_allow_html=True,"
    else:
        insertion = f"\n{indent}    unsafe_allow_html=True,"

    return text[:close_idx] + insertion + text[close_idx:], 1


def patch_all_markdown_unsafe(text: str):
    """
    Жёстко добавляет unsafe_allow_html=True ко всем st.markdown(...).

    Это безопасно для нашего случая, потому что приложение само генерирует HTML-карточки.
    Зато полностью убирает проблему, когда <div> и <span> видны текстом.
    """
    target = "st.markdown"
    patches = []

    pos = 0

    while True:
        idx = text.find(target, pos)

        if idx == -1:
            break

        paren = text.find("(", idx + len(target))

        if paren == -1:
            break

        # Проверяем, что между st.markdown и ( нет мусора.
        between = text[idx + len(target):paren].strip()
        if between:
            pos = idx + len(target)
            continue

        close = find_matching_paren(text, paren)

        if close == -1:
            pos = idx + len(target)
            continue

        patches.append((idx, close))
        pos = close + 1

    added = 0

    for start, close in reversed(patches):
        text, delta = add_unsafe_to_call(text, start, close)
        added += delta

    return text, added, len(patches)


def patch_html_st_write(text: str):
    """
    Если где-то HTML случайно выводится через st.write("<div..."),
    заменяем такие вызовы на st.markdown(..., unsafe_allow_html=True).
    """
    markers = ["<div", "<span", "<p", "<h1", "<h2", "<h3", "<a ", "<style"]

    target = "st.write"
    patches = []

    pos = 0

    while True:
        idx = text.find(target, pos)

        if idx == -1:
            break

        paren = text.find("(", idx + len(target))

        if paren == -1:
            break

        between = text[idx + len(target):paren].strip()
        if between:
            pos = idx + len(target)
            continue

        close = find_matching_paren(text, paren)

        if close == -1:
            pos = idx + len(target)
            continue

        segment = text[idx:close + 1]

        if any(m in segment for m in markers):
            patches.append((idx, close))

        pos = close + 1

    changed = 0

    for start, close in reversed(patches):
        segment = text[start:close + 1]
        segment = segment.replace("st.write", "st.markdown", 1)

        text = text[:start] + segment + text[close + 1:]
        new_close = start + len(segment) - 1
        text, delta = add_unsafe_to_call(text, start, new_close)
        changed += 1

    return text, changed


def remove_visible_pin_text(text: str):
    """
    Убирает видимую подсказку про PIN/авторизацию из sidebar.
    Сами старые функции авторизации могут остаться в файле, но не должны быть видны.
    """
    lines = []
    removed = 0

    noisy_parts = [
        "PIN и авторизация временно отключены",
        "PIN временно отключ",
        "PIN and auth",
        "Авторизация временно отключ",
    ]

    for line in text.splitlines():
        if any(part in line for part in noisy_parts):
            removed += 1
            continue
        lines.append(line)

    print(f"Removed visible PIN/auth text lines: {removed}")
    return "\n".join(lines) + "\n"


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")

    text, added, total = patch_all_markdown_unsafe(text)
    text, write_changed = patch_html_st_write(text)
    text = remove_visible_pin_text(text)

    APP.write_text(text, encoding="utf-8")

    py_compile.compile(str(APP), doraise=True)

    print("app.py syntax OK ✅")
    print(f"st.markdown calls found: {total}")
    print(f"unsafe_allow_html added: {added}")
    print(f"st.write HTML calls converted: {write_changed}")


def patch_qa_pid_bug():
    """
    Чиним баг в QA-скрипте:
    PowerShell переменная $PID системная, поэтому foreach ($pid in ...)
    на Windows ругается.
    """
    if not QA.exists():
        print("qa_v2_visual_audit.py not found, skip QA patch.")
        return

    backup(QA)

    text = QA.read_text(encoding="utf-8-sig")

    before = text

    text = text.replace("foreach ($pid in $pids)", "foreach ($processId in $pids)")
    text = text.replace("Stop-Process -Id $pid", "Stop-Process -Id $processId")
    text = text.replace('Write-Host "Stopped process $pid on port 8501"', 'Write-Host "Stopped process $processId on port 8501"')

    QA.write_text(text, encoding="utf-8")
    py_compile.compile(str(QA), doraise=True)

    if text != before:
        print("qa_v2_visual_audit.py PID bug fixed ✅")
    else:
        print("qa_v2_visual_audit.py PID bug already fixed or not found.")


def main():
    print("=== Fix all raw HTML rendering in v2 ===")

    patch_app()
    patch_qa_pid_bug()

    print()
    print("Готово ✅")
    print("Теперь запускаю QA ещё раз...")
    print()

    if QA.exists():
        subprocess.run([sys.executable, str(QA)], cwd=str(ROOT))
    else:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
