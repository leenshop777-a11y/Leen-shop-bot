import asyncio
import aiohttp
import time
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== الإعدادات - عدّل هنا فقط ==========
BOT_TOKEN = "8432218715:AAGCaMGfnGc6pXfiOUf2reCRu1ThzvENGk4 # من BotFather
TRON_ADDRESS = "TNLtMGhQbTWpHkwKiWuAMMC95hhe6e1Qkn"
BOT_USERNAME = "Leenshop777bot"

PRODUCTS = {
    "product1": {
        "name_ar": "من الصفر إلى ألف دولار",
        "name_en": "From Zero to $1000",
        "price": 47,
        "link": "https://drive.google.com/file/d/1VNKROsJLSddq3wVXGreexfZk7GxXKSWb/view?usp=drivesdk"
    },
    "product2": {
        "name_ar": "Royal 90 Day Digital Success Planner",
        "name_en": "Royal 90 Day Digital Success Planner",
        "price": 37,
        "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view?usp=drivesdk"
    },
    "product3": {
        "name_ar": "Leen Slim Secret Pro",
        "name_en": "Leen Slim Secret Pro",
        "price": 27,
        "link": "https://drive.google.com/file/d/1ZD9XWSD1jmczhJix7DbZ_EJ0ccAvyLRt/view?usp=drivesdk"
    }
}

# ========== قاعدة البيانات المؤقتة ==========
pending_orders = {} # {order_id: {user_id, product_id, price, timestamp}}
completed_orders = set() # لتجنب الإرسال مرتين

# ========== الدوال المساعدة ==========
def generate_order_id():
    return f"{int(time.time())}_{random.randint(100,999)}"

async def check_tron_payment(order_id, expected_amount):
    """يشيك بلوك تشين TRON عن تحويلة بـ Memo = order_id"""
    url = f"https://apilist.tronscanapi.com/api/transaction?address={TRON_ADDRESS}&limit=20"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                for tx in data.get("data", []):
                    memo = tx.get("data", "")
                    amount = int(tx.get("amount", 0)) / 1000000 # من SUN إلى USDT
                    if memo == order_id and abs(amount - expected_amount) < 0.5:
                        return True
    except:
        pass
    return False

# ========== أوامر البوت ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    # لو جاي من Carrd: /start product1
    if args and args[0] in PRODUCTS:
        product_id = args[0]
        product = PRODUCTS[product_id]
        order_id = generate_order_id()

        # حفظ الطلب
        pending_orders[order_id] = {
            "user_id": user_id,
            "product_id": product_id,
            "price": product["price"],
            "timestamp": time.time()
        }

        text = f"""
Please send {product['price']} USDT to the following TRON address:
يرجى إرسال {product['price']} USDT إلى عنوان TRON التالي:

Address: `{TRON_ADDRESS}`
Network: TRON - TRC20

Memo/Note: `{order_id}`
ملاحظة مهمة: `{order_id}`

Important: You must add the Order ID in Memo field
مهم: يجب إضافة رقم الطلب في خانة الملاحظة Memo

Product: {product['name_en']}
المنتج: {product['name_ar']}

We will send your file automatically after payment confirmation.
سيتم إرسال ملفك تلقائياً بعد تأكيد الدفع.
"""
        await update.message.reply_text(text, parse_mode='Markdown')

    else:
        # القائمة الرئيسية
        text = """
Welcome to Leen Shop! 🛍️
أهلاً بك في متجر لين! 🛍️

To buy, please visit our website and click "Buy Now"
للشراء يرجى زيارة موقعنا والضغط على "اشتري الآن"

For support: @LeenShop777bot
للدعم: @LeenShop777bot
"""
        await update.message.reply_text(text)

async def check_payments(context: ContextTypes.DEFAULT_TYPE):
    """يشيك كل الطلبات المعلقة كل 30 ثانية"""
    to_delete = []
    for order_id, order in pending_orders.items():
        # لو الطلب قديم أكثر من ساعة نحذفه
        if time.time() - order["timestamp"] > 3600:
            to_delete.append(order_id)
            continue

        if order_id in completed_orders:
            continue

        paid = await check_tron_payment(order_id, order["price"])
        if paid:
            product = PRODUCTS[order["product_id"]]
            completed_orders.add(order_id)
            to_delete.append(order_id)

            # رسالة الشكر + الرابط
            text = f"""
Payment confirmed! ✅
تم تأكيد الدفع! ✅

Thank you for your purchase!
شكراً لشرائك!

Product: {product['name_en']}
المنتج: {product['name_ar']}

Order ID: `{order_id}`
رقم الطلب: `{order_id}`

Here is your download link:
هذا رابط التحميل الخاص بك:
{product['link']}

Enjoy! For support contact @{BOT_USERNAME}
استمتع! للدعم تواصل @{BOT_USERNAME}
"""
            try:
                await context.bot.send_message(
                    chat_id=order["user_id"],
                    text=text,
                    parse_mode='Markdown'
                )
            except:
                pass

    for order_id in to_delete:
        if order_id in pending_orders:
            del pending_orders[order_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
How to buy:
كيفية الشراء:

1. Go to our website and click "Buy Now"
اذهب لموقعنا واضغط "اشتري الآن"

2. Send the exact USDT amount to our TRON address
أرسل مبلغ USDT بالضبط لعنوان TRON

3. Must add Order ID in Memo field
يجب إضافة رقم الطلب في خانة الملاحظة

4. You will receive your file automatically in 1-2 minutes
ستستلم ملفك تلقائياً خلال 1-2 دقيقة

Support: @{BOT_USERNAME}
الدعم: @{BOT_USERNAME}
"""
    await update.message.reply_text(text)

# ========== تشغيل البوت ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # يشيك الدفعات كل 30 ثانية
    app.job_queue.run_repeating(check_payments, interval=30, first=10)

    print("Bot is running... البوت شغال")
    app.run_polling()

if __name__ == "__main__":
    main()
    import os
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    Thread(target=run).start()
    application.run_polling()
