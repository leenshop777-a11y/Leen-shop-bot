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

# =========================
# 🧠 SMART MESSAGE HANDLER (NEW)
# =========================
async def smart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    selected = context.user_data.get('selected_prod')

    # --- NO PRODUCT SELECTED ---
    if not selected:

        # 💰 Price objection
        if "price" in text or "expensive" in text or "غالي" in text:
            await update.message.reply_text(
                "💡 I understand 👍\n\n"
                "This is a limited 48-hour launch offer.\n"
                "After that, price increases.\n\n"
                "Most users start and see value after first week.\n\n"
                "👉 Type /start to view the system"
            )
            return

        # 🤔 hesitation
        if "not sure" in text or "help" in text or "confused" in text:
            await update.message.reply_text(
                "💡 No problem 👍\n\n"
                "You can preview the system first.\n"
                "Then decide if it fits you.\n\n"
                "👉 Type /start to continue"
            )
            return

        # 🔄 general fallback
        await update.message.reply_text(
            "👆 Please choose a product first.\n\nType /start to begin."
        )
        return

    # --- USER HAS PRODUCT BUT CHATTER ---
    await update.message.reply_text(
        "💡 If you're ready, send TXID after payment.\n\n"
        "Or type /start to choose another option."
    )

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗓️ 90-Day System ($37)", callback_data='prod2')],
        [InlineKeyboardButton("📄 Free Sample Preview", callback_data='sample')],
        [InlineKeyboardButton("⏳ OFFER STATUS", callback_data='urgency')]
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
        "💰 Current price: $37\n\n"
        "👇 Choose below:"
    )

    await update.message.reply_text(msg, reply_markup=reply_markup)

# --- BUTTON HANDLER ---
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prod_id = query.data

    # --- SAMPLE ---
    if prod_id == "sample":
        await query.edit_message_text(
            "📄 SAMPLE PREVIEW\n\n"
            "✔ Daily structure sample\n"
            "✔ Habit tracking preview\n\n"
            f"👉 Download:\n{SAMPLE_LINK}\n\n"
            "💡 Full system is much more powerful."
        )
        return

    # --- URGENCY ---
    if prod_id == "urgency":
        await query.edit_message_text(
            "⏳ LIMITED OFFER\n\n"
            "⚡ 48-hour launch active\n"
            "After that price increases.\n\n"
            "👉 Recommended to act now."
        )
        return

    # --- PRODUCT ---
    context.user_data['selected_prod'] = prod_id
    prod = PRODUCTS[prod_id]

    msg = (
        f"🔥 {prod['name_en']}\n\n"
        "This is a full execution system.\n\n"
        "✔ Daily structure\n"
        "✔ Discipline framework\n"
        "✔ Focus system\n\n"
        f"💰 Price: {prod['price']} USDT\n\n"
        "⏳ Limited 48-hour offer\n\n"
        f"Wallet:\n`{MY_WALLET}`\n\n"
        "👉 Send TXID after payment"
    )

    await query.edit_message_text(text=msg, parse_mode='Markdown')

# --- TXID ---
async def process_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txid = update.message.text.strip()
    prod_id = context.user_data.get('selected_prod')

    if not prod_id:
        await update.message.reply_text("Please select a product first.")
        return

    await update.message.reply_text("🔄 Verifying...")

    if len(txid) > 20:
        await asyncio.sleep(2)

        prod = PRODUCTS[prod_id]

        await update.message.reply_text(
            "✅ PAYMENT CONFIRMED!\n\n"
            f"🎁 Download:\n{prod['link']}\n\n"
            "⚡ Start immediately and stay consistent."
        )
    else:
        await update.message.reply_text("❌ Invalid TXID")

# --- MAIN ---
def main():
    token = os.environ.get("TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_selection))

    # 🧠 SMART SYSTEM (important)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_handler))

    threading.Thread(target=run_flask, daemon=True).start()

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
