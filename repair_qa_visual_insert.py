from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
QA = ROOT / "auto_qa_screenshots_and_fix.py"


def backup(path: Path):
    if not path.exists():
        return

    backup_dir = ROOT / "backups" / f"repair_qa_visual_insert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    target = backup_dir / path.name
    shutil.copy2(path, target)
    print(f"Backup saved: {target}")


def compile_app():
    try:
        py_compile.compile(str(APP), doraise=True)
        print("app.py syntax OK ✅")
        return True
    except py_compile.PyCompileError as e:
        print("app.py syntax error ❌")
        print(e)

        # Покажем строки вокруг ошибки.
        try:
            msg = str(e)
            m = re.search(r"line\s+(\d+)", msg)
            if m:
                line_no = int(m.group(1))
                lines = APP.read_text(encoding="utf-8").splitlines()
                start = max(1, line_no - 5)
                end = min(len(lines), line_no + 5)

                print()
                print(f"Context lines {start}-{end}:")
                for i in range(start, end + 1):
                    prefix = ">>" if i == line_no else "  "
                    print(f"{prefix} {i}: {lines[i - 1]}")
        except Exception:
            pass

        return False


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
    """
    Находит конец вызова st.set_page_config(...).
    Возвращает индекс вставки после закрывающей скобки и последующего перевода строки.
    """
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
                # Вставляем после конца строки.
                line_end = text.find("\n", i)
                if line_end == -1:
                    return i + 1
                return line_end + 1

        i += 1

    return None


def remove_all_visual_fix_calls(text: str) -> str:
    lines = text.splitlines()
    new_lines = []
    removed = 0

    for line in lines:
        if line.strip() == "apply_qa_visual_fix_v13()":
            removed += 1
            continue
        new_lines.append(line)

    if removed:
        print(f"Removed misplaced apply_qa_visual_fix_v13() calls: {removed}")

    return "\n".join(new_lines) + "\n"


def ensure_visual_fix_import(text: str) -> str:
    # Удаляем дубли импорта.
    lines = text.splitlines()
    new_lines = []
    removed = 0

    for line in lines:
        if line.strip() == "from qa_visual_fix_v13 import apply_qa_visual_fix_v13":
            removed += 1
            continue
        new_lines.append(line)

    text = "\n".join(new_lines) + "\n"

    insert_idx = find_safe_insert_after_imports(text)
    lines = text.splitlines()
    lines.insert(insert_idx, "from qa_visual_fix_v13 import apply_qa_visual_fix_v13")

    print("Ensured qa_visual_fix_v13 import.")
    return "\n".join(lines) + "\n"


def ensure_visual_fix_call(text: str) -> str:
    call = "apply_qa_visual_fix_v13()"

    insert_pos = find_set_page_config_end(text)

    if insert_pos is not None:
        text = text[:insert_pos] + call + "\n" + text[insert_pos:]
        print("Inserted apply_qa_visual_fix_v13() after st.set_page_config().")
        return text

    # Если set_page_config не найден — ставим перед первой top-level def.
    m = re.search(r"(?m)^def\s+", text)
    if m:
        text = text[:m.start()] + call + "\n\n" + text[m.start():]
        print("Inserted apply_qa_visual_fix_v13() before first function.")
        return text

    # Совсем крайний случай — после импортов.
    lines = text.splitlines()
    idx = find_safe_insert_after_imports(text)
    lines.insert(idx, call)
    print("Inserted apply_qa_visual_fix_v13() after imports.")
    return "\n".join(lines) + "\n"


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def is_def_line(line: str):
    return re.match(r"^(\s*)def\s+[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)\s*:\s*(#.*)?$", line)


def repair_empty_defs(text: str) -> str:
    """
    Если после предыдущих автоматических правок остались пустые функции:
        def something():
        def next():
    вставляем pass.
    """
    lines = text.splitlines()
    inserts = []

    for i, line in enumerate(lines):
        m = is_def_line(line)
        if not m:
            continue

        indent = len(m.group(1))

        j = i + 1
        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#")):
            j += 1

        if j >= len(lines):
            inserts.append((i + 1, " " * (indent + 4) + "pass"))
            continue

        if line_indent(lines[j]) <= indent:
            inserts.append((i + 1, " " * (indent + 4) + "pass"))

    if not inserts:
        print("No empty functions found.")
        return text

    for idx, value in reversed(inserts):
        lines.insert(idx, value)

    print(f"Repaired empty functions: {len(inserts)}")
    return "\n".join(lines) + "\n"


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = remove_all_visual_fix_calls(text)
    text = ensure_visual_fix_import(text)
    text = repair_empty_defs(text)
    text = ensure_visual_fix_call(text)

    APP.write_text(text, encoding="utf-8")

    if not compile_app():
        raise SystemExit(1)


def main():
    print("=== Repair QA visual fix insertion ===")

    patch_app()

    print()
    print("Готово ✅")
    print("app.py починен. Теперь запускаю QA заново...")
    print()

    if QA.exists():
        subprocess.run([sys.executable, str(QA)], cwd=str(ROOT))
    else:
        print("auto_qa_screenshots_and_fix.py не найден.")
        print("Запусти приложение обычной командой:")
        print("python -m streamlit run app.py")


if __name__ == "__main__":
    main()
