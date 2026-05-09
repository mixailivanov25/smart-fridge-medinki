from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
BACKUPS = ROOT / "backups"
QA = ROOT / "qa_v2_visual_audit.py"


def find_latest_sidebar_backup():
    patterns = [
        "custom_sidebar_v2_fixed_*",
        "custom_sidebar_v2_*",
    ]

    candidates = []

    for pattern in patterns:
        for folder in BACKUPS.glob(pattern):
            app_backup = folder / "app.py"
            if app_backup.exists():
                candidates.append(app_backup)

    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def backup_current_app():
    backup_dir = BACKUPS / f"rollback_custom_sidebar_current_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / "app_with_broken_custom_sidebar.py"

    if APP.exists():
        shutil.copy2(APP, target)
        print(f"Current broken app backed up: {target}")


def clean_bom(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")


def main():
    print("=== Rollback broken custom sidebar v2 ===")

    backup_app = find_latest_sidebar_backup()

    if not backup_app:
        print("Не найден backup перед custom sidebar.")
        print("Нужно будет восстановить app.py другим способом.")
        raise SystemExit(1)

    print(f"Found backup to restore: {backup_app}")

    backup_current_app()

    shutil.copy2(backup_app, APP)
    clean_bom(APP)

    py_compile.compile(str(APP), doraise=True)
    print("app.py restored and syntax OK ✅")

    print()
    print("Откатили только последний эксперимент с кастомной левой панелью.")
    print("Теперь запускаю QA заново...")
    print()

    if QA.exists():
        subprocess.run([sys.executable, str(QA)], cwd=str(ROOT))
    else:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()