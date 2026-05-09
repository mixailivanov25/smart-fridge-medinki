from pathlib import Path
import py_compile

APP_FILE = Path("app.py")


def main():
    if not APP_FILE.exists():
        print("❌ Не найден app.py")
        return

    text = APP_FILE.read_text(encoding="utf-8")

    # 1. Добавляем глобальный счётчик, если его ещё нет
    if "DOWNLOAD_BUTTON_COUNTER = 0" not in text:
        text = text.replace(
            "def render_shopping_list(items):",
            "DOWNLOAD_BUTTON_COUNTER = 0\n\n\ndef render_shopping_list(items):"
        )

    # 2. Добавляем уникальный key к download_button внутри render_shopping_list
    old_block = '''    st.download_button(
        "📥 Скачать список покупок",
        data="\\n".join(text_lines),
        file_name="shopping_list_medinki.txt",
        mime="text/plain"
    )'''

    new_block = '''    global DOWNLOAD_BUTTON_COUNTER
    DOWNLOAD_BUTTON_COUNTER += 1

    st.download_button(
        "📥 Скачать список покупок",
        data="\\n".join(text_lines),
        file_name="shopping_list_medinki.txt",
        mime="text/plain",
        key=f"download_shopping_list_{DOWNLOAD_BUTTON_COUNTER}"
    )'''

    if old_block in text:
        text = text.replace(old_block, new_block)
        APP_FILE.write_text(text, encoding="utf-8")
        print("✅ app.py обновлён: добавлены уникальные key для download_button.")
    elif 'key=f"download_shopping_list_{DOWNLOAD_BUTTON_COUNTER}"' in text:
        print("ℹ️ Похоже, исправление уже применено.")
    else:
        print("⚠️ Не нашёл стандартный блок st.download_button. Возможно, код уже изменён.")
        print("Пришли функцию render_shopping_list из app.py, если ошибка останется.")

    try:
        py_compile.compile(str(APP_FILE), doraise=True)
        print("✅ Синтаксис app.py в порядке.")
    except Exception as e:
        print("❌ Ошибка синтаксиса после исправления:")
        print(e)


if __name__ == "__main__":
    main()