import os
import threading
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
# 🧠 SMART HANDLER (SALES AI)
# =========================
async def smart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    selected = context.user_data.get('selected_prod')

    # --- NO PRODUCT SELECTED ---
    if not selected:

        # 💰 objection handling
        if "price" in text or "expensive" in text or "غالي" in text:
            await update.message.reply_text(
                "💡 I understand 👍\n\n"
                "💰 Launch Offer: $37\n"
                "⏳ Limited 48-hour access only\n\n"
                "⚡ After this period price increases\n\n"
                "👉 Type /start to view system"
            )
            return

        # 🤔 hesitation
        if "not sure" in text or "help" in text or "confused" in text:
            await update.message.reply_text(
                "💡 No problem 👍\n\n"
                "You can preview the system first.\n"
                "Then decide later.\n\n"
                "👉 Type /start"
            )
            return

        # fallback
        await update.message.reply_text(
            "👆 Please select a product first.\n\nType /start"
        )
        return

    # --- POST PURCHASE FLOW ---
    await update.message.reply_text(
        "💡 If you're ready, send TXID after payment.\n\n"
        "Or type /start to go back."
    )

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🗓️ 90-Day System ($37)", callback_data='prod2')],
        [InlineKeyboardButton("📄 Free Sample Preview", callback_data='sample')],
        [InlineKeyboardButton("⏳ LIMITED OFFER", callback_data='urgency')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "👑 Welcome to Leen Shop\n\n"
        "This is not a planner.\n"
        "This is a 90-day execution system.\n\n"
        "⚡ Build discipline\n"
        "⚡ Stay focused\n"
        "⚡ Execute daily\n\n"
        "⏳ LIMITED 48-HOUR LAUNCH OFFER\n"
        "💰 Price: $37\n\n"
        "👇 Choose below:"
    )

    await update.message.reply_text(msg, reply_markup=reply_markup)

# =========================
# BUTTONS
# =========================
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prod_id = query.data

    # SAMPLE
    if prod_id == "sample":
        await query.edit_message_text(
            "📄 SAMPLE\n\n"
            "✔ Daily structure\n"
            "✔ Habit tracking\n\n"
            f"👉 Download:\n{SAMPLE_LINK}\n\n"
            "💡 Full system is much stronger."
        )
        return

    # URGENCY
    if prod_id == "urgency":
        await query.edit_message_text(
            "⏳ LIMITED OFFER\n\n"
            "⚡ 48-hour launch active\n"
            "After that price increases.\n\n"
            "👉 Act now."
        )
        return

    # PRODUCT
    context.user_data['selected_prod'] = prod_id
    prod = PRODUCTS[prod_id]

    msg = (
        f"🔥 {prod['name_en']}\n\n"
        "This is a full execution system.\n\n"
        "✔ Structure\n"
        "✔ Discipline system\n"
        "✔ Focus framework\n\n"
        f"💰 Launch Offer: ${prod['price']}\n"
        "⏳ Limited 48-hour access\n\n"
        f"Wallet:\n`{MY_WALLET}`\n\n"
        "👉 Send TXID after payment"
    )

    await query.edit_message_text(text=msg, parse_mode='Markdown')

# =========================
# TXID
# =========================
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

# =========================
# MAIN
# =========================
def main():
    token = os.environ.get("TOKEN")
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_selection))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_handler))

    threading.Thread(target=run_flask, daemon=True).start()

    print("Bot running...")
    application.run_polling()

if __name__ == '__main__':
    main()
