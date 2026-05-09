import re
from collections import defaultdict

from settings import PEOPLE, PERSON_GENITIVE, PERSON_EMOJI

from database import (
    get_user_profile,
    get_favorite_dishes,
    get_products,
    reduce_product_quantity,
    add_cooking_history,
    create_accepted_week_menu,
    add_accepted_week_menu_item,
    add_product_transaction
)

from recipes import DAYS, get_recipe_matches, find_product, to_base_unit


def get_person_emoji(person):
    return PERSON_EMOJI.get(person, "👤")


def get_person_genitive(person):
    return PERSON_GENITIVE.get(person, person)


def split_text_items(text):
    if not text:
        return []
    parts = re.split(r"[,;\n]+", str(text).lower())
    return [part.strip() for part in parts if part.strip()]


def recipe_contains_terms(recipe, terms):
    if not terms:
        return False

    haystack = recipe["name"].lower() + " " + recipe.get("description", "").lower()

    for ingredient in recipe.get("ingredients", []):
        haystack += " " + ingredient.get("name", "").lower()
        haystack += " " + " ".join(ingredient.get("variants", [])).lower()

    for term in terms:
        if term and term in haystack:
            return True

    return False


def get_favorites_map(person):
    favorites = get_favorite_dishes(person)
    result = {}

    for row in favorites:
        favorite_id, row_person, dish_name, source, rating, notes, created_at = row
        result[dish_name.lower().strip()] = {
            "rating": int(rating),
            "notes": notes,
            "source": source
        }

    return result


def meal_slots_for_profile(meals_per_day):
    meals_per_day = int(meals_per_day)

    if meals_per_day <= 1:
        return ["Основной приём пищи"]
    if meals_per_day == 2:
        return ["Завтрак", "Ужин"]
    if meals_per_day == 3:
        return ["Завтрак", "Обед", "Ужин"]
    if meals_per_day == 4:
        return ["Завтрак", "Обед", "Ужин", "Перекус"]
    return ["Завтрак", "Обед", "Ужин", "Перекус", "Дополнительно"]


def preferred_categories_for_slot(slot):
    if slot == "Завтрак":
        return ["Завтрак"]
    if slot == "Обед":
        return ["Обед", "Салат"]
    if slot == "Ужин":
        return ["Ужин", "Обед", "Салат"]
    if slot in ["Перекус", "Дополнительно"]:
        return ["Перекус", "Завтрак"]
    return ["Обед", "Ужин", "Салат", "Завтрак", "Перекус"]


def score_recipe_for_person(item, slot, profile, favorites_map, used_counts, daily_calories):
    recipe = item["recipe"]
    person_name, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at = profile

    score = item["score"]

    if item["can_make"]:
        score += 20

    if recipe["category"] in preferred_categories_for_slot(slot):
        score += 30

    recipe_key = recipe["name"].lower().strip()

    if recipe_key in favorites_map:
        rating = favorites_map[recipe_key]["rating"]
        score += 40 + rating * 10

    if recipe_contains_terms(recipe, split_text_items(preferences)):
        score += 12

    if recipe_contains_terms(recipe, split_text_items(dislikes)):
        score -= 90

    if recipe_contains_terms(recipe, split_text_items(allergies)):
        score -= 250

    if protein_focus:
        if recipe_contains_terms(recipe, ["курица", "творог", "яйца", "тунец", "сыр", "индейка", "говядина"]):
            score += 12

    remaining_target = target_calories - daily_calories

    if recipe["calories"] <= remaining_target:
        score += 10
    else:
        score -= 8

    score -= used_counts[recipe["name"]] * 14

    return score


