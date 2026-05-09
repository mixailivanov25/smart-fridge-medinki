from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"
CATALOG = ROOT / "v2_catalog_data.py"


CATALOG_CODE = r'''
from datetime import date, timedelta


PRODUCT_CATALOG_RAW = """
апельсин|🍊|Фрукты|шт|47|0.9|0.1|11.8|14|Цитрус для перекуса и сока
яблоко|🍎|Фрукты|шт|52|0.3|0.2|14|Универсальный фрукт для перекуса
банан|🍌|Фрукты|шт|89|1.1|0.3|23|Быстрый источник энергии
груша|🍐|Фрукты|шт|57|0.4|0.1|15|Сладкий фрукт для перекуса
киви|🥝|Фрукты|шт|61|1.1|0.5|15|Фрукт с витамином C
лимон|🍋|Фрукты|шт|29|1.1|0.3|9|Для чая, соусов и маринадов
мандарины|🍊|Фрукты|шт|53|0.8|0.3|13|Сладкие цитрусы
виноград|🍇|Фрукты|г|69|0.7|0.2|18|Сладкая ягода для десертов
арбуз|🍉|Фрукты|кг|30|0.6|0.2|8|Летний сочный продукт
дыня|🍈|Фрукты|кг|34|0.8|0.2|8|Сладкая летняя дыня
клубника|🍓|Ягоды|г|32|0.7|0.3|7.7|5|Ягода для завтраков и десертов
малина|🍓|Ягоды|г|52|1.2|0.7|12|4|Ягода для каш и творога
черника|🫐|Ягоды|г|57|0.7|0.3|14|6|Ягода для завтраков
смородина|🫐|Ягоды|г|44|1.0|0.4|7.3|5|Кислая ягода для компотов
картофель|🥔|Овощи|кг|77|2.0|0.1|17|30|База для гарниров и супов
морковь|🥕|Овощи|шт|41|0.9|0.2|10|21|Для супов, салатов и гарниров
лук|🧅|Овощи|шт|40|1.1|0.1|9|30|База для большинства блюд
чеснок|🧄|Овощи|шт|149|6.4|0.5|33|60|Ароматная добавка
помидоры|🍅|Овощи|г|18|0.9|0.2|3.9|7|Для салатов и соусов
огурцы|🥒|Овощи|г|15|0.7|0.1|3.6|7|Для салатов и перекусов
перец болгарский|🫑|Овощи|шт|31|1.0|0.3|6|10|Для салатов, жарки и запекания
капуста белокочанная|🥬|Овощи|кг|25|1.3|0.1|6|30|Для салатов, супов и тушения
капуста пекинская|🥬|Овощи|шт|16|1.2|0.2|3.2|10|Для лёгких салатов
брокколи|🥦|Овощи|г|34|2.8|0.4|7|7|Полезный зелёный гарнир
цветная капуста|🥦|Овощи|г|25|1.9|0.3|5|7|Для гарниров и запеканок
кабачок|🥒|Овощи|шт|24|0.6|0.3|4.6|10|Для тушения и оладий
баклажан|🍆|Овощи|шт|25|1.0|0.2|6|7|Для рагу и запекания
свекла|🫒|Овощи|шт|43|1.6|0.2|10|30|Для борща и салатов
тыква|🎃|Овощи|кг|26|1.0|0.1|6.5|45|Для супов и запекания
салат айсберг|🥬|Зелень|шт|14|0.9|0.1|3|5|Хрустящая зелень
укроп|🌿|Зелень|г|43|3.5|1.1|7|5|Ароматная зелень
петрушка|🌿|Зелень|г|36|3.0|0.8|6|5|Зелень для супов и салатов
зелёный лук|🌿|Зелень|г|32|1.8|0.2|7|5|Свежая добавка
молоко|🥛|Молочные продукты|л|60|3.2|3.2|4.8|7|Для каш, омлетов и напитков
кефир|🥛|Молочные продукты|л|41|3.0|1.0|4|7|Кисломолочный напиток
йогурт натуральный|🥛|Молочные продукты|г|61|3.5|3.3|4.7|10|Для завтраков и соусов
творог 5%|🍚|Молочные продукты|г|121|17|5|2|5|Белковый продукт
сметана|🥣|Молочные продукты|г|206|2.8|20|3.2|10|Для супов и соусов
сыр твёрдый|🧀|Молочные продукты|г|350|25|27|2|21|Для бутербродов и блюд
сыр творожный|🧀|Молочные продукты|г|230|6|22|4|10|Для завтраков и закусок
масло сливочное|🧈|Молочные продукты|г|748|0.5|82|0.8|30|Для каш и выпечки
сливки|🥛|Молочные продукты|мл|206|2.5|20|3.7|7|Для соусов и десертов
яйца|🥚|Яйца|шт|157|12.7|10.9|0.7|25|Для завтраков и выпечки
куриная грудка|🍗|Мясо и птица|г|165|31|3.6|0|3|Нежирный белок
куриное бедро|🍗|Мясо и птица|г|185|19|12|0|3|Сочное мясо
курица целая|🍗|Мясо и птица|кг|190|18|13|0|3|Для запекания и супа
индейка филе|🦃|Мясо и птица|г|135|29|1.5|0|3|Диетический белок
говядина|🥩|Мясо и птица|г|250|26|15|0|4|Для тушения и стейков
свинина|🥩|Мясо и птица|г|270|16|23|0|4|Для жарки и запекания
фарш мясной|🥩|Мясо и птица|г|250|17|20|0|2|Для котлет и пасты
ветчина|🥓|Мясо и птица|г|145|21|6|1|7|Для бутербродов
бекон|🥓|Мясо и птица|г|541|37|42|1.4|7|Для завтраков
лосось|🐟|Рыба|г|208|20|13|0|2|Жирная рыба
треска|🐟|Рыба|г|82|18|0.7|0|2|Нежирная рыба
тунец консервированный|🐟|Консервы|шт|130|29|1|0|365|Белковая консерва
сардины|🐟|Консервы|шт|208|25|11|0|365|Рыбная консерва
креветки|🦐|Морепродукты|г|99|24|0.3|0.2|2|Морепродукты для салатов
кальмар|🦑|Морепродукты|г|92|15|1.4|3.1|2|Для салатов и жарки
рис|🍚|Крупы и паста|г|344|6.7|0.7|78|365|Базовый гарнир
гречка|🌾|Крупы и паста|г|313|12.6|3.3|62|365|Полезная крупа
овсянка|🥣|Крупы и паста|г|370|13|7|60|365|Для завтраков
пшено|🌾|Крупы и паста|г|348|11.5|3.3|69|365|Для каш
перловка|🌾|Крупы и паста|г|315|9.3|1.1|73|365|Для супов и гарниров
булгур|🌾|Крупы и паста|г|342|12|1.3|76|365|Для гарниров и салатов
кускус|🌾|Крупы и паста|г|376|12.8|0.6|77|365|Быстрый гарнир
макароны|🍝|Крупы и паста|г|350|12|1.5|72|365|Для пасты и гарниров
спагетти|🍝|Крупы и паста|г|350|12|1.5|72|365|Для итальянских блюд
мука пшеничная|🌾|Выпечка|г|334|10|1|70|365|Для выпечки
хлеб белый|🍞|Хлеб|шт|265|8|3.2|49|4|Для бутербродов
хлеб ржаной|🍞|Хлеб|шт|210|6|1.2|43|5|Ржаной хлеб
лаваш|🫓|Хлеб|шт|275|8|1.2|56|5|Для рулетов
тосты|🍞|Хлеб|шт|300|9|4|55|10|Для завтраков
фасоль консервированная|🫘|Консервы|шт|99|6|0.5|17|365|Для салатов и супов
кукуруза консервированная|🌽|Консервы|шт|86|3|1.2|19|365|Для салатов
горошек консервированный|🟢|Консервы|шт|73|5|0.4|12|365|Для салатов
томаты в собственном соку|🍅|Консервы|шт|22|1.1|0.2|4|365|Для соусов
оливки|🫒|Консервы|шт|115|0.8|10.7|6|365|Для салатов и закусок
замороженные овощи|🥦|Заморозка|г|65|3|0.5|10|180|Быстрый гарнир
замороженная ягода|🫐|Заморозка|г|50|1|0.3|12|180|Для каш и десертов
пельмени|🥟|Заморозка|г|275|11|12|30|120|Быстрый ужин
вареники|🥟|Заморозка|г|220|7|5|36|120|Быстрый обед
оливковое масло|🫒|Масла и соусы|мл|884|0|100|0|365|Для салатов
подсолнечное масло|🌻|Масла и соусы|мл|899|0|100|0|365|Для жарки
майонез|🥫|Масла и соусы|г|680|1|75|3|60|Соус для салатов
кетчуп|🍅|Масла и соусы|г|112|1.3|0.2|26|90|Томатный соус
соевый соус|🥫|Масла и соусы|мл|53|8|0.6|4.9|365|Для маринадов
горчица|🥫|Масла и соусы|г|143|9|6|12|180|Острый соус
мёд|🍯|Сладости|г|304|0.3|0|82|365|Для каш и чая
сахар|🍬|Сладости|г|387|0|0|100|365|Для напитков и выпечки
шоколад тёмный|🍫|Сладости|г|546|5|31|61|180|Десерт
печенье|🍪|Сладости|г|430|6|14|70|120|К чаю
чай|🍵|Напитки|упак.|1|0|0|0|365|Напиток
кофе|☕|Напитки|упак.|2|0|0|0|365|Напиток
сок яблочный|🧃|Напитки|л|46|0.1|0|11|180|Фруктовый напиток
вода минеральная|💧|Напитки|л|0|0|0|0|365|Вода
соль|🧂|Специи|г|0|0|0|0|365|Базовая специя
перец чёрный|🌶️|Специи|г|251|10|3.3|64|365|Специя
паприка|🌶️|Специи|г|282|14|13|54|365|Специя
корица|🧂|Специи|г|247|4|1.2|81|365|Для десертов и каш
лавровый лист|🌿|Специи|г|313|8|8|75|365|Для супов
"""


RECIPE_CATALOG = [
    {"name": "Омлет", "emoji": "🍳", "category": "Завтрак", "time": "12 минут", "calories": 320, "description": "Нежный омлет на молоке.", "ingredients": "яйца, молоко, соль"},
    {"name": "Яичница с помидорами", "emoji": "🍳", "category": "Завтрак", "time": "10 минут", "calories": 280, "description": "Быстрый завтрак из яиц и овощей.", "ingredients": "яйца, помидоры, зелень"},
    {"name": "Овсянка на молоке", "emoji": "🥣", "category": "Завтрак", "time": "10 минут", "calories": 350, "description": "Сытный завтрак с медленными углеводами.", "ingredients": "овсянка, молоко, фрукты"},
    {"name": "Творог с фруктами", "emoji": "🍚", "category": "Завтрак", "time": "5 минут", "calories": 300, "description": "Белковый завтрак или перекус.", "ingredients": "творог, фрукты, мёд"},
    {"name": "Сырники", "emoji": "🥞", "category": "Завтрак", "time": "25 минут", "calories": 420, "description": "Домашние сырники из творога.", "ingredients": "творог, яйцо, мука"},
    {"name": "Курица с рисом", "emoji": "🍗", "category": "Обед", "time": "35 минут", "calories": 560, "description": "Сытное домашнее блюдо.", "ingredients": "курица, рис, морковь, лук"},
    {"name": "Гречка с курицей", "emoji": "🍗", "category": "Обед", "time": "35 минут", "calories": 520, "description": "Простое блюдо с крупой и белком.", "ingredients": "гречка, курица, лук"},
    {"name": "Паста с курицей", "emoji": "🍝", "category": "Обед", "time": "30 минут", "calories": 610, "description": "Паста с курицей и соусом.", "ingredients": "макароны, курица, сливки"},
    {"name": "Паста с тунцом", "emoji": "🍝", "category": "Обед", "time": "20 минут", "calories": 540, "description": "Быстрая паста из консервированного тунца.", "ingredients": "макароны, тунец, томаты"},
    {"name": "Борщ", "emoji": "🍲", "category": "Суп", "time": "90 минут", "calories": 330, "description": "Классический домашний суп.", "ingredients": "свекла, капуста, мясо, картофель"},
    {"name": "Куриный суп", "emoji": "🍲", "category": "Суп", "time": "60 минут", "calories": 280, "description": "Лёгкий суп с курицей.", "ingredients": "курица, картофель, морковь, лук"},
    {"name": "Овощной суп", "emoji": "🥦", "category": "Суп", "time": "35 минут", "calories": 190, "description": "Лёгкий суп из овощей.", "ingredients": "овощи, картофель, зелень"},
    {"name": "Жареный картофель", "emoji": "🥔", "category": "Ужин", "time": "30 минут", "calories": 420, "description": "Простое домашнее блюдо.", "ingredients": "картофель, лук, масло"},
    {"name": "Картофельное пюре", "emoji": "🥔", "category": "Гарнир", "time": "30 минут", "calories": 250, "description": "Нежный гарнир.", "ingredients": "картофель, молоко, масло"},
    {"name": "Рис с овощами", "emoji": "🍚", "category": "Гарнир", "time": "25 минут", "calories": 310, "description": "Гарнир или лёгкий ужин.", "ingredients": "рис, замороженные овощи"},
    {"name": "Гречка с грибами", "emoji": "🌾", "category": "Гарнир", "time": "30 минут", "calories": 340, "description": "Ароматная гречка.", "ingredients": "гречка, грибы, лук"},
    {"name": "Салат с тунцом", "emoji": "🥗", "category": "Салат", "time": "15 минут", "calories": 290, "description": "Лёгкий белковый салат.", "ingredients": "тунец, овощи, зелень"},
    {"name": "Овощной салат", "emoji": "🥗", "category": "Салат", "time": "10 минут", "calories": 120, "description": "Свежий салат.", "ingredients": "помидоры, огурцы, зелень"},
    {"name": "Салат с курицей", "emoji": "🥗", "category": "Салат", "time": "20 минут", "calories": 360, "description": "Сытный салат.", "ingredients": "курица, салат, овощи"},
    {"name": "Запечённая рыба", "emoji": "🐟", "category": "Ужин", "time": "35 минут", "calories": 380, "description": "Рыба в духовке.", "ingredients": "рыба, лимон, специи"},
    {"name": "Лосось с овощами", "emoji": "🐟", "category": "Ужин", "time": "30 минут", "calories": 520, "description": "Полезный ужин.", "ingredients": "лосось, овощи"},
    {"name": "Котлеты домашние", "emoji": "🥩", "category": "Ужин", "time": "45 минут", "calories": 480, "description": "Домашние котлеты.", "ingredients": "фарш, лук, яйцо"},
    {"name": "Тефтели с рисом", "emoji": "🍚", "category": "Ужин", "time": "50 минут", "calories": 520, "description": "Сытное домашнее блюдо.", "ingredients": "фарш, рис, томатный соус"},
    {"name": "Плов", "emoji": "🍚", "category": "Обед", "time": "70 минут", "calories": 650, "description": "Рис с мясом и овощами.", "ingredients": "рис, мясо, морковь, лук"},
    {"name": "Овощное рагу", "emoji": "🥦", "category": "Ужин", "time": "40 минут", "calories": 260, "description": "Тушёные овощи.", "ingredients": "кабачок, баклажан, перец, томаты"},
]


def _to_float(value, default=0.0):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return default


def _to_int(value, default=7):
    try:
        return int(float(str(value).replace(",", ".")))
    except Exception:
        return default


def parse_product_catalog():
    items = []

    for raw in PRODUCT_CATALOG_RAW.strip().splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue

        parts = raw.split("|")

        if len(parts) < 10:
            continue

        name, emoji, category, unit, calories, protein, fat, carbs, storage_days, description = parts[:10]

        items.append({
            "name": name.strip(),
            "emoji": emoji.strip() or "🧺",
            "category": category.strip() or "Другое",
            "unit": unit.strip() or "шт",
            "calories_per_100g": _to_float(calories),
            "protein": _to_float(protein),
            "fat": _to_float(fat),
            "carbs": _to_float(carbs),
            "storage_days": _to_int(storage_days),
            "description": description.strip(),
        })

    return items


PRODUCT_CATALOG = parse_product_catalog()
PRODUCT_CATEGORIES = sorted({item["category"] for item in PRODUCT_CATALOG})


def default_products_for_seed(limit=20):
    result = []
    for item in PRODUCT_CATALOG[:limit]:
        result.append((
            item["name"],
            1,
            item["unit"],
            item["calories_per_100g"],
            item["category"],
            date.today() + timedelta(days=item["storage_days"]),
            item["emoji"],
        ))
    return result
'''


