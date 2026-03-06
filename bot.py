import telebot
import os

TOKEN = os.environ.get("TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "اهلا بك في بوت القرآن الكريم.\nارسل رقم الصفحة من 1 الى 604."
    )

@bot.message_handler(func=lambda m: True)
def send_page(message):
    msg = message.text

    if not msg.isdigit():
        bot.reply_to(message, "ارسل رقم صفحة فقط")
        return

    page = int(msg)

    if page < 1 or page > 604:
        bot.reply_to(message, "الصفحات من 1 الى 604 فقط")
        return

    bot.send_chat_action(message.chat.id, "upload_photo")

    url = f"https://surahquran.com/img/pages-quran/page{page:03}.png"

    bot.send_photo(message.chat.id, url, caption=f"الصفحة رقم {page}")

bot.infinity_polling()