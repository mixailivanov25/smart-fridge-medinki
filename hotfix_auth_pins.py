from pathlib import Path
import py_compile
from datetime import datetime
import shutil
import subprocess


PROJECT_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = PROJECT_DIR / "settings.py"
APP_FILE = PROJECT_DIR / "app.py"


def run(command):
    result = subprocess.run(
        command,
        shell=True,
        cwd=PROJECT_DIR,
        text=True,
        capture_output=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result


def main():
    print("====================================")
    print(" Hotfix DEFAULT_AUTH_PINS")
    print("====================================")

    if not SETTINGS_FILE.exists():
        print("❌ settings.py не найден.")
        return

    backup_name = f"settings_backup_before_auth_pins_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(SETTINGS_FILE, PROJECT_DIR / backup_name)
    print(f"📦 Backup создан: {backup_name}")

    text = SETTINGS_FILE.read_text(encoding="utf-8")

    # Обновляем версию, если нужно
    import re
    if "APP_VERSION" in text:
        text = re.sub(r'APP_VERSION\s*=\s*"[^"]+"', 'APP_VERSION = "v1.1"', text)
    else:
        text += '\nAPP_VERSION = "v1.1"\n'

    # Добавляем DEFAULT_AUTH_PINS, если его нет
    if "DEFAULT_AUTH_PINS" not in text:
        text += '''

# v1.1 Auth defaults
# В облачной версии лучше задать PIN-коды в Streamlit Cloud Secrets:
# AUTH_PIN_MISHKA = "ваш_PIN"
# AUTH_PIN_MEDINKA = "ваш_PIN"
DEFAULT_AUTH_PINS = {
    "Мишка": "1111",
    "Мединка": "2222"
}
'''
        print("✅ DEFAULT_AUTH_PINS добавлен в settings.py")
    else:
        print("ℹ️ DEFAULT_AUTH_PINS уже есть в settings.py")

    SETTINGS_FILE.write_text(text, encoding="utf-8")

    try:
        py_compile.compile(str(SETTINGS_FILE), doraise=True)
        print("✅ settings.py синтаксически корректен.")
    except Exception as e:
        print("❌ Ошибка синтаксиса в settings.py:")
        print(e)
        return

    if APP_FILE.exists():
        try:
            py_compile.compile(str(APP_FILE), doraise=True)
            print("✅ app.py синтаксически корректен.")
        except Exception as e:
            print("❌ Ошибка синтаксиса в app.py:")
            print(e)
            return

    print("\n✅ Hotfix применён.")
    print("\nТеперь запусти локально:")
    print("python -m streamlit run app.py")

    # Пробуем отправить на GitHub, если git есть
    if (PROJECT_DIR / ".git").exists():
        print("\nПробую отправить исправление на GitHub...")

        run("git add settings.py app.py")
        status = run("git status --short")

        if status.stdout.strip():
            run('git commit -m "Fix auth pins settings"')
            push = run("git push")

            if push.returncode == 0:
                print("✅ Исправление отправлено на GitHub.")
            else:
                print("⚠️ Git push не прошёл автоматически. Можно потом выполнить вручную:")
                print("git add settings.py app.py")
                print('git commit -m "Fix auth pins settings"')
                print("git push")
        else:
            print("ℹ️ Нет изменений для коммита.")


if __name__ == "__main__":
    main()