FRIDGE_CODE = r'''
def page_fridge():
    products = get_products()

    hero(
        "Холодильник",
        "Продукты как карточки: фото, количество, сроки годности и быстрые действия.",
        "🧊",
    )

    tab_catalog, tab_manual, tab_cards, tab_table = st.tabs(["Каталог", "Вручную", "Карточки", "Таблица"])

    with tab_catalog:
        st.markdown("## 🧺 Большой каталог продуктов")
        st.caption("Выбери продукт из каталога, укажи количество и срок годности — он попадёт в холодильник.")

        categories = ["Все категории"] + PRODUCT_CATEGORIES

        c1, c2 = st.columns([1, 2])

        with c1:
            selected_category = st.selectbox("Категория", categories, key="catalog_category_v2")

        with c2:
            search = st.text_input("Поиск", placeholder="Например: молоко, курица, рис", key="catalog_search_v2")

        filtered = PRODUCT_CATALOG

        if selected_category != "Все категории":
            filtered = [p for p in filtered if p["category"] == selected_category]

        if search.strip():
            q = search.strip().lower()
            filtered = [
                p for p in filtered
                if q in p["name"].lower()
                or q in p["category"].lower()
                or q in p["description"].lower()
            ]

        if not filtered:
            st.info("Ничего не найдено.")
        else:
            names = [
                f'{p["emoji"]} {p["name"]} · {p["category"]} · {int(p["calories_per_100g"])} ккал'
                for p in filtered
            ]

            selected_label = st.selectbox("Продукт", names, key="catalog_product_v2")
            item = filtered[names.index(selected_label)]

            st.markdown(
                f"""
<div class="v2-card">
    <div class="v2-photo">{item["emoji"]}</div>
    <h2>{item["name"]}</h2>
    <p>{item["description"]}</p>
    <span class="v2-chip v2-chip-green">{item["category"]}</span>
    <span class="v2-chip v2-chip-blue">{item["calories_per_100g"]} ккал на 100 г</span>
    <span class="v2-chip v2-chip-purple">Б {item["protein"]} · Ж {item["fat"]} · У {item["carbs"]}</span>
    <span class="v2-chip v2-chip-orange">хранение ~{item["storage_days"]} дн.</span>
</div>
""",
                unsafe_allow_html=True,
            )

            with st.form("add_from_catalog_v2"):
                c1, c2, c3 = st.columns(3)

                with c1:
                    quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)

                with c2:
                    unit = st.selectbox(
                        "Единица",
                        ["шт", "г", "кг", "мл", "л", "упак."],
                        index=["шт", "г", "кг", "мл", "л", "упак."].index(item["unit"]) if item["unit"] in ["шт", "г", "кг", "мл", "л", "упак."] else 0,
                    )

                with c3:
                    expiration_date = st.date_input(
                        "Срок годности",
                        value=date.today() + timedelta(days=int(item["storage_days"])),
                    )

                submitted = st.form_submit_button("🧊 Добавить из каталога", use_container_width=True)

            if submitted:
                add_product(
                    name=item["name"],
                    quantity=quantity,
                    unit=unit,
                    calories=item["calories_per_100g"],
                    category=item["category"],
                    expiration_date=expiration_date,
                    emoji=item["emoji"],
                    image_data=None,
                )
                st.success(f'Добавлено: {item["name"]}')
                st.rerun()

        with st.expander("Показать весь каталог таблицей"):
            st.dataframe(pd.DataFrame(PRODUCT_CATALOG), use_container_width=True, hide_index=True)

    with tab_manual:
        st.markdown("## ✍️ Добавить продукт вручную")

        with st.form("add_product_v2_manual"):
            c1, c2 = st.columns(2)

            with c1:
                name = st.text_input("Название", placeholder="Например: молоко")
                category = st.text_input("Категория", value="Другое")
                emoji = st.text_input("Emoji", value="🧺")
                expiration_date = st.date_input("Срок годности", value=date.today() + timedelta(days=7))

            with c2:
                quantity = st.number_input("Количество", min_value=0.0, value=1.0, step=0.1)
                unit = st.selectbox("Единица", ["шт", "г", "кг", "мл", "л", "упак."], key="manual_unit_v2")
                calories = st.number_input("Ккал на 100 г", min_value=0.0, value=0.0, step=1.0)
                photo = st.file_uploader("Фото продукта", type=["jpg", "jpeg", "png", "webp"])

            submitted = st.form_submit_button("➕ Добавить в холодильник", use_container_width=True)

        if submitted:
            if not name.strip():
                st.warning("Укажи название продукта.")
            else:
                add_product(
                    name=name.strip(),
                    quantity=quantity,
                    unit=unit,
                    calories=calories,
                    category=category,
                    expiration_date=expiration_date,
                    emoji=emoji or "🧺",
                    image_data=image_to_data_url(photo),
                )
                st.success("Продукт добавлен.")
                st.rerun()

    with tab_cards:
        if not products:
            st.info("Пока в холодильнике нет продуктов.")
        else:
            cols = st.columns(3)

            for i, p in enumerate(products):
                status, cls = expiry_status(p.get("expiration_date"))
                emoji = p.get("emoji") or "🧺"
                image = p.get("image_data")

                with cols[i % 3]:
                    if image:
                        photo_html = f'<div class="v2-photo"><img src="{image}"></div>'
                    else:
                        photo_html = f'<div class="v2-photo">{emoji}</div>'

                    st.markdown(
                        f"""
<div class="v2-card">
    {photo_html}
    <h2>{p.get("name")}</h2>
    <span class="v2-chip v2-chip-green">{p.get("quantity")} {p.get("unit")}</span>
    <span class="v2-chip v2-chip-blue">{p.get("calories_per_100g")} ккал</span>
    <span class="v2-chip {cls}">{status}</span>
    <p class="v2-label">{p.get("category") or "Другое"}</p>
</div>
""",
                        unsafe_allow_html=True,
                    )

                    if st.button("Удалить", key=f"delete_product_{p.get('id')}", use_container_width=True):
                        delete_product(p.get("id"))
                        st.rerun()

    with tab_table:
        if products:
            st.dataframe(pd.DataFrame(products), use_container_width=True, hide_index=True)
        else:
            st.info("Нет продуктов.")
'''


