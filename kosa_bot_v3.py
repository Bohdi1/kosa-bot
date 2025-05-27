# bohdi1/kosa-bot/kosa_bot_v3.py
import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Завантажуємо змінні середовища з файлу .env
load_dotenv()

try:
    from aiogram import Bot, Dispatcher, F, Router
    from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    from aiogram.enums import ParseMode
    from aiogram.filters import CommandStart, Command
    from aiogram.client.default import DefaultBotProperties
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State, StatesGroup
except ModuleNotFoundError:
    print("ПОМИЛКА: Необхідну бібліотеку 'aiogram' не знайдено.")
    print("Будь ласка, встановіть її, відкривши термінал (командний рядок) та виконавши команду:")
    print("pip install -r requirements.txt")
    print("Після успішного встановлення, будь ласка, спробуйте запустити скрипт знову.")
    sys.exit()

# Беремо токен та ID чату з оточення
API_TOKEN = os.getenv('API_TOKEN')
ADMIN_CHAT_ID = os.getenv('CHAT_ID')

if not API_TOKEN:
    print("ПОМИЛКА: API_TOKEN не знайдено. Перевірте ваш .env файл.")
    sys.exit()
if not ADMIN_CHAT_ID:
    print("ПОМИЛКА: CHAT_ID не знайдено. Перевірте ваш .env файл.")
    sys.exit()

logging.basicConfig(level=logging.INFO)

# Створюємо бота і диспетчер
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
diagnostic_router = Router()

# ОНОВЛЕНО: Стани для FSM діагностики + створення заявки
class DiagnosticStates(StatesGroup):
    waiting_for_device_type = State()
    waiting_for_problem_category_pc = State()
    waiting_for_screen_symptom_pc = State()
    waiting_for_problem_category_mobile = State()
    waiting_for_mobile_screen_symptom = State()
    waiting_for_other_device_main_category = State()
    waiting_for_problem_category_office = State()
    waiting_for_problem_category_appliance = State()
    waiting_for_problem_category_av = State()
    waiting_for_problem_category_etransport = State()
    # НОВІ СТАНИ для створення заявки
    waiting_for_name = State()
    waiting_for_phone = State()

# Клавіатура - без змін
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Адреса сервісу"), KeyboardButton(text="Контакти")],
    [KeyboardButton(text="Діагностика"), KeyboardButton(text="Що ремонтуємо?")],
    [KeyboardButton(text="🤖 Інтерактивна діагностика")]
], resize_keyboard=True)

# Тексти повідомлень (без змін, винесені для чистоти коду)
REPAIR_SERVICES_TEXT = ("<b>«КоСА-Сервіс» – ваш надійний партнер у світі технологій!</b>...")
ADRESY_TEXT = ("<b>Наші сервісні центри KoSA:</b>...")
KONTAKTY_TEXT = ("<b>Наші контакти:</b>...")
GRAFIK_ROBOTY_TEXT = ("<b>Графік роботи сервісних центрів KoSA:</b>...")
DIAGNOSTYKA_TEXT = ("🔍 <b>Діагностика техніки в KoSA Service...</b>")
keyword_responses = {
    # ... (словник без змін)
}

# --- Початок блоку інтерактивної діагностики ---

