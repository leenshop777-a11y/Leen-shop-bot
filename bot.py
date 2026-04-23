import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- إعداد خادم الويب (Flask) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Leen Shop Bot is Running!"

def run_flask():
    # Render يطلب تشغيل السيرفر على بورت معين
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- إعداد البوت (Telegram Bot) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    message = (
        f"أهلاً بك يا {user_name} في متجر لين (Leen Shop) 🌸\n\n"
        "كتابنا الرقمي متاح الآن بسعر مميز:\n"
        "💰 السعر بالدولار: 47$\n"
        "🇸🇦 السعر بالريال السعودي: 176 ريال\n\n"
        "لطلب الكتاب أو الاستفسار، نحن هنا لخدمتك!"
    )
    await update.message.reply_text(message)

def main_bot():
    # جلب التوكن من إعدادات ريندر (Environment Variables)
    token = os.environ.get("TOKEN")
    if not token:
        print("خطأ: لم يتم العثور على TOKEN في الإعدادات!")
        return

    # بناء تطبيق البوت
    application = Application.builder().token(token).build()

    # إضافة الأوامر
    application.add_handler(CommandHandler("start", start))

    # بدء الاستماع للرسائل
    print("البوت بدأ الاستماع للرسائل...")
    application.run_polling()

if __name__ == '__main__':
    # 1. تشغيل Flask في خيط منفصل (Thread) لكي لا يتوقف البوت
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 2. تشغيل البوت في الخيط الرئيسي
    main_bot()
