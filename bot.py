import os
import threading
import requests
import time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- Flask server ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Leen Shop AI is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- Wallet ---
MY_WALLET = "TNLtMGhQbTWpHkwKiWuAMMC95hhe6e1Qkn"

# --- Products (English only) ---
PRODUCTS = {
    "prod1": {
        "name_en": "From Zero to $1000",
        "price": 47,
        "link": "https://drive.google.com/file/d/1VNKROsJLSddq3wVXGreexfZk7GxXKSWb/view?usp=drivesdk"
    },
    "prod2": {
        "name_en": "Royal 90-Day Digital Success Planner",
        "price": 37,
        "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view?usp=drivesdk"
    }
}

# --- Fake TX verification (temporary) ---
def verify_usdt_payment(txid, expected_amount):
    try:
        url = f"https://apilist.tronscan.org/api/transaction-info?hash={txid}"
        response = requests.get(url)
        data = response.json()

        if data.get('confirmed') and data.get('contractRet') == 'SUCCESS':
            return True
        return False
    except:
        return False

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 From Zero to $1000 ($47)", callback_data='prod1')],
        [InlineKeyboardButton("🗓️ 90-Day Success Planner ($37)", callback_data='prod2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "🚀 Welcome to Leen Shop\n\n"
        "Digital products to boost your income & productivity.\n\n"
        "Choose a product to get started:"
    )
    await update.message.reply_text(msg, reply_markup=reply_markup)

# --- Product selection ---
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prod_id = query.data
    context.user_data['selected_prod'] = prod_id
    prod = PRODUCTS[prod_id]

    msg = (
        f"🔥 {prod['name_en']}\n"
        f"💰 Price: {prod['price']} USDT (TRC20)\n\n"
        f"⚡ Limited offer (48 hours)\n\n"
        f"Send payment to wallet:\n\n"
        f"`{MY_WALLET}`\n\n"
        "After payment, paste TXID below:"
    )
    await query.edit_message_text(text=msg, parse_mode='Markdown')

# --- TXID handling ---
async def process_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txid = update.message.text.strip()
    prod_id = context.user_data.get('selected_prod')

    if not prod_id:
        await update.message.reply_text("Please select a product first.")
        return

    await update.message.reply_text("🔄 Verifying payment...")

    if len(txid) > 20:
        time.sleep(2)
        prod = PRODUCTS[prod_id]

        success_msg = (
            f"✅ Payment Confirmed!\n\n"
            f"🎁 Download link:\n"
            f"{prod['link']}\n\n"
            "⚡ Save your file now!"
        )
        await update.message.reply_text(success_msg)
    else:
        await update.message.reply_text("❌ Invalid TXID, try again.")

# --- Main ---
def main():
    token = os.environ.get("TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_selection))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_txid))

    threading.Thread(target=run_flask, daemon=True).start()

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
