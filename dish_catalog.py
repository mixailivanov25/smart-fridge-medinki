DISH_METADATA = {
    "Омлет": {
        "emoji": "🥚",
        "image_url": "",
        "origin": "Европейская кухня",
        "where_popular": "Франция, Европа, домашняя кухня по всему миру.",
        "history": "Омлет часто связывают с французской кухней, хотя блюда из взбитых яиц готовили в разных культурах задолго до современного рецепта.",
        "interesting_fact": "Классический французский омлет готовят нежным, без сильной корочки."
    },
    "Курица с рисом": {
        "emoji": "🍗",
        "image_url": "",
        "origin": "Домашняя кухня",
        "where_popular": "Во многих странах как базовое сытное блюдо.",
        "history": "Сочетание риса и курицы встречается во множестве кухонь: от плова до азиатских рисовых тарелок.",
        "interesting_fact": "Это одно из самых популярных блюд для meal prep — заготовки еды на несколько дней."
    },
    "Греческий салат": {
        "emoji": "🥗",
        "image_url": "",
        "origin": "Греция",
        "where_popular": "Греция, Средиземноморье, рестораны по всему миру.",
        "history": "Греческий салат, или хориатики, традиционно готовят из помидоров, огурцов, сыра фета, оливок и масла.",
        "interesting_fact": "В классическом варианте листья салата обычно не добавляют."
    },
    "Паста с курицей": {
        "emoji": "🍝",
        "image_url": "",
        "origin": "Итальянская и домашняя кухня",
        "where_popular": "Европа, США, домашняя кухня.",
        "history": "Паста с курицей — адаптация итальянской пасты под более сытный домашний формат.",
        "interesting_fact": "Можно сделать сливочную, томатную или сырную версию."
    },
    "Овсянка на молоке": {
        "emoji": "🥣",
        "image_url": "",
        "origin": "Северная Европа",
        "where_popular": "Великобритания, Скандинавия, Россия, фитнес-питание.",
        "history": "Овсяная каша стала популярной благодаря доступности овса и высокой питательности.",
        "interesting_fact": "Овсянка содержит медленные углеводы и хорошо насыщает."
    },
    "Овощной салат": {
        "emoji": "🥗",
        "image_url": "",
        "origin": "Домашняя кухня",
        "where_popular": "Практически по всему миру.",
        "history": "Свежие овощные салаты появились как простое сезонное блюдо из доступных овощей.",
        "interesting_fact": "Овощной салат легко адаптировать под продукты в холодильнике."
    },
}


def get_dish_metadata(dish_name):
    default = {
        "emoji": "🍽️",
        "image_url": "",
        "origin": "Домашняя кухня",
        "where_popular": "Популярно в домашнем питании.",
        "history": "Это блюдо можно адаптировать под продукты, которые есть в холодильнике.",
        "interesting_fact": "Состав блюда можно менять под вкус и цели питания."
    }

    return DISH_METADATA.get(dish_name, default)


def enrich_recipe(recipe):
    metadata = get_dish_metadata(recipe["name"])
    enriched = dict(recipe)
    enriched.update(metadata)
    return enriched


def get_enriched_recipes(recipes):
    return [enrich_recipe(recipe) for recipe in recipes]


def search_dish_metadata(query=""):
    query = query.lower().strip()
    items = []

    for dish_name, metadata in DISH_METADATA.items():
        row = {"name": dish_name, **metadata}

        if not query:
            items.append(row)
        else:
            haystack = " ".join([
                dish_name,
                metadata.get("origin", ""),
                metadata.get("where_popular", ""),
                metadata.get("history", ""),
                metadata.get("interesting_fact", "")
            ]).lower()

            if query in haystack:
                items.append(row)

    return sorted(items, key=lambda item: item["name"])
