from pathlib import Path
from datetime import datetime
import base64
import mimetypes
import sys


PROJECT_DIR = Path(__file__).resolve().parent
OUT_HTML = PROJECT_DIR / "presentation_medinki.html"
OUT_PDF = PROJECT_DIR / "presentation_medinki.pdf"

ASSETS_DIR = PROJECT_DIR / "presentation_assets"


APP_NAME = "Умный холодильник Мединки"
APP_VERSION = "v1.2"
APP_URL = "https://smart-fridge-medinki-7s5ear7hec9kczrwif9mx4.streamlit.app/"
DEVELOPER = "Иванов Михаил"


def image_to_base64(path: Path):
    if not path.exists():
        return None

    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/png"

    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def find_image(*names):
    candidates = []

    for name in names:
        candidates.append(ASSETS_DIR / name)
        candidates.append(PROJECT_DIR / name)

    # fallback старых автоскриншотов
    fallback_dirs = [
        PROJECT_DIR / "screenshots_v04",
        PROJECT_DIR / "screenshots_v05",
        PROJECT_DIR / "screenshots_v06",
        PROJECT_DIR / "screenshots_v07",
        PROJECT_DIR / "screenshots_v08",
        PROJECT_DIR / "screenshots_v09",
    ]

    for folder in fallback_dirs:
        for name in names:
            candidates.append(folder / name)

    for path in candidates:
        if path.exists():
            return path

    return None


def screenshot_block(title, caption, *image_names):
    path = find_image(*image_names)

    if path:
        src = image_to_base64(path)
        return f"""
        <div class="screenshot-block">
            <div class="screenshot-title">{title}</div>
            <img src="{src}" alt="{title}">
            <div class="caption">{caption}</div>
        </div>
        """

    return f"""
    <div class="screenshot-placeholder">
        <div class="placeholder-icon">🖼️</div>
        <div class="screenshot-title">{title}</div>
        <div class="caption">
            Скриншот можно добавить в папку <b>presentation_assets</b>.<br>
            Подходящие имена: {", ".join(image_names)}
        </div>
    </div>
    """


def slide(title, subtitle="", content="", class_name=""):
    return f"""
    <section class="slide {class_name}">
        <div class="slide-inner">
            <h1>{title}</h1>
            {f"<p class='subtitle'>{subtitle}</p>" if subtitle else ""}
            {content}
        </div>
    </section>
    """


def card(title, text, icon="✅"):
    return f"""
    <div class="card">
        <div class="card-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{text}</p>
    </div>
    """


