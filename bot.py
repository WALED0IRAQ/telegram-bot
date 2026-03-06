import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# القراء المتاحين
RECITERS = {
    "husary": ("الحصري", "Husary_128kbps"),
    "sudais": ("السديس", "Abdurrahmaan_As-Sudais_128kbps"),
    "shuraim": ("الشريم", "Saood_ash-Shuraym_128kbps")
}

user_reciter = {}

def page_image(page):
    return f"https://surahquran.com/img/pages-quran/page{page:03}.png"

def page_audio(page, reciter_code):
    return f"https://everyayah.com/data/{reciter_code}/PageMp3/{page:03}.mp3"

def nav_keyboard(page):
    kb = InlineKeyboardMarkup()
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page:{page-1}"))
    if page < 604:
        buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page:{page+1}"))
    kb.row(*buttons)
    kb.row(
        InlineKeyboardButton("🎧 تغيير القارئ", callback_data="reciters")
    )
    return kb

def reciters_keyboard():
    kb = InlineKeyboardMarkup()
    for key, (name, _) in RECITERS.items():
        kb.add(InlineKeyboardButton(f"🎙 {name}", callback_data=f"setrec:{key}"))
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    user_reciter[m.from_user.id] = "husary"
    bot.send_message(
        m.chat.id,
        "أهلاً بك في بوت القرآن.\nأرسل رقم الصفحة (1–604).\nيمكنك تغيير القارئ من الزر."
    )

@bot.message_handler(func=lambda m: True)
def handle_page(m):
    text = (m.text or "").strip()
    if not text.isdigit():
        bot.reply_to(m, "أرسل رقم صفحة فقط (1–604).")
        return

    page = int(text)
    if page < 1 or page > 604:
        bot.reply_to(m, "الصفحات من 1 إلى 604 فقط.")
        return

    send_page(m.chat.id, m.from_user.id, page)

def send_page(chat_id, user_id, page):
    rec_key = user_reciter.get(user_id, "husary")
    rec_name, rec_code = RECITERS[rec_key]

    img = page_image(page)
    aud = page_audio(page, rec_code)

    bot.send_chat_action(chat_id, "upload_photo")
    bot.send_photo(
        chat_id,
        img,
        caption=f"📖 الصفحة {page}\n🎙 القارئ: {rec_name}",
        reply_markup=nav_keyboard(page)
    )

    bot.send_chat_action(chat_id, "upload_audio")
    bot.send_audio(
        chat_id,
        aud,
        caption=f"تلاوة الصفحة {page} - {rec_name}"
    )

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    data = c.data

    if data.startswith("page:"):
        page = int(data.split(":")[1])
        bot.answer_callback_query(c.id)
        send_page(c.message.chat.id, c.from_user.id, page)

    elif data == "reciters":
        bot.answer_callback_query(c.id)
        bot.send_message(
            c.message.chat.id,
            "اختر القارئ:",
            reply_markup=reciters_keyboard()
        )

    elif data.startswith("setrec:"):
        key = data.split(":")[1]
        if key in RECITERS:
            user_reciter[c.from_user.id] = key
            name = RECITERS[key][0]
            bot.answer_callback_query(c.id, f"تم اختيار القارئ: {name}")
            bot.send_message(c.message.chat.id, f"تم تغيير القارئ إلى: {name}")

bot.infinity_polling()