from pathlib import Path
import subprocess
import py_compile
import shutil


PROJECT_DIR = Path(__file__).resolve().parent

GITHUB_REPO_URL = "https://github.com/mixailivanov25/smart-fridge-medinki.git"

REQUIRED_FILES = [
    "app.py",
    "database.py",
    "settings.py",
    "recipes.py",
    "demo_data.py",
    "product_catalog.py",
    "dish_catalog.py",
    "menu_engine.py",
]

REQUIREMENTS_CONTENT = """streamlit
pandas
"""

GITIGNORE_CONTENT = """# Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environments
venv/
.env/
.venv/

# Local database
data/fridge.db

# Backups
backup_before_*/
backup_before_v*/
app_backup_before_*.py

# Screenshots
screenshots_v*/
*.png

# System
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Streamlit secrets
.streamlit/secrets.toml
"""

README_CONTENT = """# Умный холодильник Мединки

Приложение для учёта продуктов, рецептов, меню на неделю, покупок, дневника питания и списания продуктов.

## Возможности

- учёт продуктов в холодильнике;
- сроки годности;
- каталог продуктов;
- рецепты;
- каталог блюд;
- меню на неделю для Мишки и Мединки;
- любимые блюда;
- дневник питания;
- умные покупки;
- история приготовленных блюд;
- списание продуктов;
- аналитика;
- мобильное открытие через браузер.

## Запуск локально

python -m streamlit run app.py

## Разработчик

Иванов Михаил
"""

STREAMLIT_CONFIG_CONTENT = """[theme]
primaryColor = "#2f6b45"
backgroundColor = "#f7f9fb"
secondaryBackgroundColor = "#ffffff"
textColor = "#163020"
font = "sans serif"

[server]
headless = true

[browser]
gatherUsageStats = false
"""


def run(command, check=True):
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

    if check and result.returncode != 0:
        raise RuntimeError(f"Команда завершилась с ошибкой: {command}")

    return result


def write_text_file(relative_path, content):
    path = PROJECT_DIR / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ Создан/обновлён файл: {relative_path}")


def check_required_files():
    print("\n==============================")
    print("Проверяю основные файлы проекта")
    print("==============================")

    missing = []

    for file_name in REQUIRED_FILES:
        path = PROJECT_DIR / file_name

        if path.exists():
            print(f"✅ Есть: {file_name}")
        else:
            print(f"❌ Нет: {file_name}")
            missing.append(file_name)

    if missing:
        print("\n❌ Не хватает файлов:")
        for item in missing:
            print(f"- {item}")

        return False

    return True


def create_deploy_files():
    print("\n==============================")
    print("Создаю файлы для публикации")
    print("==============================")

    write_text_file("requirements.txt", REQUIREMENTS_CONTENT)
    write_text_file(".gitignore", GITIGNORE_CONTENT)
    write_text_file("README.md", README_CONTENT)
    write_text_file(".streamlit/config.toml", STREAMLIT_CONFIG_CONTENT)

    data_dir = PROJECT_DIR / "data"
    data_dir.mkdir(exist_ok=True)

    gitkeep = data_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
        print("✅ Создан файл: data/.gitkeep")


def compile_python_files():
    print("\n==============================")
    print("Проверяю синтаксис Python-файлов")
    print("==============================")

    ok = True

    for file_name in REQUIRED_FILES:
        path = PROJECT_DIR / file_name

        try:
            py_compile.compile(str(path), doraise=True)
            print(f"✅ OK: {file_name}")
        except Exception as e:
            ok = False
            print(f"❌ Ошибка в {file_name}")
            print(e)

    return ok


def check_git_installed():
    print("\n==============================")
    print("Проверяю Git")
    print("==============================")

    if shutil.which("git") is None:
        print("❌ Git не найден.")
        print("Скачай и установи Git:")
        print("https://git-scm.com/downloads")
        print("После установки закрой и заново открой VS Code.")
        return False

    result = run("git --version", check=False)

    if result.returncode == 0:
        print("✅ Git установлен.")
        return True

    print("❌ Git есть, но команда git не работает.")
    return False


def setup_git():
    print("\n==============================")
    print("Настраиваю Git")
    print("==============================")

    if not (PROJECT_DIR / ".git").exists():
        run("git init")
    else:
        print("✅ Git уже инициализирован.")

    # Локальные настройки только для этого проекта
    run('git config user.name "Ivanov Mikhail"', check=False)
    run('git config user.email "mixailivanov25@users.noreply.github.com"', check=False)

    existing_remote = run("git remote get-url origin", check=False)

    if existing_remote.returncode == 0:
        run(f'git remote set-url origin "{GITHUB_REPO_URL}"')
    else:
        run(f'git remote add origin "{GITHUB_REPO_URL}"')

    run("git branch -M main", check=False)


def commit_and_push():
    print("\n==============================")
    print("Делаю commit и отправляю на GitHub")
    print("==============================")

    run("git add .")

    status = run("git status --short", check=False)

    if status.stdout.strip():
        commit_result = run('git commit -m "Prepare Streamlit deployment"', check=False)

        if commit_result.returncode != 0:
            text = (commit_result.stdout + commit_result.stderr).lower()

            if "nothing to commit" in text:
                print("ℹ️ Коммит не нужен, изменений нет.")
            else:
                print("⚠️ Git commit завершился нестандартно. Смотри сообщение выше.")
    else:
        print("ℹ️ Нет изменений для коммита.")

    print("\nСейчас проект будет отправлен на GitHub.")
    print("Если откроется окно авторизации GitHub — войди и подтверди.")

    run("git push -u origin main", check=True)

    print("✅ Проект отправлен на GitHub.")


def print_streamlit_steps():
    print("\n==============================")
    print("Осталось сделать в браузере")
    print("==============================")

    print("""
1. Обнови страницу GitHub:
   https://github.com/mixailivanov25/smart-fridge-medinki

2. Убедись, что там появились файлы:
   app.py
   database.py
   settings.py
   requirements.txt
   README.md

3. Открой Streamlit Cloud:
   https://streamlit.io/cloud

4. Войди через GitHub.

5. Нажми New app.

6. Выбери:
   Repository: smart-fridge-medinki
   Branch: main
   Main file path: app.py

7. Нажми Deploy.

8. После деплоя получишь ссылку вида:
   https://smart-fridge-medinki.streamlit.app

9. Открой ссылку на телефоне.

10. Добавь на главный экран:
   Android: Chrome → ⋮ → Добавить на главный экран
   iPhone: Safari → Поделиться → На экран Домой
""")


def main():
    print("======================================")
    print(" Публикация приложения")
    print(" Умный холодильник Мединки")
    print("======================================")

    if not check_required_files():
        print("\n❌ Сначала нужно убедиться, что все файлы проекта на месте.")
        return

    create_deploy_files()

    if not compile_python_files():
        print("\n❌ Есть ошибки синтаксиса. Сначала нужно их исправить.")
        return

    if not check_git_installed():
        return

    setup_git()

    try:
        commit_and_push()
    except Exception as e:
        print("\n❌ Ошибка при отправке на GitHub:")
        print(e)
        print("""
Возможные причины:
1. GitHub попросил авторизацию.
2. Git не получил доступ к репозиторию.
3. Нужно войти в GitHub в браузере.
4. Можно попробовать выполнить команду вручную:

git push -u origin main
""")
        return

    print_streamlit_steps()

    print("\n✅ Готово. Проект подготовлен и отправлен на GitHub.")


if __name__ == "__main__":
    main()