def backup(path: Path):
    backup_dir = ROOT / "backups" / f"upgrade_v20_catalogs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    if path.exists():
        target = backup_dir / path.name
        shutil.copy2(path, target)
        print(f"Backup saved: {target}")


def compile_py(path: Path):
    py_compile.compile(str(path), doraise=True)


def write_catalog_module():
    backup(CATALOG)
    CATALOG.write_text(CATALOG_CODE, encoding="utf-8")
    compile_py(CATALOG)
    print("v2_catalog_data.py written.")


def find_assignment_block(text: str, name: str):
    marker = f"{name} ="
    start = text.find(marker)

    if start == -1:
        return None

    bracket_start = text.find("[", start)

    if bracket_start == -1:
        return None

    depth = 0
    in_string = None
    escape = False
    triple = False

    i = bracket_start

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

        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                return start, end

        i += 1

    return None


def replace_assignment(text: str, name: str, replacement: str) -> str:
    block = find_assignment_block(text, name)

    if not block:
        print(f"{name} assignment not found, appending replacement.")
        return text + "\n\n" + replacement.strip() + "\n"

    start, end = block
    print(f"Replaced {name}.")
    return text[:start] + replacement.strip() + text[end:]


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


def ensure_import(text: str) -> str:
    import_line = "from v2_catalog_data import PRODUCT_CATALOG, PRODUCT_CATEGORIES, RECIPE_CATALOG, default_products_for_seed"

    if import_line in text:
        return text

    lines = text.splitlines()
    idx = find_safe_insert_after_imports(text)
    lines.insert(idx, import_line)
    print("Added v2_catalog_data import.")
    return "\n".join(lines) + "\n"


