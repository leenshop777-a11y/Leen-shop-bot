import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8432218715:AAGCaMGfnGc6pXfi0Uf2reCRu1ThzvENGk4"

FILES = {
    "planner2026": {"name": "Royal 90-Day Business Planner 2026", "price": "$37", "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view?usp=drivesdk"},
    "slim7days": {"name": "7 Days Slim Secret", "price": "$27", "link": "https://drive.google.com/file/d/1ZD9XWSD1jmczhJix7DbZ_EJ0ccAvyLRt/view?usp=drivesdk"}
}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        product_key = context.args[0]
        if product_key in FILES:
            product = FILES[product_key]
            await update.message.reply_text(f"طلبك جاهز يا بطل 💛\n\n{product['name']} - {product['price']}\n\nجاري الإرسال...")
            await update.message.reply_document(document=product['link'], caption=f"شكراً لشرائك من LEEN SHOP ✨")
            return

    keyboard = []
    for key, item in FILES.items():
        keyboard.append([InlineKeyboardButton(f"{item['name']} - {item['price']}", callback_data=key)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('أهلاً بك في LEEN SHOP 👑\nاختر منتجك الرقمي:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_key = query.data
    product = FILES[product_key]

    await query.edit_message_text(text=f"طلبك: {product['name']} - {product['price']}\n\nجاري الإرسال...")
    await context.bot.send_document(chat_id=query.message.chat_id, document=product['link'], caption=f"شكراً لشرائك من LEEN SHOP ✨")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()
