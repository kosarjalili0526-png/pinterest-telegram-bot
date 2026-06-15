import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# این مقدار رو دست نزن، تنظیمش رو توی Render انجام میدیم
BOT_TOKEN = os.getenv("BOT_TOKEN")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def extract_pinterest_media(url):
    # حل مشکل لینک‌های کوتاه pin.it
    session = requests.Session()
    response = session.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
    final_url = response.url
    
    soup = BeautifulSoup(response.text, "html.parser")

    # جستجوی ویدئو
    video_tag = soup.find("meta", property="og:video")
    if video_tag and video_tag.get("content"):
        return "video", video_tag["content"]

    # جستجوی تصویر
    image_tag = soup.find("meta", property="og:image")
    if image_tag and image_tag.get("content"):
        return "image", image_tag["content"]

    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لینک پینترست رو بفرست تا برات دانلود کنم. 📌")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "pinterest.com" not in url and "pin.it" not in url:
        await update.message.reply_text("لطفاً فقط لینک معتبر پینترست بفرست. ❌")
        return

    msg = await update.message.reply_text("در حال پردازش... ⏳")

    try:
        media_type, media_url = extract_pinterest_media(url)

        if not media_url:
            await msg.edit_text("متأسفانه نتونستم فایل رو پیدا کنم. ممکنه لینک خصوصی باشه. 😕")
            return

        if media_type == "video":
            await update.message.reply_video(video=media_url, caption="بفرمایید ویدئو شما ✅")
        else:
            await update.message.reply_photo(photo=media_url, caption="بفرمایید تصویر شما ✅")
        
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"خطایی رخ داد: {str(e)}")

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("خطا: BOT_TOKEN تنظیم نشده است!")
    else:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("ربات روشن شد...")
        app.run_polling()
