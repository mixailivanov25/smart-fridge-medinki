from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import subprocess
import sys

ROOT = Path.cwd()
APP = ROOT / "app.py"


HERO_CODE = r'''
def hero(title, subtitle, icon="🥦"):
    st.markdown(
        f"""
<div class="v2-hero">
    <h1>{icon} {title}</h1>
    <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )
'''


METRIC_GRID_CODE = r'''
def metric_grid(products):
    total_products = len(products)

    attention = 0
    today_value = date.today()

    for p in products:
        exp = p.get("expiration_date")
        if exp:
            try:
                exp_date = date.fromisoformat(str(exp)[:10])
                if (exp_date - today_value).days <= 3:
                    attention += 1
            except Exception:
                pass

    calories_stock = 0

    for p in products:
        try:
            q = float(p.get("quantity") or 0)
            cal = float(p.get("calories_per_100g") or 0)
            unit = str(p.get("unit") or "")

            if unit in ["г", "мл"]:
                calories_stock += q / 100 * cal
            elif unit in ["кг", "л"]:
                calories_stock += q * 10 * cal
            else:
                calories_stock += cal
        except Exception:
            pass

    st.markdown(
        f"""
<div class="v2-grid-4">
    <div class="v2-card">
        <div class="v2-metric">{total_products}</div>
        <div class="v2-label">продуктов дома</div>
    </div>
    <div class="v2-card">
        <div class="v2-metric">{attention}</div>
        <div class="v2-label">требуют внимания</div>
    </div>
    <div class="v2-card">
        <div class="v2-metric">{len(DEFAULT_RECIPES)}</div>
        <div class="v2-label">идей блюд</div>
    </div>
    <div class="v2-card">
        <div class="v2-metric">{int(calories_stock)}</div>
        <div class="v2-label">ккал в запасах</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
'''


RENDER_TOP_NAV_CODE = r'''
def render_top_nav():
    render_nav_styles()

    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠 Сегодня"),
        ("fridge", "🧊 Холодильник"),
        ("scan", "📸 Сканер"),
        ("recipes", "🍳 Рецепты"),
        ("shopping", "🛒 Покупки"),
        ("diary", "📔 Дневник"),
        ("analytics", "📊 Аналитика"),
        ("settings", "⚙️ Настройки"),
    ]

    links = []

    for key, label in items:
        active = "active" if current == key else ""
        links.append(f'<a class="{active}" href="?tab={key}" target="_self">{label}</a>')

    st.markdown(
        f"""
<div class="v2-top-nav">
    {''.join(links)}
</div>
""",
        unsafe_allow_html=True,
    )
'''


BOTTOM_NAV_CODE = r'''
def bottom_nav():
    current = st.session_state.get("tab", "today")

    items = [
        ("today", "🏠", "Сегодня"),
        ("fridge", "🧊", "Холод."),
        ("scan", "📸", "Сканер"),
        ("recipes", "🍳", "Рецепты"),
        ("shopping", "🛒", "Покупки"),
    ]

    links = []

    for key, emoji, label in items:
        active = "active" if current == key else ""
        links.append(
            f'<a class="{active}" href="?tab={key}" target="_self"><span class="emoji">{emoji}</span><span>{label}</span></a>'
        )

    st.markdown(
        f"""
<div class="v2-bottom-nav">
    {''.join(links)}
</div>
""",
        unsafe_allow_html=True,
    )
'''


RENDER_ACTION_LINKS_CODE = r'''
def render_action_links():
    st.markdown(
        """
<div class="v2-action-grid">
    <a class="v2-action-link" href="?tab=scan" target="_self">📸 Сканировать</a>
    <a class="v2-action-link" href="?tab=fridge" target="_self">🧊 Холодильник</a>
    <a class="v2-action-link" href="?tab=recipes" target="_self">🍳 Рецепты</a>
    <a class="v2-action-link" href="?tab=shopping" target="_self">🛒 Покупки</a>
</div>
""",
        unsafe_allow_html=True,
    )
'''


def backup(path: Path):
    backup_dir = ROOT / "backups" / f"fix_raw_html_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    if path.exists():
        target = backup_dir / path.name
        shutil.copy2(path, target)
        print(f"Backup saved: {target}")


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


def remove_bom(text: str) -> str:
    return text.replace("\ufeff", "")


def main():
    if not APP.exists():
        print("app.py not found")
        raise SystemExit(1)

    print("=== Fix raw HTML rendering in v2 ===")

    backup(APP)

    text = APP.read_text(encoding="utf-8-sig")
    text = remove_bom(text)

    text = replace_function(text, "hero", HERO_CODE)
    text = replace_function(text, "metric_grid", METRIC_GRID_CODE)
    text = replace_function(text, "render_top_nav", RENDER_TOP_NAV_CODE)
    text = replace_function(text, "bottom_nav", BOTTOM_NAV_CODE)
    text = replace_function(text, "render_action_links", RENDER_ACTION_LINKS_CODE)

    APP.write_text(text, encoding="utf-8")

    py_compile.compile(str(APP), doraise=True)
    print("app.py syntax OK ✅")

    print()
    print("Готово ✅")
    print("HTML больше не должен отображаться как текст.")
    print()
    print("Запускаю приложение...")
    print()

    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=str(ROOT))


if __name__ == "__main__":
    main()