def replace_function(text: str, func_name: str, code: str) -> str:
    pattern = rf'(?ms)^def\s+{re.escape(func_name)}\s*\([^)]*\)\s*:\n.*?(?=^def\s+|^if\s+__name__\s*==|\Z)'

    new_text, count = re.subn(
        pattern,
        code.strip() + "\n\n",
        text,
        count=1,
    )

    if count:
        print(f"Replaced {func_name}()")
        return new_text

    print(f"{func_name}() not found, appended.")
    return text.rstrip() + "\n\n" + code.strip() + "\n"


def patch_app():
    if not APP.exists():
        raise FileNotFoundError("app.py not found")

    backup(APP)

    text = APP.read_text(encoding="utf-8")

    text = ensure_import(text)

    text = replace_assignment(
        text,
        "DEFAULT_PRODUCTS",
        "DEFAULT_PRODUCTS = default_products_for_seed(limit=20)"
    )

    text = replace_assignment(
        text,
        "DEFAULT_RECIPES",
        "DEFAULT_RECIPES = RECIPE_CATALOG"
    )

    text = replace_function(text, "page_fridge", FRIDGE_CODE)

    APP.write_text(text, encoding="utf-8")
    compile_py(APP)
    print("app.py syntax OK.")


def main():
    print("=== upgrade v2 catalogs ===")

    write_catalog_module()
    patch_app()

    print()
    print("Готово ✅")
    print("Добавлено:")
    print("- большой каталог продуктов;")
    print("- категории, калории, БЖУ, сроки хранения;")
    print("- добавление продукта из каталога в холодильник;")
    print("- расширенный каталог рецептов;")
    print("- холодильник теперь имеет вкладки: Каталог / Вручную / Карточки / Таблица.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