# Клавіатури для діагностики (без змін)
def get_device_type_kb():
    buttons = [
        [InlineKeyboardButton(text="💻 Комп'ютер / Ноутбук", callback_data="diag_device_pc")],
        [InlineKeyboardButton(text="📱 Смартфон / Планшет", callback_data="diag_device_mobile")],
        [InlineKeyboardButton(text="🛠️ Інша техніка", callback_data="diag_device_other_category_selection")],
        [InlineKeyboardButton(text="⬅️ Скасувати діагностику", callback_data="diag_cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ... (інші функції get_*_kb() без змін) ...
def get_pc_problem_category_kb():
    #...
    return InlineKeyboardMarkup(inline_keyboard=buttons)
def get_pc_screen_symptoms_kb():
    #...
    return InlineKeyboardMarkup(inline_keyboard=buttons)
def get_mobile_problem_category_kb():
    #...
    return InlineKeyboardMarkup(inline_keyboard=buttons)
def get_mobile_screen_symptoms_kb():
    #...
    return InlineKeyboardMarkup(inline_keyboard=buttons)
def get_other_device_main_category_kb():
    #...
    return InlineKeyboardMarkup(inline_keyboard=buttons)
def get_generic_problem_categories_kb(device_category_prefix: str):
    #...
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ОНОВЛЕНО: Клавіатура після діагностики з опцією створення заявки
def get_post_diagnostic_kb():
    buttons = [
        [InlineKeyboardButton(text="✍️ Створити заявку на ремонт", callback_data="diag_create_ticket")],
        [InlineKeyboardButton(text="🔄 Почати спочатку", callback_data="diag_restart")],
        [InlineKeyboardButton(text="📞 Зв'язатися з нами", callback_data="diag_show_contacts")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Обробник кнопки "Інтерактивна діагностика" (без змін)
@dp.message(F.text == "🤖 Інтерактивна діагностика")
async def start_interactive_diagnostic(message: Message, state: FSMContext):
    # ...

# Обробник скасування діагностики (без змін)
@diagnostic_router.callback_query(F.data == "diag_cancel")
async def cancel_diagnostic_handler(callback: CallbackQuery, state: FSMContext):
    # ...

# ... (усі обробники вибору проблеми без змін) ...
# @diagnostic_router.callback_query(DiagnosticStates.waiting_for_device_type, ...)
# ...

# ОНОВЛЕНО: Функція для показу ПОПЕРЕДНЬОГО результату діагностики
# Вона більше не скидає стан, щоб дозволити створення заявки
async def show_preliminary_diagnostic_result(callback: CallbackQuery, state: FSMContext, problem_description: str):
    await state.update_data(problem_description=problem_description) # Зберігаємо опис проблеми
    user_data = await state.get_data()
    device_type_choice = user_data.get("device_type_choice", "невідомий пристрій")

    device_map = {
        "pc": "Комп'ютер / Ноутбук",
        "mobile": "Смартфон / Планшет",
        "other_category_selection": "Інша техніка"
    }
    device_name = device_map.get(device_type_choice, "Пристрій")

    text = (
        f"<b>Результат попередньої діагностики для: {device_name}</b>\n\n"
        f"<b>Ймовірна проблема:</b>\n{problem_description}\n\n"
        "<b>Що далі?</b>\n"
        "Це лише попередній висновок. Для точного визначення причини та вартості ремонту потрібна професійна діагностика в сервісному центрі.\n\n"
        "Ви можете <b>створити попередню заявку</b>, і наш менеджер зв'яжеться з вами, або зателефонувати нам самостійно."
    )
    reply_markup = get_post_diagnostic_kb()
    await callback.message.edit_text(text, reply_markup=reply_markup)
    await callback.answer()


# Обробники, що ведуть до результату, тепер викликають нову функцію
@diagnostic_router.callback_query(DiagnosticStates.waiting_for_screen_symptom_pc, F.data.startswith("diag_pc_screen_"))
async def pc_screen_symptom_chosen(callback: CallbackQuery, state: FSMContext):
    # ... (логіка визначення проблеми)
    description = symptom_description_map.get(screen_symptom, "Проблеми з відображенням на екрані.")
    await show_preliminary_diagnostic_result(callback, state, problem_description=description) # Виклик нової функції

# ... (інші обробники проблем також оновлені для виклику show_preliminary_diagnostic_result) ...


# --- НОВИЙ БЛОК: Створення заявки після діагностики ---

@diagnostic_router.callback_query(F.data == "diag_create_ticket")
async def create_ticket_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Чудово! Щоб створити заявку, вкажіть, будь ласка, ваше ім'я.")
    await state.set_state(DiagnosticStates.waiting_for_name)
    await callback.answer()

@dp.message(DiagnosticStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Дякую. Тепер вкажіть ваш контактний номер телефону.")
    await state.set_state(DiagnosticStates.waiting_for_phone)

@dp.message(DiagnosticStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(user_phone=message.text)
    user_data = await state.get_data()

    # Формуємо заявку для адміна
    device_type = user_data.get('device_type_choice', 'не вказано').replace('_', ' ').capitalize()
    problem_description = user_data.get('problem_description', 'не вказано')
    user_name = user_data.get('user_name', 'не вказано')
    user_phone = user_data.get('user_phone', 'не вказано')

    ticket_text = (
        f"🚨 **Нова заявка з Телеграм-бота** 🚨\n\n"
        f"👤 **Клієнт:** {user_name}\n"
        f"📞 **Телефон:** <code>{user_phone}</code>\n\n"
        f"💻 **Пристрій:** {device_type}\n"
        f"🔧 **Опис проблеми (з бота):** {problem_description}"
    )

    try:
        await bot.send_message(ADMIN_CHAT_ID, ticket_text)
        await message.answer(
            "✅ **Заявку створено!**\n\n"
            "Дякую! Наш менеджер зв'яжеться з вами найближчим часом для уточнення деталей.\n\n"
            "Чим ще можу допомогти?",
            reply_markup=main_kb
        )
    except Exception as e:
        logging.error(f"Не вдалося відправити заявку: {e}")
        await message.answer(
            "😥 Виникла помилка під час створення заявки. "
            "Будь ласка, зв'яжіться з нами за телефонами, вказаними в розділі 'Контакти'.",
            reply_markup=main_kb
        )
    finally:
        await state.clear()

# --- Кінець нового блоку ---


# Обробник кнопки "Почати спочатку" (тепер скидає стан)
@diagnostic_router.callback_query(F.data == "diag_restart")
async def restart_diagnostic_flow(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # ... (код для початку діагностики)

# Обробник кнопки "Зв'язатися з нами" (тепер скидає стан)
@diagnostic_router.callback_query(F.data == "diag_show_contacts")
async def show_contacts_from_diag(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(KONTAKTY_TEXT, reply_markup=main_kb)
    await callback.answer("Контакти надіслано.")
    await state.clear() # Скидаємо стан, бо дія завершена


# Головні обробники команд /start, /help, та текстових повідомлень (без змін)
@dp.message(CommandStart())
async def handle_start(message: Message):
    #...

@dp.message(Command("help"))
async def handle_help(message: Message):
    #...

@dp.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    #...

async def main():
    dp.include_router(diagnostic_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
