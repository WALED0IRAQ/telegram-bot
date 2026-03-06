import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("TOKEN")
bot = telebot.TeleBot(TOKEN)

# القارئ الافتراضي (للاستخدام مستقبلاً)
user_reciter = {}

# Admin ID
ADMIN_ID = 123456789  # ضع هنا رقمك الخاص

# متغير لتخزين عدد المستخدمين
user_count = set()

def page_image(page):
    return f"https://surahquran.com/img/pages-quran/page{page:03}.png"

def nav_keyboard(page):
    kb = InlineKeyboardMarkup()
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page:{page-1}"))
    if page < 604:
        buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page:{page+1}"))
    kb.row(*buttons)
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    user_count.add(m.from_user.id)
    bot.send_message(
        m.chat.id,
        "أهلاً بك في بوت القرآن.\nأرسل رقم الصفحة (1–604) لإرسال الصورة.\nيمكنك استخدام أزرار التنقل بعد إرسال أي صفحة."
    )

@bot.message_handler(func=lambda m: True)
def handle_page(m):
    user_count.add(m.from_user.id)  # تسجيل المستخدم

    text = (m.text or "").strip()

    # أمر إحصائية الأدمن
    if text.lower() == "/stats" and m.from_user.id == ADMIN_ID:
        bot.reply_to(m, f"عدد المستخدمين الفعلي: {len(user_count)}")
        return

    # التحقق من رقم الصفحة
    if not text.isdigit():
        bot.reply_to(m, "أرسل رقم صفحة صالح (1–604).")
        return

    page = int(text)
    if page < 1 or page > 604:
        bot.reply_to(m, "الصفحات من 1 إلى 604 فقط.")
        return

    # إرسال الصفحة
    send_page(m.chat.id, page)

def send_page(chat_id, page):
    img = page_image(page)
    bot.send_chat_action(chat_id, "upload_photo")
    bot.send_photo(
        chat_id,
        img,
        caption=f"📖 الصفحة {page}",
        reply_markup=nav_keyboard(page)
    )

@bot.callback_query_handler(func=lambda c: True)
def callbacks(c):
    data = c.data
    if data.startswith("page:"):
        page = int(data.split(":")[1])
        bot.answer_callback_query(c.id)
        send_page(c.message.chat.id, page)

bot.infinity_polling()