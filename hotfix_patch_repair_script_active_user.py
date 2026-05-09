from pathlib import Path
import py_compile

ROOT = Path(__file__).parent.resolve()
TARGET = ROOT / "hotfix_v13_repair_empty_fast_screen.py"


def main():
    if not TARGET.exists():
        print("Не найден файл hotfix_v13_repair_empty_fast_screen.py")
        return

    text = TARGET.read_text(encoding="utf-8")

    before = text

    text = text.replace(
        "<h2>👤 Активный пользователь: {active_user}</h2>",
        "<h2>👤 Активный пользователь: {{active_user}}</h2>",
    )

    text = text.replace(
        "Активный пользователь: {active_user}",
        "Активный пользователь: {{active_user}}",
    )

    TARGET.write_text(text, encoding="utf-8")

    if text != before:
        print("Готово ✅")
        print("Исправлен hotfix_v13_repair_empty_fast_screen.py")
        print("Теперь {active_user} не будет вычисляться слишком рано.")
    else:
        print("Замена не потребовалась или строка уже исправлена.")

    try:
        py_compile.compile(str(TARGET), doraise=True)
        print("Скрипт hotfix_v13_repair_empty_fast_screen.py синтаксически корректен ✅")
    except Exception as e:
        print("В самом repair-скрипте всё ещё есть ошибка:")
        print(e)


if __name__ == "__main__":
    main()