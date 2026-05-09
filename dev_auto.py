from pathlib import Path
from datetime import datetime
import argparse
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import webbrowser
import py_compile

ROOT = Path(__file__).parent.resolve()
BACKUP_ROOT = ROOT / "backups"


def log(msg: str):
    print(msg, flush=True)


def get_clipboard_text() -> str:
    """
    Берёт текст из буфера обмена.
    Сначала пробует tkinter, потом PowerShell.
    """
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            return result.stdout
    except Exception:
        pass

    return ""


def strip_code_fence(content: str) -> str:
    """
    Убирает markdown-обёртку ```python ... ```
    """
    content = content.strip("\n")

    lines = content.splitlines()

    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).rstrip() + "\n"


def parse_patch_bundle(text: str):
    """
    Поддерживаем формат:

    --- FILE: filename.py ---
    ```python
    ...
    ```

    --- RUN ---
    python filename.py

    Можно несколько FILE-блоков.
    """

    file_marker = re.compile(r"^\s*---\s*FILE:\s*(.+?)\s*---\s*$", re.IGNORECASE)
    run_marker = re.compile(r"^\s*---\s*RUN\s*---\s*$", re.IGNORECASE)

    files = []
    run_commands = []

    current_type = None
    current_name = None
    buffer = []

    def flush():
        nonlocal current_type, current_name, buffer, files, run_commands

        if current_type == "file" and current_name:
            files.append((current_name, strip_code_fence("\n".join(buffer))))
        elif current_type == "run":
            raw = "\n".join(buffer)
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    continue
                if line.startswith("```"):
                    continue
                run_commands.append(line)

        current_type = None
        current_name = None
        buffer = []

    for line in text.splitlines():
        fm = file_marker.match(line)
        rm = run_marker.match(line)

        if fm:
            flush()
            current_type = "file"
            current_name = fm.group(1).strip()
            buffer = []
            continue

        if rm:
            flush()
            current_type = "run"
            current_name = None
            buffer = []
            continue

        if current_type:
            buffer.append(line)

    flush()

    return files, run_commands


def backup_file(path: Path, backup_dir: Path):
    if not path.exists():
        return

    backup_dir.mkdir(parents=True, exist_ok=True)

    rel = path.relative_to(ROOT)
    target = backup_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(path, target)


def apply_files(files):
    if not files:
        log("Файлы в patch-bundle не найдены.")
        return False

    backup_dir = BACKUP_ROOT / f"dev_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in files:
        safe_name = filename.replace("\\", "/").strip("/")

        if ".." in Path(safe_name).parts:
            raise ValueError(f"Небезопасный путь файла: {filename}")

        path = ROOT / safe_name

        backup_file(path, backup_dir)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        log(f"Записан файл: {safe_name}")

    log(f"Backup: {backup_dir}")
    return True


def should_skip_py(path: Path) -> bool:
    parts = set(path.parts)
    name = path.name.lower()

    skip_dirs = {
        "backups",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "env",
        ".mypy_cache",
        ".pytest_cache",
    }

    if parts & skip_dirs:
        return True

    # Старые backup-файлы app.py в корне не должны ломать проверку проекта.
    backup_name_prefixes = (
        "app_backup",
        "app_before",
        "app_old",
    )

    if name.startswith(backup_name_prefixes):
        return True

    if "backup_before" in name:
        return True

    return False

def compile_python_files():
    """
    Проверяет синтаксис всех .py файлов проекта, кроме backups/venv.
    """
    ok = True
    errors = []

    py_files = [
        p for p in ROOT.rglob("*.py")
        if not should_skip_py(p)
    ]

    if not py_files:
        log("Python-файлы не найдены.")
        return False

    for path in py_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as e:
            ok = False
            errors.append((path, e))

    if ok:
        log(f"Синтаксис OK ✅ Проверено файлов: {len(py_files)}")
        return True

    log("Есть ошибки синтаксиса ❌")
    for path, err in errors:
        log("")
        log(f"Файл: {path.relative_to(ROOT)}")
        log(str(err))

    return False


def run_command(command: str):
    log("")
    log(f"> {command}")

    result = subprocess.run(
        command,
        shell=True,
        cwd=str(ROOT),
        text=True,
    )

    if result.returncode != 0:
        log(f"Команда завершилась с ошибкой: {result.returncode}")
        return False

    return True


def is_port_open(host="127.0.0.1", port=8501, timeout=0.4):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def start_streamlit(open_browser=True):
    """
    Запускает Streamlit, если порт 8501 ещё не занят.
    Если уже запущен — просто открывает браузер.
    """

    if is_port_open():
        log("Streamlit уже запущен на http://localhost:8501")
        if open_browser:
            webbrowser.open("http://localhost:8501")
        return True

    app = ROOT / "app.py"
    if not app.exists():
        log("app.py не найден.")
        return False

    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]

    log("Запускаю Streamlit...")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_CONSOLE

    subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        creationflags=creationflags,
    )

    for _ in range(30):
        if is_port_open():
            log("Streamlit запущен: http://localhost:8501")
            if open_browser:
                webbrowser.open("http://localhost:8501")
            return True
        time.sleep(0.5)

    log("Streamlit не успел подняться за 15 секунд. Проверь терминал Streamlit.")
    return False


def open_app():
    webbrowser.open("http://localhost:8501")
    log("Открываю http://localhost:8501")


def patch_from_clipboard(args):
    text = get_clipboard_text()

    if not text.strip():
        log("Буфер обмена пустой или не удалось его прочитать.")
        return False

    files, commands = parse_patch_bundle(text)

    if not files:
        log("В буфере не найдено FILE-блоков.")
        log("")
        log("Ожидаемый формат:")
        log("--- FILE: hotfix.py ---")
        log("```python")
        log("print('hello')")
        log("```")
        log("")
        log("--- RUN ---")
        log("python hotfix.py")
        return False

    log(f"Найдено файлов в patch: {len(files)}")
    for filename, _ in files:
        log(f"- {filename}")

    if commands:
        log("")
        log("Команды RUN:")
        for c in commands:
            log(f"- {c}")

    apply_files(files)

    if args.run:
        for command in commands:
            ok = run_command(command)
            if not ok:
                return False

    if not args.no_check:
        ok = compile_python_files()
        if not ok:
            return False

    if args.open:
        start_streamlit(open_browser=True)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Dev automation helper for Smart Fridge Medinki"
    )

    sub = parser.add_subparsers(dest="command")

    p_patch = sub.add_parser("patch", help="Apply patch-bundle from clipboard")
    p_patch.add_argument("--run", action="store_true", help="Run commands from RUN block")
    p_patch.add_argument("--open", action="store_true", help="Start/open Streamlit")
    p_patch.add_argument("--no-check", action="store_true", help="Do not compile-check python files")

    sub.add_parser("check", help="Compile-check python files")

    p_run = sub.add_parser("run", help="Start/open Streamlit")
    p_run.add_argument("--no-open", action="store_true", help="Do not open browser")

    sub.add_parser("open", help="Open app in browser")

    args = parser.parse_args()

    if args.command == "patch":
        ok = patch_from_clipboard(args)
        sys.exit(0 if ok else 1)

    if args.command == "check":
        ok = compile_python_files()
        sys.exit(0 if ok else 1)

    if args.command == "run":
        ok = start_streamlit(open_browser=not args.no_open)
        sys.exit(0 if ok else 1)

    if args.command == "open":
        open_app()
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()