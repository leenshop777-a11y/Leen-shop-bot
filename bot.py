import os
import asyncio
import random
import sqlite3
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = "https://leen-shop-bot-3.onrender.com"
WALLET = "TNLtMGhQbTWpHkwKiWuAMMC95hhe6e1Qkn"

app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

# قاعدة بيانات
conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    product_id TEXT,
    price REAL,
    paid INTEGER DEFAULT 0,
    txid TEXT
)
""")
conn.commit()

PRODUCTS = {
    "p1": {"name": "From Zero to $1000", "price": 47,
           "link": "https://drive.google.com/file/d/1VNKROsJLSddq3wVXGreexfZk7GxXKSWb/view"},
    "p2": {"name": "Royal Planner", "price": 37,
           "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view"},
    "p3": {"name": "Leen Slim", "price": 27,
           "link": "https://drive.google.com/file/d/1ZD9XWSD1jmczhJix7DbZ_EJ0ccAvyLRt/view"}
}

def generate_price(base):
    return round(base + random.uniform(0.01, 0.09), 2)

def create_order(chat_id, product_id):
    price = generate_price(PRODUCTS[product_id]["price"])
    cursor.execute("INSERT INTO orders (chat_id, product_id, price) VALUES (?, ?, ?)",
                   (chat_id, product_id, price))
    conn.commit()
    return price

def get_transactions():
    url = f"https://apilist.tronscan.org/api/transaction?address={WALLET}"
    return requests.get(url).json()

def check_payments():
    while True:
        data = get_transactions()
        for tx in data.get("data", []):
            amount = tx.get("contractData", {}).get("amount", 0) / 1e6
            txid = tx.get("hash")

            cursor.execute("SELECT * FROM orders WHERE txid=?", (txid,))
            if cursor.fetchone():
                continue

            cursor.execute("SELECT * FROM orders WHERE price=? AND paid=0", (amount,))
            order = cursor.fetchone()

            if order:
                order_id, chat_id, product_id, price, paid, _ = order
                cursor.execute("UPDATE orders SET paid=1, txid=? WHERE id=?",
                               (txid, order_id))
                conn.commit()

                product = PRODUCTS[product_id]

                asyncio.run(
                    application.bot.send_message(chat_id,
                        f"✅ Payment received!\n\n🔗 {product['link']}")
                )

        import time
        time.sleep(15)

# أمر start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_id = context.args[0]
    except:
        await update.message.reply_text("Choose product from website")
        return

    if product_id in PRODUCTS:
        price = create_order(update.effective_chat.id, product_id)

        await update.message.reply_text(
            f"""📦 {PRODUCTS[product_id]['name']}

💰 Send: {price} USDT (TRC20)

💳 Address:
{WALLET}

⏳ Auto delivery after payment"""
        )

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def home():
    return "Bot running ✅"

# تشغيل الخلفية
import threading
threading.Thread(target=check_payments).start()

# ضبط webhook
asyncio.run(application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}"))
