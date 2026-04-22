import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get('TOKEN')

PRODUCTS = {
    "p1": {
        "name_ar": "من الصفر إلى ألف دولار",
        "name_en": "From Zero to $1,000",
        "price_ar": "47 دولار",
        "price_en": "$47",
        "desc_ar": "دليل عملي خطوة بخطوة لتحقيق أول ألف دولار أونلاين. مناسب للمبتدئين تماماً.",
        "desc_en": "Step-by-step practical guide to make your first $1,000 online. Perfect for beginners.",
        "link": "https://drive.google.com/file/d/1VNKROsJLSddq3wVXGreexfZk7GxXKSWb/view?usp=drivesdk"
    },
    "p2": {
        "name_ar": "مخطط النجاح الرقمي 90 يوم",
        "name_en": "Royal 90-Day Digital Success Planner",
        "price_ar": "37 دولار",
        "price_en": "$37",
        "desc_ar": "مخطط رقمي لمدة 90 يوم لتنظيم أهدافك ومشاريعك وتحقيق النجاح الرقمي.",
        "desc_en": "90-day digital planner to organize your goals, projects and achieve digital success.",
        "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view?usp=drivesdk"
    },
    "p3": {
        "name_ar": "لين سليم سيكريت برو",
        "name_en": "Leen Slim Secret Pro",
        "price_ar": "دولار27",
        "price_en": "$27",
        "desc_ar": "برنامج لين سليم سيكريت برو الاحترافي. تواصل معنا لمعرفة السعر والتفاصيل.",
        "desc_en": "Leen Slim Secret Pro program. Contact us for price and details.",
        "link": "https://drive.google.com/file/d/1ZD9XWSD1jmczhJix7DbZ_EJ0ccAvyLRt/view?usp=drivesdk"
    }
}

TEXTS = {
    "ar": {
        "welcome": "أهلاً بك في متجر لين 🌸\nاختاري اللغة:",
        "main_menu": "القائمة الرئيسية 🏠\nاختاري المنتج:",
        "back": "🔙 رجوع للقائمة",
        "download": "📥 رابط التحميل",
        "price": "السعر:"
    },
    "en": {
        "welcome": "Welcome to Leen Store 🌸\nChoose language:",
        "main_menu": "Main Menu 🏠\nChoose a product:",
        "back": "🔙 Back to Menu",
        "download": "📥 Download Link",
        "price": "Price:"
    }
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')],
        [InlineKeyboardButton("English 🇺🇸", callback_data='lang_en')]
    ]
    await update.message.reply_text(TEXTS["ar"]["welcome"], reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'lang_ar' or data == 'lang_en':
        lang = 'ar' if data == 'lang_ar' else 'en'
        context.user_data['lang'] = lang
        keyboard = []
        for pid, product in PRODUCTS.items():
            name = product[f'name_{lang}']
            price = product[f'price_{lang}']
            keyboard.append([InlineKeyboardButton(f"{name} - {price}", callback_data=f'prod_{pid}')])
        await query.edit_message_text(text=TEXTS['main_menu'], reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith('prod_'):
        lang = context.user_data.get('lang', 'ar')
        pid = data.split('_')[1]
        product = PRODUCTS[pid]
        name = product[f'name_{lang}']
        price = product[f'price_{lang}']
        desc = product[f'desc_{lang}']
        link = product['link']
        text = f"**{name}**\n\n{TEXTS['price']} {price}\n\n{desc}"
        keyboard = [
            [InlineKeyboardButton(TEXTS['download'], url=link)],
            [InlineKeyboardButton(TEXTS['back'], callback_data=f'lang_{lang}')]
        ]
        await query.edit_message_text(text=text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

app = Flask('')

@app.route('/')
def home():
    return "Leen Shop Bot is running 24/7"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    Thread(target=run_flask).start()
    application.run_polling()

if __name__ == '__main__':
    main()
