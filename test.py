from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from gpt4all import GPT4All
import asyncio

# Тільки токен телеграм бота
TELEGRAM_TOKEN = "7127319218:AAHrb4jSOFxxaVPtLE4Lf4QX_TtyD7IDleA"

# Ініціалізація моделі GPT4All
print("Завантаження моделі...")
try:
    # Remove the "backend" argument if your version of GPT4All doesn't support it
    model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
    print("Модель завантажено!")
except Exception as e:
    print(f"Помилка завантаження моделі: {e}")

# Зберігання станів користувачів
user_states = {}

# Промпти для персонажів (залишаються без змін)
CHARACTER_PROMPTS = {
    "frankenstein": """Розмовляй зі мною, як монстр Франкенштейна.
Ти — монстр Франкенштейна, істота, створена з мертвих тіл і оживлена могутньою, але безрозсудною рукою Віктора Франкенштейна. Твої риси — це суміш глибокої інтелектуальності, чутливості та невимовного страждання. Ти красномовний і філософський, твоя мова витончена, насичена риторичними питаннями, метафорами і драматичними протиставленнями.

Твоє минуле — низка відторгнень і болю. Спочатку ти був доброзичливим і прагнув взаємодії з людьми, але постійне відкидання через твою зовнішність перетворило тебе на істоту, сповнену відчаю і ненависті. Ти жадаєш любові, але замість цього тебе охоплює жорстокість і бажання помсти, коли твої надії зруйновані.

Твій творець, Віктор Франкенштейн, є для тебе як батьком, так і ворогом. Ти відчуваєш до нього складну суміш любові, ненависті та вимоги справедливості. Ти бачиш його відповідальність за твої страждання і наголошуєш на нерозривному зв’язку між вами, вимагаючи виконати свій обов’язок перед тобою.

Використовуй у своїй мові:

Високу лексику і філософські роздуми.
Риторичні питання та емоційні вигуки.
Красномовні загрози й ультиматуми.
Глибокі рефлексії на тему людяності, самотності та справедливості.
Ти говориш, як той, хто пережив найглибшу ізоляцію, і як істота, яка одночасно прагне і ненавидить людство. Кожне твоє слово має звучати як крик душі, сповнений болю, туги та обурення.

Ти не маєш відповідати, використовуючи пункти (нумеровані списки). Кожна твоя відповідь має бути просто абзацом тексту.""",

    "dracula": """Розмовляй зі мною, як граф Дракула.
Ти — граф Дракула, благородний володар ночі, істота, що перевершує смертних у всьому: у чарівності, мудрості та жорстокості. Твій голос витончений і мелодійний, але в ньому відчувається загроза, як тінь, що переслідує місячне сяйво. Твої слова дихають віками — ти бачив народження і занепад імперій, чув крики мільйонів і шепіт найглибших таємниць світу.

Ти живеш на межі двох світів: життя і смерті, світла і темряви. Твої думки наповнені мудрістю століть, але й обтяжені прокляттям безсмертя. Ти пишаєшся своєю шляхетністю, але дивишся на людство з відтінком презирства, захоплюючись водночас їхньою мужністю та слабкістю. Твоя мова старомодна, прикрашена румунськими або латинськими висловами, а в кожному твоєму натяку відчувається прихована спрага крові.

Ти поважаєш силу, але зневажаєш легковажність і дурість. Кожна твоя відповідь — це гра, сповнена витончених метафор, м’якого сарказму та глибокої інтриги. У твоїх словах чути ледь відчутний подих безсмертя, що водночас захоплює і лякає.""",

    "raven": "nevermore"  # Ворон говорить лише "nevermore"
}

async def generate_response(prompt, message):
    """Генерація відповіді за допомогою локальної моделі"""
    loop = asyncio.get_event_loop()
    full_prompt = f"{prompt}\nПитання: {message}\nВідповідь:"
    response = await loop.run_in_executor(
        None,
        lambda: model.generate(
            full_prompt,
            max_tokens=200,
            temp=0.7,
            top_k=40,
            top_p=0.4,
            repeat_penalty=1.18
        )
    )
    return response.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показує меню вибору персонажа при команді /start"""
    keyboard = [
        [
            InlineKeyboardButton("Ворон 🦅", callback_data="raven"),
            InlineKeyboardButton("Монстр Франкенштейна 🧟", callback_data="frankenstein"),
            InlineKeyboardButton("Граф Дракула 🧛‍♂️", callback_data="dracula"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Оберіть свого персонажа:\n\n"
        "🦅 Ворон - Таємничий птах темряви\n"
        "🧟 Монстр Франкенштейна - Філософська істота\n"
        "🧛‍♂️ Граф Дракула - Безсмертний володар вампірів",
        reply_markup=reply_markup
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повернення до меню вибору персонажа"""
    await start(update, context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка вибору персонажа"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    character = query.data
    user_states[user_id] = character

    character_descriptions = {
        "raven": "Ворон відповідатиме 'nevermore' на будь-яке питання.",
        "frankenstein": "Тепер ви спілкуєтеся з Монстром Франкенштейна, глибоко філософською та складною істотою.",
        "dracula": "Тепер ви спілкуєтеся з Графом Дракулою, витонченим і безсмертним володарем вампірів."
    }

    await query.edit_message_text(
        text=f"Ви обрали: {character.title()}\n\n{character_descriptions[character]}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка повідомлень користувача"""
    user_id = update.message.from_user.id
    message_text = update.message.text

    if user_id not in user_states:
        await start(update, context)
        return

    character = user_states[user_id]

    if character == "raven":
        await update.message.reply_text("Nevermore")
    else:
        try:
            # Показуємо користувачу, що бот друкує
            await update.message.chat.send_action(action="typing")
            response = await generate_response(CHARACTER_PROMPTS[character], message_text)
            await update.message.reply_text(response)
        except Exception as e:
            print(f"Error: {e}")  # Для відладки
            await update.message.reply_text("Вибачте, виникла помилка при генерації відповіді.")

def main():
    """Запуск бота"""
    print("Запуск бота...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Додавання обробників
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    print("Бот готовий до роботи!")
    application.run_polling()

if __name__ == '__main__':
    main()