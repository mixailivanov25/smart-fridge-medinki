from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
DEV_AUTO = ROOT / "dev_auto.py"


PAGE_INTRO_CODE = r'''
def render_page_intro(title=None, subtitle=None, icon=None, *args, **kwargs):
    """
    Универсальный intro-блок страницы.

    Работает так:
    - render_page_intro()
    - render_page_intro("Заголовок", "Описание", "📱")
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

    st.markdown(
        f"""
<div class="medinki-page-intro" style="
    padding: 22px 26px;
    border-radius: 28px;
    background: linear-gradient(135deg, #f0fff4 0%, #ffffff 100%);
    border: 1px solid rgba(18, 51, 33, 0.10);
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    margin-bottom: 22px;
">
    <div style="
        display: flex;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
    ">
        <div style="font-size: 2.15rem; line-height: 1;">{icon}</div>
        <div>
            <h1 style="
                margin: 0;
                padding: 0;
                line-height: 1.18;
                color: #123321;
                font-size: clamp(2rem, 4vw, 3rem);
            ">{title}</h1>
            <p style="
                margin: 8px 0 0 0;
                color: #475569;
                font-size: 1.08rem;
                line-height: 1.45;
            ">{subtitle}</p>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
'''


DEV_AUTO_SHOULD_SKIP_CODE = r'''
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
'''


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"auto_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def compile_py(path: Path):
    py_compile.compile(str(path), doraise=True)


def quarantine_root_app_backups():
    target_dir = ROOT / "backups" / f"root_app_backups_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    moved = 0

    patterns = [
        "app_backup*.py",
        "app_before*.py",
        "app_*backup*.py",
    ]

    files = []
    for pattern in patterns:
        files.extend(ROOT.glob(pattern))

    for path in sorted(set(files)):
        if path.name == "app.py":
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / path.name
        shutil.move(str(path), str(target))
        moved += 1
        print(f"Moved backup file: {path.name} -> {target}")

    if moved:
        print(f"Moved root backup files: {moved}")
    else:
        print("No root app backup files to move.")


def patch_dev_auto():
    if not DEV_AUTO.exists():
        print("dev_auto.py not found, skip.")
        return

    backup(DEV_AUTO)

    text = DEV_AUTO.read_text(encoding="utf-8")

    pattern = r'(?ms)^def\s+should_skip_py\s*\(\s*path:\s*Path\s*\)\s*->\s*bool\s*:\n.*?(?=^def\s+|\Z)'

    new_text, count = re.subn(
        pattern,
        DEV_AUTO_SHOULD_SKIP_CODE.strip() + "\n\n",
        text,
        count=1,
    )

    if count:
        DEV_AUTO.write_text(new_text, encoding="utf-8")
        compile_py(DEV_AUTO)
        print("dev_auto.py patched.")
    else:
        print("should_skip_py() not found in dev_auto.py, skip.")


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


def patch_render_page_intro():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    pattern = r'(?ms)^def\s+render_page_intro\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'

    new_text, count = re.subn(
        pattern,
        PAGE_INTRO_CODE.strip() + "\n\n",
        text,
        count=1,
    )

    if count:
        text = new_text
        print("render_page_intro() replaced.")
    else:
        lines = text.splitlines()
        insert_idx = find_safe_insert_after_imports(text)
        lines[insert_idx:insert_idx] = [""] + PAGE_INTRO_CODE.strip().splitlines() + [""]
        text = "\n".join(lines) + "\n"
        print("render_page_intro() added.")

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    print("app.py syntax OK.")


def main():
    print("=== Auto repair current error ===")

    quarantine_root_app_backups()
    patch_dev_auto()
    patch_render_page_intro()

    print()
    print("Готово ✅")
    print("Теперь запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
