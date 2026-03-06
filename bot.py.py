import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

TOKEN = os.environ.get("TOKEN")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("أرسل رابط فيديو صالح")
        return

    await update.message.reply_text("جاري التنزيل...")

    ydl_opts = {
        "format": "best[filesize<50M]",
        "outtmpl": "video.%(ext)s"
    }

    filename = None

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, "rb") as f:
            await update.message.reply_video(f)

    except Exception as e:
        await update.message.reply_text(f"فشل التنزيل: {e}")

    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

print("البوت شغال")
app.run_polling()