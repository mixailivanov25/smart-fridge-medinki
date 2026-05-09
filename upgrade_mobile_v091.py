from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import subprocess


PROJECT_DIR = Path(__file__).resolve().parent

APP_FILE = PROJECT_DIR / "app.py"
SETTINGS_FILE = PROJECT_DIR / "settings.py"


def run(command, check=False):
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


def backup_files():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_DIR / f"backup_before_mobile_v091_{timestamp}"
    backup_dir.mkdir(exist_ok=True)

    for file_path in [APP_FILE, SETTINGS_FILE]:
        if file_path.exists():
            shutil.copy2(file_path, backup_dir / file_path.name)

    print(f"📦 Резервная копия создана: {backup_dir.name}")
    return backup_dir


def update_settings():
    if not SETTINGS_FILE.exists():
        print("❌ settings.py не найден")
        return False

    text = SETTINGS_FILE.read_text(encoding="utf-8")

    versions = [
        "v0.6",
        "v0.7",
        "v0.8",
        "v0.9",
        "v0.9.0"
    ]

    changed = False

    for version in versions:
        old = f'APP_VERSION = "{version}"'
        if old in text:
            text = text.replace(old, 'APP_VERSION = "v0.9.1"')
            changed = True

    if 'APP_VERSION = "v0.9.1"' not in text:
        text += '\nAPP_VERSION = "v0.9.1"\n'
        changed = True

    SETTINGS_FILE.write_text(text, encoding="utf-8")

    if changed:
        print("✅ settings.py обновлён до v0.9.1")
    else:
        print("ℹ️ settings.py уже был v0.9.1")

    return True


def build_mobile_css():
    return r'''

    /* -----------------------------
       v0.9.1 Mobile Polish
       ----------------------------- */

    .mobile-install-card {
        background: linear-gradient(135deg, #f1fff6, #ffffff);
        padding: 20px 22px;
        border-radius: 24px;
        border: 1px solid #d7f5e2;
        box-shadow: 0 12px 30px rgba(22, 48, 32, 0.07);
        margin-bottom: 18px;
    }

    .mobile-install-card h3 {
        margin-bottom: 8px;
        color: #163020;
    }

    .mobile-step {
        display: inline-block;
        background: #e7f8ef;
        color: #147a3d;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    .mobile-home-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-bottom: 18px;
    }

    .mobile-action-card {
        background: white;
        border: 1px solid #e8f3ed;
        border-radius: 22px;
        padding: 18px;
        box-shadow: 0 10px 26px rgba(22, 48, 32, 0.07);
        text-align: center;
    }

    .mobile-action-card .icon {
        font-size: 34px;
        margin-bottom: 8px;
    }

    .mobile-action-card .title {
        font-weight: 900;
        color: #163020;
        font-size: 16px;
    }

    .mobile-action-card .text {
        color: #6b756e;
        font-size: 13px;
        margin-top: 4px;
    }

    /* Make Streamlit buttons more touch-friendly */
    div.stButton > button {
        border-radius: 14px;
        min-height: 42px;
        font-weight: 700;
    }

    div.stDownloadButton > button {
        border-radius: 14px;
        min-height: 42px;
        font-weight: 700;
    }

    /* Inputs */
    div[data-baseweb="input"] {
        border-radius: 14px;
    }

    div[data-baseweb="select"] {
        border-radius: 14px;
    }

    textarea {
        border-radius: 14px !important;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
            max-width: 100% !important;
        }

        .app-title {
            font-size: 28px !important;
            line-height: 1.12 !important;
            letter-spacing: -0.5px !important;
        }

        .app-subtitle {
            font-size: 14px !important;
            margin-bottom: 16px !important;
        }

        h1 {
            font-size: 28px !important;
        }

        h2 {
            font-size: 24px !important;
        }

        h3 {
            font-size: 20px !important;
        }

        .gradient-card {
            padding: 20px !important;
            border-radius: 22px !important;
            margin-bottom: 16px !important;
        }

        .gradient-card h3 {
            font-size: 22px !important;
        }

        .soft-card,
        .card,
        .recipe-card,
        .person-card,
        .favorite-card,
        .menu-day-card,
        .catalog-card,
        .dish-card,
        .mobile-install-card {
            padding: 16px !important;
            border-radius: 20px !important;
            margin-bottom: 14px !important;
        }

        .big-number {
            font-size: 28px !important;
        }

        .small-label {
            font-size: 13px !important;
        }

        .status-pill,
        .badge-green,
        .badge-yellow,
        .badge-red {
            font-size: 12px !important;
            padding: 5px 9px !important;
            margin-bottom: 5px !important;
        }

        .emoji-big {
            font-size: 34px !important;
        }

        .mobile-home-grid {
            grid-template-columns: 1fr !important;
            gap: 10px !important;
        }

        .mobile-action-card {
            text-align: left !important;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px !important;
        }

        .mobile-action-card .icon {
            font-size: 30px !important;
            margin-bottom: 0 !important;
        }

        .menu-meal {
            padding: 11px 12px !important;
            border-radius: 16px !important;
        }

        .footer {
            font-size: 12px !important;
            padding: 12px 14px !important;
            border-radius: 14px !important;
        }

        /* Make tables less painful on mobile */
        div[data-testid="stDataFrame"] {
            overflow-x: auto !important;
            border-radius: 16px !important;
        }

        /* Larger tabs tap area */
        button[data-baseweb="tab"] {
            padding-left: 10px !important;
            padding-right: 10px !important;
            min-height: 42px !important;
            font-weight: 700 !important;
        }

        /* Sidebar radio labels */
        section[data-testid="stSidebar"] label {
            font-size: 15px !important;
            line-height: 1.4 !important;
        }

        section[data-testid="stSidebar"] {
            background: #f3f7f5 !important;
        }
    }

    @media (max-width: 480px) {
        .app-title {
            font-size: 25px !important;
        }

        .gradient-card p,
        .soft-card p,
        .mobile-install-card p {
            font-size: 14px !important;
        }

        .status-pill,
        .badge-green,
        .badge-yellow,
        .badge-red {
            display: inline-block !important;
        }
    }
'''