def metric(value, label, icon=""):
    return f"""
    <div class="metric">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


def build_html():
    generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    slides = []

    slides.append(slide(
        title=APP_NAME,
        subtitle="Семейное облачное приложение для холодильника, рецептов, меню, покупок и питания",
        class_name="cover",
        content=f"""
        <div class="cover-grid">
            <div>
                <div class="badge">Версия {APP_VERSION}</div>
                <div class="badge">Разработка: {DEVELOPER}</div>
                <div class="badge">Streamlit + Supabase</div>
                <p class="cover-url">{APP_URL}</p>
            </div>
            <div class="cover-emoji">🥦</div>
        </div>
        <div class="footer-note">Презентация создана: {generated_at}</div>
        """
    ))

    slides.append(slide(
        title="Идея проекта",
        subtitle="Превратить обычный холодильник в умного семейного помощника",
        content=f"""
        <div class="grid-2">
            {card("Что есть дома", "Приложение хранит список продуктов, количество, сроки годности и калорийность.", "🧊")}
            {card("Что приготовить", "Подбирает рецепты из имеющихся продуктов и показывает, чего не хватает.", "🍳")}
            {card("Что купить", "Формирует список покупок и переносит купленное в холодильник.", "🛒")}
            {card("Что съели", "Ведёт дневник питания для Мишки и Мединки.", "📔")}
        </div>
        """
    ))

    slides.append(slide(
        title="Проблема",
        subtitle="В быту сложно помнить продукты, сроки, питание и покупки одновременно",
        content=f"""
        <div class="grid-3">
            {card("Продукты забываются", "Часть еды портится, потому что её не видно в общем списке.", "⏰")}
            {card("Меню приходится придумывать", "Каждый день возникает вопрос: что приготовить из того, что есть?", "🤔")}
            {card("Покупки хаотичны", "Список покупок часто составляется вручную и не связан с меню.", "📝")}
            {card("Калории не учитываются", "Сложно следить за дневной целью питания отдельно для двух человек.", "🎯")}
            {card("История теряется", "Не видно, что уже готовили и какие продукты были потрачены.", "📜")}
            {card("Данные должны жить в облаке", "Приложение должно открываться с телефона и сохранять данные постоянно.", "☁️")}
        </div>
        """
    ))

    slides.append(slide(
        title="Для кого приложение",
        subtitle="Семейный режим: Мишка и Мединка",
        content=f"""
        <div class="grid-2">
            <div class="person-card">
                <div class="person-emoji">🐻</div>
                <h2>Мишка</h2>
                <ul>
                    <li>цель по калориям;</li>
                    <li>любимые блюда;</li>
                    <li>личный дневник питания;</li>
                    <li>персональное меню на неделю.</li>
                </ul>
            </div>
            <div class="person-card">
                <div class="person-emoji">🌸</div>
                <h2>Мединка</h2>
                <ul>
                    <li>отдельные цели питания;</li>
                    <li>любимые блюда;</li>
                    <li>персональное меню;</li>
                    <li>учёт съеденного за день.</li>
                </ul>
            </div>
        </div>
        """
    ))

    slides.append(slide(
        title="Ключевой функционал",
        subtitle="Что уже реализовано в приложении",
        content=f"""
        <div class="grid-3">
            {card("Холодильник", "Продукты, количество, категории, калории, сроки годности.", "🧊")}
            {card("Каталог продуктов", "Выбор продукта из каталога вместо ручного ввода.", "🧺")}
            {card("Рецепты", "Подбор блюд из имеющихся продуктов.", "🍳")}
            {card("Каталог блюд", "Описание, история блюда, происхождение и факты.", "🍽️")}
            {card("Меню на неделю", "Отдельное меню для Мишки и Мединки.", "🗓️")}
            {card("Принять меню", "Списание продуктов по недельному меню.", "✅")}
            {card("Дневник питания", "Записи съеденного, калории, БЖУ.", "📔")}
            {card("Умные покупки", "Список покупок и перенос купленного в холодильник.", "🛒")}
            {card("Аналитика", "Сводки по питанию, покупкам, истории и списаниям.", "📊")}
        </div>
        """
    ))

    slides.append(slide(
        title="Главный экран",
        subtitle="Быстрый мобильный сценарий после входа",
        content=f"""
        <div class="grid-2">
            <div>
                <h2>Что показывает быстрый экран</h2>
                <ul>
                    <li>текущую дату и время;</li>
                    <li>активного пользователя;</li>
                    <li>калории за сегодня;</li>
                    <li>быстрые кнопки;</li>
                    <li>срочные продукты;</li>
                    <li>меню на сегодня.</li>
                </ul>
            </div>
            {screenshot_block("Быстрый экран", "Главная мобильная точка входа в приложение.", "02_fast_screen.png", "01_home.png", "01_glavnaya.png")}
        </div>
        """
    ))

    slides.append(slide(
        title="Холодильник",
        subtitle="Учёт продуктов и сроков годности",
        content=f"""
        <div class="grid-2">
            {screenshot_block("Мой холодильник", "Таблица и карточки продуктов со статусами сроков.", "03_fridge.png", "02_holodilnik_tablica.png", "03_holodilnik_kartochki.png")}
            <div>
                <h2>Возможности</h2>
                <ul>
                    <li>добавление продуктов вручную;</li>
                    <li>добавление из каталога;</li>
                    <li>массовый ввод списком;</li>
                    <li>редактирование остатков;</li>
                    <li>цветовые статусы сроков годности;</li>
                    <li>расчёт примерных калорий в запасах.</li>
                </ul>
            </div>
        </div>
        """
    ))

    slides.append(slide(
        title="Каталог продуктов",
        subtitle="Добавление продуктов без ручного ввода",
        content=f"""
        <div class="grid-3">
            {card("Категории", "Овощи, фрукты, молочные продукты, мясо, крупы, заморозка и другое.", "🗂️")}
            {card("Автоданные", "Единица измерения, калорийность, примерный срок хранения.", "⚙️")}
            {card("Быстрый поиск", "Можно найти продукт по названию или категории.", "🔎")}
        </div>
        {screenshot_block("Каталог продуктов", "Выбор продукта из каталога и добавление в холодильник.", "04_catalog.png", "05_dobavit_odin.png", "06_dobavit_spiskom.png")}
        """
    ))

    slides.append(slide(
        title="Рецепты и каталог блюд",
        subtitle="Блюда, ингредиенты, история и интересные факты",
        content=f"""
        <div class="grid-2">
            <div>
                <h2>Рецепты</h2>
                <ul>
                    <li>процент совпадения с холодильником;</li>
                    <li>что можно приготовить сейчас;</li>
                    <li>чего не хватает;</li>
                    <li>калории и время приготовления;</li>
                    <li>списание ингредиентов при готовке.</li>
                </ul>
            </div>
            {screenshot_block("Рецепты", "Подбор блюд из продуктов в холодильнике.", "05_recipes.png", "07_recepty.png")}
        </div>
        <div class="grid-2">
            {card("История блюда", "Откуда блюдо появилось и где популярно.", "📚")}
            {card("Факты", "Короткие интересные заметки о блюдах.", "✨")}
        </div>
        """
    ))

    slides.append(slide(
        title="Меню на неделю",
        subtitle="Персональное меню для Мишки и Мединки",
        content=f"""
        <div class="grid-2">
            {screenshot_block("Меню на неделю", "Отдельное меню по калориям и предпочтениям.", "06_menu.png", "08_menu_na_nedelyu.png")}
            <div>
                <h2>Что учитывается</h2>
                <ul>
                    <li>цель по калориям;</li>
                    <li>количество приёмов пищи;</li>
                    <li>любимые блюда;</li>
                    <li>нелюбимые продукты;</li>
                    <li>аллергии и ограничения;</li>
                    <li>наличие продуктов в холодильнике.</li>
                </ul>
            </div>
        </div>
        """
    ))

    slides.append(slide(
        title="Принятие меню и списание продуктов",
        subtitle="Меню можно принять, после чего продукты списываются автоматически",
        content=f"""
        <div class="grid-3">
            {card("Принять меню", "Сохраняется недельный план для двух человек.", "✅")}
            {card("Списать продукты", "Ингредиенты автоматически уменьшаются в холодильнике.", "📉")}
            {card("Отменить меню", "Можно отменить последнее принятое меню и вернуть продукты.", "↩️")}
        </div>
        <div class="note">
            Приложение защищает от случайного повторного списания: если меню уже принималось сегодня, нужна дополнительная галочка.
        </div>
        """
    ))

    slides.append(slide(
        title="Дневник питания",
        subtitle="Факт питания отдельно для Мишки и Мединки",
        content=f"""
        <div class="grid-2">
            {screenshot_block("Дневник питания", "Запись съеденного, калорий и БЖУ.", "07_diary.png")}
            <div>
                <h2>Возможности</h2>
                <ul>
                    <li>дата;</li>
                    <li>пользователь;</li>
                    <li>приём пищи;</li>
                    <li>блюдо;</li>
                    <li>калории;</li>
                    <li>белки, жиры, углеводы;</li>
                    <li>комментарий.</li>
                </ul>
            </div>
        </div>
        """
    ))

    slides.append(slide(
        title="Умные покупки",
        subtitle="Покупки связаны с холодильником",
        content=f"""
        <div class="grid-2">
            <div>
                <h2>Как работает</h2>
                <ul>
                    <li>добавить продукт в список покупок;</li>
                    <li>выбрать из каталога или ввести вручную;</li>
                    <li>отметить как купленное;</li>
                    <li>добавить купленное в холодильник;</li>
                    <li>создать транзакцию покупки.</li>
                </ul>
            </div>
            {screenshot_block("Умные покупки", "Список покупок с переносом в холодильник.", "08_shopping.png", "09_spisok_pokupok.png")}
        </div>
        """
    ))

    slides.append(slide(
        title="Аналитика",
        subtitle="Сводка по питанию, покупкам, списаниям и истории",
        content=f"""
        <div class="grid-4">
            {metric("ккал", "съедено сегодня", "🍽️")}
            {metric("история", "приготовленные блюда", "📜")}
            {metric("покупки", "купленные продукты", "🛒")}
            {metric("списания", "движение продуктов", "📉")}
        </div>
        {screenshot_block("Аналитика", "Общий обзор данных приложения.", "09_analytics.png")}
        """
    ))

    slides.append(slide(
        title="Свои рецепты",
        subtitle="Пользовательская книга рецептов",
        content=f"""
        <div class="grid-3">
            {card("Добавить рецепт", "Название, категория, время, калории, БЖУ.", "📝")}
            {card("Ингредиенты и шаги", "Можно сохранить полный текст рецепта.", "🥣")}
            {card("Использовать дальше", "Добавить в дневник или любимые блюда.", "❤️")}
        </div>
        <div class="note">
            Это основа для будущей функции: включать пользовательские рецепты в автоматическое меню.
        </div>
        """
    ))

    slides.append(slide(
        title="Облако и постоянная база",
        subtitle="Streamlit Cloud + Supabase",
        content=f"""
        <div class="architecture">
            <div class="arch-box">Пользователь<br><span>Телефон / ПК</span></div>
            <div class="arch-arrow">→</div>
            <div class="arch-box">Streamlit Cloud<br><span>Веб-приложение</span></div>
            <div class="arch-arrow">→</div>
            <div class="arch-box">Supabase<br><span>PostgreSQL база</span></div>
        </div>
        <div class="grid-2">
            {card("Доступ с любого устройства", "Приложение работает по ссылке из браузера.", "🌍")}
            {card("Данные не сбрасываются", "Продукты, покупки, дневник и история хранятся в Supabase.", "🗄️")}
        </div>
        """
    ))

    slides.append(slide(
        title="Безопасность",
        subtitle="Простой семейный вход по PIN",
        content=f"""
        <div class="grid-2">
            {card("PIN-код", "Приложение закрыто от случайных пользователей по ссылке.", "🔐")}
            {card("Семейный режим", "Можно войти как Мишка или Мединка и переключаться между пользователями.", "👨‍👩‍👧")}
        </div>
        <div class="note">
            PIN-коды хранятся в Streamlit Secrets. Это базовая защита для семейного приложения.
        </div>
        """
    ))

    slides.append(slide(
        title="Мобильная версия",
        subtitle="Приложение можно использовать как PWA-подход через браузер",
        content=f"""
        <div class="grid-2">
            {screenshot_block("Мобильный вид", "Приложение можно добавить на главный экран телефона.", "11_mobile.png", "02_fast_screen.png")}
            <div>
                <h2>Как установить</h2>
                <ul>
                    <li>Android: Chrome → ⋮ → Добавить на главный экран;</li>
                    <li>iPhone: Safari → Поделиться → На экран Домой;</li>
                    <li>после этого открывается почти как приложение.</li>
                </ul>
            </div>
        </div>
        """
    ))

    slides.append(slide(
        title="Стресс-тест",
        subtitle="Проверка связок приложения и облачной базы",
        content=f"""
        <div class="grid-3">
            {card("База", "Проверяется подключение к Supabase.", "🗄️")}
            {card("Запись", "Создаются и удаляются тестовые продукты, покупки, рецепты.", "✍️")}
            {card("Меню", "Проверяется построение меню для Мишки и Мединки.", "🗓️")}
        </div>
        {screenshot_block("Стресс-тест", "Все базовые связки прошли проверку.", "10_stress.png")}
        <div class="success">Все базовые связки прошли стресс-тест ✅</div>
        """
    ))

    slides.append(slide(
        title="Техническая архитектура",
        subtitle="Основные файлы и роли компонентов",
        content=f"""
        <div class="tech-list">
            <div><b>app.py</b><span>основной интерфейс Streamlit</span></div>
            <div><b>database.py</b><span>работа с SQLite локально и Supabase/PostgreSQL в облаке</span></div>
            <div><b>settings.py</b><span>название, версия, пользователи, настройки</span></div>
            <div><b>recipes.py</b><span>рецепты и логика совпадения продуктов</span></div>
            <div><b>product_catalog.py</b><span>каталог продуктов, категории, калории, сроки хранения</span></div>
            <div><b>dish_catalog.py</b><span>метаданные блюд: история, происхождение, факты</span></div>
            <div><b>menu_engine.py</b><span>персональное меню, покупки для меню, принятие меню</span></div>
            <div><b>demo_data.py</b><span>демо-данные для проверки приложения</span></div>
        </div>
        """
    ))

    slides.append(slide(
        title="Дизайн-система",
        subtitle="Современный визуальный стиль внутри Streamlit",
        content=f"""
        <div class="grid-3">
            {card("Карточки", "Белые блоки с мягкими тенями и скруглениями.", "▢")}
            {card("Цветовые статусы", "Зелёный, жёлтый, красный для состояния продуктов и меню.", "🎨")}
            {card("Иконки и emoji", "Быстрое визуальное распознавание разделов и блюд.", "✨")}
            {card("Мобильные кнопки", "Крупные кнопки для удобного нажатия на телефоне.", "📱")}
            {card("Бейджи", "Калории, категории, статусы, избранное.", "🏷️")}
            {card("Быстрый экран", "Минимум лишнего, максимум нужных действий.", "⚡")}
        </div>
        """
    ))

    slides.append(slide(
        title="Текущий статус",
        subtitle="Что уже готово и протестировано",
        content=f"""
        <div class="grid-4">
            {metric("✅", "облачная версия", "☁️")}
            {metric("✅", "Supabase база", "🗄️")}
            {metric("✅", "мобильный доступ", "📱")}
            {metric("✅", "PIN-вход", "🔐")}
        </div>
        <div class="success">
            Приложение опубликовано, открывается с любого устройства и прошло стресс-тест базовых связок.
        </div>
        """
    ))

    slides.append(slide(
        title="Дорожная карта",
        subtitle="Что можно развивать дальше",
        content=f"""
        <div class="roadmap">
            <div>
                <h3>v1.3</h3>
                <p>Ускорение: кэширование страниц, облегчённая главная, оптимизация Supabase-запросов.</p>
            </div>
            <div>
                <h3>v1.4</h3>
                <p>AI-рецепты: запросы вроде «ужин на 500 ккал из того, что есть».</p>
            </div>
            <div>
                <h3>v1.5</h3>
                <p>Фото чеков и продуктов: распознавание покупок и добавление в холодильник.</p>
            </div>
            <div>
                <h3>v2.0</h3>
                <p>Нативное мобильное приложение или WebView APK для Android.</p>
            </div>
        </div>
        """
    ))

    slides.append(slide(
        title="Итог",
        subtitle="Умный холодильник Мединки — уже рабочее семейное облачное приложение",
        class_name="final",
        content=f"""
        <div class="final-box">
            <div class="final-emoji">🥦</div>
            <h2>{APP_NAME}</h2>
            <p>
                Приложение объединяет холодильник, рецепты, меню, покупки,
                дневник питания, историю и аналитику в одном семейном сервисе.
            </p>
            <div class="badge">Разработка: {DEVELOPER}</div>
            <div class="badge">Версия презентации: {APP_VERSION}</div>
        </div>
        """
    ))

    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>{APP_NAME} — презентация</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #eef3f0;
            color: #163020;
        }}

        .slide {{
            width: 100%;
            min-height: 100vh;
            padding: 38px;
            page-break-after: always;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .slide-inner {{
            width: 100%;
            max-width: 1180px;
            min-height: 680px;
            background: #ffffff;
            border-radius: 34px;
            padding: 46px;
            box-shadow: 0 24px 70px rgba(22, 48, 32, 0.12);
            border: 1px solid #e2eee7;
            position: relative;
            overflow: hidden;
        }}

        .cover .slide-inner,
        .final .slide-inner {{
            background: linear-gradient(135deg, #163020, #2f6b45);
            color: white;
        }}

        h1 {{
            font-size: 46px;
            line-height: 1.05;
            margin: 0 0 14px;
            letter-spacing: -1.2px;
        }}

        h2 {{
            font-size: 28px;
            margin: 0 0 16px;
        }}

        h3 {{
            margin: 0 0 10px;
            font-size: 21px;
        }}

        p, li {{
            font-size: 18px;
            line-height: 1.5;
        }}

        ul {{
            padding-left: 22px;
        }}

        .subtitle {{
            font-size: 22px;
            color: #5c6b63;
            margin-bottom: 34px;
        }}

        .cover .subtitle,
        .final .subtitle {{
            color: #dff5e8;
        }}

        .cover-grid {{
            display: grid;
            grid-template-columns: 1.4fr 0.6fr;
            gap: 30px;
            align-items: center;
            margin-top: 60px;
        }}

        .cover-emoji {{
            font-size: 170px;
            text-align: center;
        }}

        .cover-url {{
            margin-top: 26px;
            font-size: 18px;
            color: #dff5e8;
            word-break: break-all;
        }}

        .badge {{
            display: inline-block;
            padding: 9px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            margin: 6px 6px 6px 0;
            font-weight: 700;
        }}

        .footer-note {{
            position: absolute;
            bottom: 32px;
            left: 46px;
            color: rgba(255,255,255,0.75);
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 22px;
            align-items: start;
        }}

        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
        }}

        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
        }}

        .card, .person-card, .metric, .screenshot-block, .screenshot-placeholder {{
            background: #f8fbf9;
            border: 1px solid #e4eee8;
            border-radius: 24px;
            padding: 22px;
            box-shadow: 0 12px 30px rgba(22, 48, 32, 0.06);
        }}

        .card-icon {{
            font-size: 34px;
            margin-bottom: 12px;
        }}

        .card p {{
            color: #5c6b63;
            margin-bottom: 0;
        }}

        .person-emoji {{
            font-size: 60px;
            margin-bottom: 14px;
        }}

        .metric {{
            text-align: center;
            min-height: 150px;
        }}

        .metric-icon {{
            font-size: 32px;
        }}

        .metric-value {{
            font-size: 42px;
            font-weight: 900;
            margin-top: 12px;
            color: #2f6b45;
        }}

        .metric-label {{
            font-size: 15px;
            color: #5c6b63;
            margin-top: 8px;
        }}

        .screenshot-block img {{
            width: 100%;
            max-height: 420px;
            object-fit: contain;
            border-radius: 18px;
            border: 1px solid #e0e8e3;
            background: #fff;
        }}

        .screenshot-title {{
            font-size: 19px;
            font-weight: 900;
            margin-bottom: 12px;
        }}

        .caption {{
            font-size: 14px;
            color: #64736a;
            margin-top: 10px;
            line-height: 1.4;
        }}

        .screenshot-placeholder {{
            min-height: 320px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
            border-style: dashed;
        }}

        .placeholder-icon {{
            font-size: 70px;
            margin-bottom: 16px;
        }}

        .note {{
            margin-top: 22px;
            padding: 20px 22px;
            border-radius: 22px;
            background: #e8f1ff;
            color: #1b4d8f;
            font-size: 18px;
            line-height: 1.5;
        }}

        .success {{
            margin-top: 24px;
            padding: 20px 22px;
            border-radius: 22px;
            background: #e7f8ef;
            color: #147a3d;
            font-size: 22px;
            font-weight: 900;
            text-align: center;
        }}

        .architecture {{
            display: grid;
            grid-template-columns: 1fr auto 1fr auto 1fr;
            gap: 18px;
            align-items: center;
            margin: 45px 0;
        }}

        .arch-box {{
            background: #f8fbf9;
            border: 1px solid #e4eee8;
            border-radius: 26px;
            padding: 30px;
            text-align: center;
            font-size: 25px;
            font-weight: 900;
        }}

        .arch-box span {{
            display: block;
            margin-top: 8px;
            font-size: 16px;
            color: #5c6b63;
            font-weight: 500;
        }}

        .arch-arrow {{
            font-size: 32px;
            color: #2f6b45;
            font-weight: 900;
        }}

        .tech-list {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }}

        .tech-list div {{
            background: #f8fbf9;
            border: 1px solid #e4eee8;
            border-radius: 20px;
            padding: 18px;
        }}

        .tech-list b {{
            display: block;
            font-size: 20px;
            color: #163020;
            margin-bottom: 6px;
        }}

        .tech-list span {{
            color: #5c6b63;
            font-size: 16px;
        }}

        .roadmap {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
            margin-top: 40px;
        }}

        .roadmap div {{
            background: #f8fbf9;
            border: 1px solid #e4eee8;
            border-radius: 24px;
            padding: 22px;
        }}

        .roadmap h3 {{
            color: #2f6b45;
            font-size: 26px;
        }}

        .final-box {{
            text-align: center;
            max-width: 760px;
            margin: 70px auto 0;
        }}

        .final-emoji {{
            font-size: 120px;
            margin-bottom: 20px;
        }}

        .final-box p {{
            color: #e4f7ec;
            font-size: 23px;
        }}

        @media print {{
            body {{
                background: white;
            }}

            .slide {{
                min-height: 100vh;
                padding: 0;
            }}

            .slide-inner {{
                min-height: 100vh;
                border-radius: 0;
                box-shadow: none;
                border: none;
            }}
        }}
    </style>
</head>
<body>
    {''.join(slides)}
</body>
</html>
"""

    return html


