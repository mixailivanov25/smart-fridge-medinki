from pathlib import Path
import py_compile
import shutil
from datetime import datetime
import subprocess


PROJECT_DIR = Path(__file__).resolve().parent
APP_FILE = PROJECT_DIR / "app.py"


def run(command):
    print(f"\n▶️ {command}")

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
    print(" Hotfix v1.2 Быстрый экран Syntax")
    print("====================================")

    if not APP_FILE.exists():
        print("❌ app.py не найден.")
        return

    backup_name = f"app_backup_before_fast_screen_syntax_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    shutil.copy2(APP_FILE, PROJECT_DIR / backup_name)
    print(f"📦 Backup создан: {backup_name}")

    text = APP_FILE.read_text(encoding="utf-8")

    if 'elif page == "Быстрый экран":' not in text:
        print("ℹ️ Не найдено 'elif page == \"Быстрый экран\"'. Возможно, уже исправлено.")
    else:
        # Меняем только первый быстрый экран с elif на if
        text = text.replace(
            'elif page == "Быстрый экран":',
            'if page == "Быстрый экран":',
            1
        )
        print("✅ Быстрый экран изменён с elif на if.")

    # Теперь первый блок Главная после Быстрого экрана должен стать elif
    fast_pos = text.find('if page == "Быстрый экран":')
    main_pos = text.find('if page == "Главная":', fast_pos)

    if fast_pos != -1 and main_pos != -1:
        text = text[:main_pos] + text[main_pos:].replace(
            'if page == "Главная":',
            'elif page == "Главная":',
            1
        )
        print("✅ Главная изменена с if на elif после Быстрого экрана.")
    else:
        print("⚠️ Не удалось найти связку Быстрый экран → Главная. Проверь app.py вручную, если ошибка останется.")

    APP_FILE.write_text(text, encoding="utf-8")

    try:
        py_compile.compile(str(APP_FILE), doraise=True)
        print("✅ Синтаксис app.py теперь в порядке.")
    except Exception as e:
        print("❌ Ошибка синтаксиса осталась:")
        print(e)
        return

    # Пробуем отправить на GitHub
    if (PROJECT_DIR / ".git").exists():
        print("\nПробую отправить исправление на GitHub...")

        run("git add app.py")
        status = run("git status --short")

        if status.stdout.strip():
            run('git commit -m "Fix fast screen syntax"')
            push = run("git push")

            if push.returncode == 0:
                print("✅ Исправление отправлено на GitHub.")
            else:
                print("⚠️ Не удалось сделать git push автоматически.")
                print("Выполни вручную:")
                print("git add app.py")
                print('git commit -m "Fix fast screen syntax"')
                print("git push")
        else:
            print("ℹ️ Нет изменений для коммита.")

    print("\n✅ Hotfix завершён.")
    print("\nПроверь локально:")
    print("python -m streamlit run app.py")


if __name__ == "__main__":
    main()