def build_personal_week_menu(person, products):
    profile = get_user_profile(person)

    if not profile:
        return None

    person_name, target_calories, goal, meals_per_day, protein_focus, preferences, dislikes, allergies, updated_at = profile
    matches = get_recipe_matches(products)
    favorites_map = get_favorites_map(person)
    used_counts = defaultdict(int)

    week = []
    slots = meal_slots_for_profile(int(meals_per_day))

    for day in DAYS:
        meals = []
        daily_calories = 0

        for slot in slots:
            best_item = None
            best_score = -999999

            for item in matches:
                score = score_recipe_for_person(
                    item=item,
                    slot=slot,
                    profile=profile,
                    favorites_map=favorites_map,
                    used_counts=used_counts,
                    daily_calories=daily_calories
                )

                if score > best_score:
                    best_score = score
                    best_item = item

            if best_item:
                recipe = best_item["recipe"]
                recipe_key = recipe["name"].lower().strip()
                favorite_info = favorites_map.get(recipe_key)

                meals.append({
                    "slot": slot,
                    "recipe": recipe,
                    "calories": recipe["calories"],
                    "can_make": best_item["can_make"],
                    "score": best_item["score"],
                    "missing": best_item["missing"],
                    "is_favorite": recipe_key in favorites_map,
                    "favorite_rating": favorite_info["rating"] if favorite_info else None,
                    "favorite_notes": favorite_info["notes"] if favorite_info else ""
                })

                daily_calories += recipe["calories"]
                used_counts[recipe["name"]] += 1

        diff = daily_calories - target_calories
        diff_percent = abs(diff) / target_calories if target_calories else 0

        if diff_percent <= 0.12:
            status = "✅ близко к цели"
            status_color = "green"
        elif diff < 0:
            status = "⚠️ ниже цели"
            status_color = "yellow"
        else:
            status = "🔥 выше цели"
            status_color = "red"

        week.append({
            "person": person,
            "day": day,
            "target_calories": target_calories,
            "meals": meals,
            "calories": daily_calories,
            "diff": diff,
            "status": status,
            "status_color": status_color
        })

    avg_calories = round(sum(day["calories"] for day in week) / len(week))
    avg_diff = avg_calories - target_calories
    favorites_used = sum(1 for day in week for meal in day["meals"] if meal["is_favorite"])

    return {
        "person": person,
        "profile": profile,
        "week": week,
        "avg_calories": avg_calories,
        "avg_diff": avg_diff,
        "favorites_used": favorites_used
    }


def build_all_personal_week_menus(products):
    return {person: build_personal_week_menu(person, products) for person in PEOPLE}


def build_shopping_list_for_menu(menu_data, products):
    if not menu_data:
        return []

    inventory = {}

    for product in products:
        product_id, name, quantity, unit, calories, category, exp_date = product
        base_amount, base_unit = to_base_unit(quantity, unit)
        inventory[product_id] = {"product": product, "amount": base_amount, "unit": base_unit}

    shopping = {}

    for day in menu_data["week"]:
        for meal in day["meals"]:
            recipe = meal["recipe"]

            for ingredient in recipe.get("ingredients", []):
                if ingredient.get("optional", False):
                    continue

                needed_amount, needed_unit = to_base_unit(ingredient["amount"], ingredient["unit"])
                product = find_product(products, ingredient["variants"])
                key = f"{ingredient['name']}|{needed_unit}"

                if not product:
                    shopping.setdefault(key, {"name": ingredient["name"], "amount": 0, "unit": needed_unit, "recipes": []})
                    shopping[key]["amount"] += needed_amount
                    if recipe["name"] not in shopping[key]["recipes"]:
                        shopping[key]["recipes"].append(recipe["name"])
                    continue

                product_id = product[0]

                if product_id not in inventory:
                    continue

                if inventory[product_id]["unit"] != needed_unit:
                    continue

                if inventory[product_id]["amount"] >= needed_amount:
                    inventory[product_id]["amount"] -= needed_amount
                else:
                    shortage = needed_amount - inventory[product_id]["amount"]
                    inventory[product_id]["amount"] = 0

                    shopping.setdefault(key, {"name": ingredient["name"], "amount": 0, "unit": needed_unit, "recipes": []})
                    shopping[key]["amount"] += shortage
                    if recipe["name"] not in shopping[key]["recipes"]:
                        shopping[key]["recipes"].append(recipe["name"])

    return list(shopping.values())


def combine_shopping_lists(*shopping_lists):
    combined = {}

    for shopping_list in shopping_lists:
        for item in shopping_list:
            key = f"{item['name']}|{item['unit']}"
            combined.setdefault(key, {"name": item["name"], "amount": 0, "unit": item["unit"], "recipes": []})
            combined[key]["amount"] += item["amount"]

            for recipe in item.get("recipes", []):
                if recipe not in combined[key]["recipes"]:
                    combined[key]["recipes"].append(recipe)

    return list(combined.values())


def convert_base_amount_to_product_unit(base_amount, base_unit, product_unit):
    _, product_base_unit = to_base_unit(1, product_unit)

    if base_unit != product_base_unit:
        return None

    product_unit = product_unit.lower().strip()

    if product_unit == "кг":
        return base_amount / 1000
    if product_unit == "л":
        return base_amount / 1000
    return base_amount