def save_pdf_with_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("Playwright не установлен.")
        print("Можно сделать PDF через браузер: открыть presentation_medinki.html → Ctrl+P → Save as PDF.")
        print("Или установить:")
        print("python -m pip install playwright")
        print("python -m playwright install chromium")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(OUT_HTML.resolve().as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(OUT_PDF),
            format="A4",
            landscape=True,
            print_background=True,
            margin={
                "top": "0mm",
                "bottom": "0mm",
                "left": "0mm",
                "right": "0mm",
            }
        )
        browser.close()

    print(f"PDF создан: {OUT_PDF}")


def main():
    html = build_html()
    OUT_HTML.write_text(html, encoding="utf-8")

    print(f"HTML-презентация создана: {OUT_HTML}")
    print("")
    print("Чтобы открыть:")
    print(f"Открой файл: {OUT_HTML.name}")
    print("")
    print("Чтобы сделать PDF вручную:")
    print("1. Открой presentation_medinki.html в Chrome/Edge.")
    print("2. Нажми Ctrl+P.")
    print("3. Printer: Save as PDF / Сохранить как PDF.")
    print("4. Layout: Landscape / Альбомная.")
    print("5. Background graphics: включить.")
    print("6. Save.")
    print("")

    if "--pdf" in sys.argv:
        save_pdf_with_playwright()


if __name__ == "__main__":
    main()