def patch_css():
    text = APP_FILE.read_text(encoding="utf-8")

    if "v0.9.1 Mobile Polish" in text:
        print("ℹ️ CSS Mobile Polish уже добавлен")
        return text

    css = build_mobile_css()

    marker = "</style>"

    if marker not in text:
        print("⚠️ Не найден </style> в app.py. CSS не добавлен.")
        return text

    text = text.replace(marker, css + "\n</style>", 1)
    print("✅ Добавлены мобильные CSS-улучшения")
    return text


def build_mobile_helpers():
    return r'''

def render_mobile_install_tip():
    st.markdown("""
    <div class="mobile-install-card">
        <h3>📱 Можно пользоваться как приложением</h3>
        <p>
            Откройте эту страницу на телефоне и добавьте её на главный экран.
            Так «Холодильник Мединки» будет запускаться почти как обычное приложение.
        </p>
        <span class="mobile-step">Android: Chrome → ⋮ → Добавить на главный экран</span>
        <span class="mobile-step">iPhone: Safari → Поделиться → На экран Домой</span>
    </div>
    """, unsafe_allow_html=True)


def render_mobile_start_cards():
    st.markdown("""
    <div class="mobile-home-grid">
        <div class="mobile-action-card">
            <div class="icon">📅</div>
            <div>
                <div class="title">Сегодня</div>
                <div class="text">План питания, калории и срочные продукты.</div>
            </div>
        </div>
        <div class="mobile-action-card">
            <div class="icon">🧊</div>
            <div>
                <div class="title">Холодильник</div>
                <div class="text">Остатки, сроки годности и продукты.</div>
            </div>
        </div>
        <div class="mobile-action-card">
            <div class="icon">🛒</div>
            <div>
                <div class="title">Покупки</div>
                <div class="text">Список покупок и перенос в холодильник.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
'''


def patch_mobile_helpers(text):
    if "def render_mobile_install_tip(" in text:
        print("ℹ️ Mobile helpers уже есть")
        return text

    marker = "def render_person_card(profile):"

    if marker not in text:
        print("⚠️ Не найден render_person_card для вставки mobile helpers.")
        return text

    text = text.replace(marker, build_mobile_helpers() + "\n\n" + marker, 1)
    print("✅ Добавлены mobile helper-функции")
    return text


def patch_home_blocks(text):
    if "render_mobile_install_tip()" in text and "render_mobile_start_cards()" in text:
        print("ℹ️ Мобильные блоки на главной уже добавлены")
        return text

    # Вставляем после welcome gradient-card на главной.
    marker = '''    c1, c2, c3, c4 = st.columns(4)'''

    if marker not in text:
        print("⚠️ Не найден блок метрик главной. Пробую альтернативное место.")

        alt_marker = "    render_current_datetime_card()"

        if alt_marker in text:
            insert = '''    render_mobile_install_tip()

    render_mobile_start_cards()

'''
            text = text.replace(alt_marker, insert + alt_marker, 1)
            print("✅ Мобильные блоки добавлены перед датой/временем")
            return text

        return text

    insert = '''    render_mobile_install_tip()

    render_mobile_start_cards()

'''

    text = text.replace(marker, insert + marker, 1)
    print("✅ На главную добавлены мобильные блоки")
    return text