def spend_ingredient_for_menu(ingredient, recipe_name, person, day, meal_slot):
    current_products = get_products()
    product = find_product(current_products, ingredient["variants"])

    needed_base_amount, needed_base_unit = to_base_unit(ingredient["amount"], ingredient["unit"])

    if not product:
        return {
            "spent": False,
            "missing": True,
            "product_name": ingredient["name"],
            "amount": needed_base_amount,
            "unit": needed_base_unit,
            "reason": "нет в наличии"
        }

    product_id, product_name, product_quantity, product_unit, calories, category, exp_date = product
    product_base_amount, product_base_unit = to_base_unit(product_quantity, product_unit)

    if product_base_unit != needed_base_unit:
        return {
            "spent": False,
            "missing": True,
            "product_name": ingredient["name"],
            "amount": needed_base_amount,
            "unit": needed_base_unit,
            "reason": f"несовместимые единицы: нужно {needed_base_unit}, есть {product_unit}"
        }

    amount_in_product_unit = convert_base_amount_to_product_unit(needed_base_amount, needed_base_unit, product_unit)

    if product_base_amount >= needed_base_amount:
        reduce_product_quantity(product_id, amount_in_product_unit)

        add_product_transaction(
            product_id=product_id,
            product_name=product_name,
            change_amount=-amount_in_product_unit,
            unit=product_unit,
            action="spend",
            reason="accepted_week_menu",
            dish_name=recipe_name,
            person=person,
            day=day,
            meal_slot=meal_slot
        )

        return {
            "spent": True,
            "missing": False,
            "product_name": product_name,
            "amount": amount_in_product_unit,
            "unit": product_unit,
            "reason": ""
        }

    available_in_product_unit = product_quantity
    shortage_base = needed_base_amount - product_base_amount

    if available_in_product_unit > 0:
        reduce_product_quantity(product_id, available_in_product_unit)

        add_product_transaction(
            product_id=product_id,
            product_name=product_name,
            change_amount=-available_in_product_unit,
            unit=product_unit,
            action="spend_partial",
            reason="accepted_week_menu",
            dish_name=recipe_name,
            person=person,
            day=day,
            meal_slot=meal_slot
        )

    return {
        "spent": True,
        "missing": True,
        "product_name": product_name,
        "amount": shortage_base,
        "unit": needed_base_unit,
        "reason": "частично списано, не хватило"
    }


def accept_week_menus(menu_mishka, menu_medinka, title="Принятое меню на неделю", notes=""):
    menu_id = create_accepted_week_menu(title=title, notes=notes)

    report = {
        "menu_id": menu_id,
        "spent": [],
        "missing": [],
        "items_saved": 0
    }

    all_menus = []
    if menu_mishka:
        all_menus.append(menu_mishka)
    if menu_medinka:
        all_menus.append(menu_medinka)

    for menu_data in all_menus:
        person = menu_data["person"]

        for day in menu_data["week"]:
            day_name = day["day"]

            for meal in day["meals"]:
                recipe = meal["recipe"]
                meal_slot = meal["slot"]

                add_accepted_week_menu_item(
                    menu_id=menu_id,
                    person=person,
                    day=day_name,
                    meal_slot=meal_slot,
                    dish_name=recipe["name"],
                    calories=recipe["calories"],
                    is_favorite=meal.get("is_favorite", False)
                )

                report["items_saved"] += 1
                spent_strings = []

                for ingredient in recipe.get("ingredients", []):
                    if ingredient.get("optional", False):
                        continue

                    result = spend_ingredient_for_menu(
                        ingredient=ingredient,
                        recipe_name=recipe["name"],
                        person=person,
                        day=day_name,
                        meal_slot=meal_slot
                    )

                    if result["spent"] and not result["missing"]:
                        report["spent"].append({
                            "person": person,
                            "day": day_name,
                            "meal_slot": meal_slot,
                            "dish_name": recipe["name"],
                            "product_name": result["product_name"],
                            "amount": result["amount"],
                            "unit": result["unit"]
                        })

                        spent_strings.append(f"{result['product_name']}: {round(result['amount'], 2)} {result['unit']}")

                    if result["missing"]:
                        report["missing"].append({
                            "person": person,
                            "day": day_name,
                            "meal_slot": meal_slot,
                            "dish_name": recipe["name"],
                            "product_name": result["product_name"],
                            "amount": result["amount"],
                            "unit": result["unit"],
                            "reason": result["reason"]
                        })

                ingredients_used = ", ".join(spent_strings) if spent_strings else "Ингредиенты не списаны"

                add_cooking_history(
                    dish_name=f"{recipe['name']} — {person}, {day_name}, {meal_slot}",
                    ingredients_used=ingredients_used,
                    calories=recipe["calories"]
                )

    return report
