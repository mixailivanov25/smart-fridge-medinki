from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
FILES = [
    ROOT / "app.py",
    ROOT / "v2_catalog_data.py",
]


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"fix_bom_ufeff_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def clean_bom(path: Path):
    if not path.exists():
        print(f"Skip missing: {path.name}")
        return

    backup(path)

    raw = path.read_bytes()

    # Читаем с utf-8-sig, чтобы убрать BOM в начале, если есть.
    text = raw.decode("utf-8-sig", errors="replace")

    count = text.count("\ufeff")

    # Убираем BOM/FEFF из любых мест файла.
    text = text.replace("\ufeff", "")

    path.write_text(text, encoding="utf-8")

    print(f"Cleaned {path.name}: removed FEFF count = {count}")


def compile_file(path: Path):
    py_compile.compile(str(path), doraise=True)
    print(f"{path.name} syntax OK ✅")


def main():
    print("=== Fix U+FEFF / BOM characters ===")

    for path in FILES:
        clean_bom(path)

    compile_file(ROOT / "v2_catalog_data.py")
    compile_file(ROOT / "app.py")

    print()
    print("Готово ✅")
    print("BOM/FEFF очищены, синтаксис проверен.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