def patch_sidebar_caption(text):
    old = 'st.sidebar.caption(f"{APP_VERSION} · {DEVELOPER}")'

    new = '''st.sidebar.caption(f"{APP_VERSION} · {DEVELOPER}")
st.sidebar.caption("📱 Откройте ссылку на телефоне и добавьте на главный экран")'''

    if "добавьте на главный экран" in text:
        print("ℹ️ Подсказка в sidebar уже есть")
        return text

    if old in text:
        text = text.replace(old, new, 1)
        print("✅ Добавлена мобильная подсказка в sidebar")
    else:
        print("⚠️ Не найден sidebar.caption для мобильной подсказки")

    return text


def patch_quick_actions_labels(text):
    # Улучшаем подписи быстрых кнопок, если функция есть.
    replacements = {
        'st.button("➕ Добавить еду", use_container_width=True)': 'st.button("➕ Добавить еду в дневник", use_container_width=True)',
        'st.button("🛒 Добавить покупку", use_container_width=True)': 'st.button("🛒 Добавить покупку", use_container_width=True)',
        'st.button("🧊 Открыть холодильник", use_container_width=True)': 'st.button("🧊 Открыть холодильник", use_container_width=True)',
    }

    changed = False

    for old, new in replacements.items():
        if old in text and new not in text:
            text = text.replace(old, new)
            changed = True

    if changed:
        print("✅ Улучшены подписи быстрых кнопок")
    else:
        print("ℹ️ Подписи быстрых кнопок не менялись")

    return text


def patch_app():
    text = APP_FILE.read_text(encoding="utf-8")

    text = patch_css()
    text = patch_mobile_helpers(text)
    text = patch_home_blocks(text)
    text = patch_sidebar_caption(text)
    text = patch_quick_actions_labels(text)

    APP_FILE.write_text(text, encoding="utf-8")
    print("✅ app.py обновлён для мобильной версии")


def compile_files():
    print("\n==============================")
    print("Проверяю синтаксис")
    print("==============================")

    files = [
        "app.py",
        "database.py",
        "settings.py",
        "recipes.py",
        "demo_data.py",
        "product_catalog.py",
        "dish_catalog.py",
        "menu_engine.py"
    ]

    ok = True

    for file_name in files:
        path = PROJECT_DIR / file_name

        if not path.exists():
            print(f"⚠️ Нет файла: {file_name}")
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            print(f"✅ OK: {file_name}")
        except Exception as e:
            ok = False
            print(f"❌ Ошибка в {file_name}:")
            print(e)

    return ok


def git_commit_push():
    print("\n==============================")
    print("Пробую отправить изменения на GitHub")
    print("==============================")

    if not (PROJECT_DIR / ".git").exists():
        print("ℹ️ Git-репозиторий не найден. Пропускаю commit/push.")
        return

    run("git add .", check=False)

    status = run("git status --short", check=False)

    if not status.stdout.strip():
        print("ℹ️ Нет изменений для коммита.")
        return

    commit = run('git commit -m "Mobile polish v0.9.1"', check=False)

    if commit.returncode != 0:
        combined = (commit.stdout + commit.stderr).lower()

        if "nothing to commit" in combined:
            print("ℹ️ Коммит не нужен.")
        else:
            print("⚠️ Commit завершился нестандартно. Продолжаю push.")

    push = run("git push", check=False)

    if push.returncode == 0:
        print("✅ Изменения отправлены на GitHub. Streamlit Cloud скоро обновится.")
    else:
        print("⚠️ Не удалось автоматически сделать git push.")
        print("Можно вручную выполнить:")
        print("git add .")
        print('git commit -m "Mobile polish v0.9.1"')
        print("git push")


def main():
    print("====================================")
    print(" v0.9.1 Mobile Polish")
    print(" Умный холодильник Мединки")
    print("====================================\n")

    if not APP_FILE.exists():
        print("❌ app.py не найден.")
        return

    if not SETTINGS_FILE.exists():
        print("❌ settings.py не найден.")
        return

    backup_files()
    update_settings()
    patch_app()

    ok = compile_files()

    print("\n==============================")

    if ok:
        print("✅ Mobile Polish v0.9.1 установлен.")
        git_commit_push()
        print("\nТеперь можно проверить локально:")
        print("python -m streamlit run app.py")
        print("\nИли подождать обновления Streamlit Cloud.")
    else:
        print("⚠️ Есть ошибки синтаксиса. Пришли текст ошибки, я поправлю.")


if __name__ == "__main__":
    main()