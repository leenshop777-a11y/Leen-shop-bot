import os
import threading
import requests
import asyncio
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

# --- Sample ---
SAMPLE_LINK = "https://drive.google.com/file/d/1bdrOs0poBRfqiEma0Sdy4DXJXANMpY8z/view?usp=drivesdk"

# --- Products ---
PRODUCTS = {
    "prod2": {
        "name_en": "Royal 90-Day Execution System",
        "price": 37,
        "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view?usp=drivesdk"
    }
}

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗓️ 90-Day System ($37)", callback_data='prod2')],
        [InlineKeyboardButton("📄 Free Sample Preview", callback_data='sample')],
        [InlineKeyboardButton("⏳ OFFER ENDING SOON", callback_data='urgency')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "👑 Welcome to Leen Shop\n\n"
        "This is not a planner…\n"
        "This is a complete execution system.\n\n"
        "⚡ Build discipline\n"
        "⚡ Stay focused\n"
        "⚡ Execute daily without overthinking\n\n"
        "⏳ LIMITED 48-HOUR LAUNCH OFFER\n"
        "After that → price increases\n\n"
        "💰 Current price: $37\n\n"
        "👇 Choose below:"
    )

    await update.message.reply_text(msg, reply_markup=reply_markup)

# --- Handle buttons ---
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prod_id = query.data

    # --- SAMPLE ---
    if prod_id == "sample":
        await query.edit_message_text(
            "📄 SAMPLE PREVIEW\n\n"
            "✔ Daily structure sample\n"
            "✔ Habit tracking preview\n"
            "✔ Execution layout example\n\n"
            f"👉 Download sample:\n{SAMPLE_LINK}\n\n"
            "⚠ This is only a small preview.\n\n"
            "The full system includes:\n"
            "✔ Full 90-day structure\n"
            "✔ Complete execution system\n"
            "✔ Real discipline framework\n\n"
            "👉 If you're serious, unlock full version now."
        )
        return

    # --- URGENCY ---
    if prod_id == "urgency":
        await query.edit_message_text(
            "⏳ OFFER ENDING SOON\n\n"
            "⚡ 48-Hour Launch Offer Active\n\n"
            "After it ends:\n"
            "❌ Price increases\n"
            "❌ Offer removed\n\n"
            "💰 Current price is temporary\n\n"
            "👉 Act now before it's gone"
        )
        return

    # --- PRODUCT FLOW ---
    context.user_data['selected_prod'] = prod_id
    prod = PRODUCTS[prod_id]

    msg = (
        f"🔥 {prod['name_en']}\n\n"
        "This is not a PDF.\n"
        "This is a complete life organization system.\n\n"
        "What you get:\n"
        "✔ Daily structure\n"
        "✔ Habit tracking system\n"
        "✔ Focus & discipline framework\n\n"
        "Results:\n"
        "→ More focus\n"
        "→ Less procrastination\n"
        "→ Real execution\n\n"
        "🔥 Already used by multiple users\n\n"
        f"💰 Price: {prod['price']} USDT (TRC20)\n\n"
        "⏳ Limited 48-hour offer\n\n"
        f"Send payment to wallet:\n\n"
        f"`{MY_WALLET}`\n\n"
        "👉 After payment, send TXID below"
    )

    await query.edit_message_text(text=msg, parse_mode='Markdown')

# --- TXID ---
async def process_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txid = update.message.text.strip()
    prod_id = context.user_data.get('selected_prod')

    if not prod_id:
        await update.message.reply_text("Please select a product first.")
        return

    await update.message.reply_text("🔄 Verifying payment...")

    if len(txid) > 20:
        await asyncio.sleep(2)

        prod = PRODUCTS[prod_id]

        success_msg = (
            "✅ PAYMENT CONFIRMED!\n\n"
            f"🎁 Download your system:\n{prod['link']}\n\n"
            "👑 You now have access.\n\n"
            "Most people buy and never use.\n\n"
            "If you follow this system:\n"
            "→ Your life can change in 90 days\n\n"
            "⚡ Start today."
        )

        await update.message.reply_text(success_msg)
    else:
        await update.message.reply_text(
            "❌ Invalid TXID\n\n"
            "👉 Please check and try again."
        )

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
