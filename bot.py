import os
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

# إعداد Flask للعمل على ريندر
app = Flask(__name__)

@app.route('/')
def home():
    return "Leen Shop Bot is Running!"

# الحصول على التوكن من إعدادات ريندر
TOKEN = os.getenv("TOKEN")

# دالة لجلب سعر صرف الدولار مقابل الريال السعودي
def get_exchange_rate():
    try:
        # استخدام API مجاني وموثوق
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=10)
        data = response.json()
        return data.get('rates', {}).get('SAR', 3.75)
    except Exception as e:
        print(f"Error fetching rate: {e}")
        return 3.75  # سعر افتراضي في حال فشل الاتصال

# دالة الأمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = get_exchange_rate()
    price_usd = 47
    price_sar = round(price_usd * rate, 2)
    
    welcome_msg = (
        f"مرحباً بك في Leen Shop! 🌸\n\n"
        f"سعر الكتاب الرقمي هو: {price_usd} دولار\n"
        f"ما يعادل تقريباً: {price_sar} ريال سعودي\n\n"
        f"لإتمام الشراء أو الاستفسار، نحن هنا لخدمتك."
    )
    await update.message.reply_text(welcome_msg)

# تشغيل البوت
def run_bot():
    if not TOKEN:
        print("خطأ: لم يتم العثور على TOKEN في إعدادات ريندر!")
        return
        
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("البوت بدأ الاستماع للرسائل...")
    application.run_polling()

if __name__ == "__main__":
    # تشغيل البوت في "خيط" منفصل لكي لا يتصادم مع Flask
    threading.Thread(target=run_bot).start()
    
    # تشغيل Flask على المنفذ الذي يطلبه ريندر
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
