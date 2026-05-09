from pathlib import Path
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
TARGET = ROOT / "auto_mobile_nav_v13.py"

if not TARGET.exists():
    print("auto_mobile_nav_v13.py не найден.")
    raise SystemExit(1)

text = TARGET.read_text(encoding="utf-8")

# Исправляем вложенные f''' ... ''' внутри большой строки MOBILE_NAV_CODE.
# Они ломали Python-синтаксис основного auto_mobile_nav_v13.py.

text = text.replace(
    "links.append(\n            f'''\n<a href=\"{href}\" target=\"_self\">",
    "links.append(\n            f\"\"\"\n<a href=\"{href}\" target=\"_self\">"
)

text = text.replace(
    "</a>\n'''\n        )",
    "</a>\n\"\"\"\n        )"
)

text = text.replace(
    "html = f'''\n<div class=\"medinki-bottom-nav-v13\">",
    "html = f\"\"\"\n<div class=\"medinki-bottom-nav-v13\">"
)

text = text.replace(
    "</div>\n'''\n\n    st.markdown(html, unsafe_allow_html=True)",
    "</div>\n\"\"\"\n\n    st.markdown(html, unsafe_allow_html=True)"
)

TARGET.write_text(text, encoding="utf-8")

try:
    py_compile.compile(str(TARGET), doraise=True)
    print("auto_mobile_nav_v13.py синтаксически исправлен ✅")
except Exception as e:
    print("Скрипт всё ещё сломан ❌")
    print(e)
    raise SystemExit(1)

print()
print("Теперь запускаю auto_mobile_nav_v13.py...")
print()

subprocess.run([sys.executable, str(TARGET)], cwd=str(ROOT))
