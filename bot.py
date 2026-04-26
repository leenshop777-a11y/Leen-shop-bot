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

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Zero to $1000 ($47)", callback_data='prod1')],
        [InlineKeyboardButton("🗓️ 90-Day System ($37)", callback_data='prod2')],
        [InlineKeyboardButton("📄 Free Sample Preview", callback_data='sample')],
        [InlineKeyboardButton("⏳ LIMITED OFFER STATUS", callback_data='urgency')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "👑 Welcome to Leen Shop\n\n"
        "We don’t sell PDFs… we sell execution systems.\n\n"
        "⚡ 90-Day structured system for focus & productivity\n"
        "⚡ Built for real results, not theory\n\n"
        "⏳ LIMITED TIME OFFER: 48 HOURS ONLY\n"
        "After that, prices return to normal\n\n"
        "💰 Today: $19–$37 launch price\n\n"
        "👇 Choose your option below:"
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
            "✔ Habit tracker preview\n"
            "✔ System layout example\n\n"
            f"👉 Download:\n{SAMPLE_LINK}\n\n"
            "💰 Full system available after purchase."
        )
        return

    # --- URGENCY ---
    if prod_id == "urgency":
        await query.edit_message_text(
            "⏳ LIMITED OFFER STATUS\n\n"
            "⚡ Active: 48-Hour Launch Offer\n"
            "⚡ After timer ends → price increases\n\n"
            "💰 Status: ACTIVE NOW\n\n"
            "👉 Recommended to act now."
        )
        return

    # --- PRODUCT FLOW ---
    context.user_data['selected_prod'] = prod_id
    prod = PRODUCTS[prod_id]

    msg = (
        f"🔥 {prod['name_en']}\n\n"
        f"💰 Price: {prod['price']} USDT (TRC20)\n\n"
        "⚡ Instant access after payment\n"
        "⚡ Limited offer (48 hours only)\n\n"
        f"Send payment to wallet:\n\n"
        f"`{MY_WALLET}`\n\n"
        "👉 After payment, send TXID to verify automatically"
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
            f"🎁 Download link:\n{prod['link']}\n\n"
            "⚡ Save your file now\n"
            "👑 Thank you for your purchase!"
        )

        await update.message.reply_text(success_msg)
    else:
        await update.message.reply_text(
            "❌ Invalid TXID\n\n"
            "👉 Please double check and try again."
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
