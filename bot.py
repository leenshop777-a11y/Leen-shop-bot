import os
import asyncio
import random
import sqlite3
import requests
import threading
import time
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
WALLET = "TNLtMGhQbTWpHkwKiWuAMMC95hhe6e1Qkn"
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# قاعدة البيانات
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

# المنتجات
PRODUCTS = {
    "p1": {"name": "From Zero to $1000", "price": 47, "link": "https://drive.google.com/file/d/1VNKROsJLSddq3wVXGreexfZk7GxXKSWb/view"},
    "p2": {"name": "Royal 90 Day Planner", "price": 37, "link": "https://drive.google.com/file/d/10JqPCJ4DsRn_8grXNZR2Y0KswypHF4YI/view"},
    "p3": {"name": "Leen Slim Secret", "price": 27, "link": "https://drive.google.com/file/d/1ZD9XWSD1jmczhJix7DbZ_EJ0ccAvyLRt/view"}
}

def generate_price(base):
    return round(base + random.uniform(0.01, 0.09), 2)

def create_order(chat_id, product_id):
    price = generate_price(PRODUCTS[product_id]["price"])
    cursor.execute("INSERT INTO orders (chat_id, product_id, price) VALUES (?,?,?)",
                   (chat_id, product_id, price))
    conn.commit()
    return price

def get_transactions():
    try:
        url = f"https://apilist.tronscan.org/api/transaction?address={WALLET}"
        return requests.get(url, timeout=10).json()
    except:
        return {"data": []}

def check_payments():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
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
                    cursor.execute("UPDATE orders SET paid=1, txid=? WHERE id=?", (txid, order_id))
                    conn.commit()
                    product = PRODUCTS[product_id]
                    loop.run_until_complete(
                        application.bot.send_message(chat_id, f"✅ Payment received!\n\n🔗 Download:\n{product['link']}")
                    )
        except Exception as e:
            print(f"Payment check error: {e}")

        time.sleep(15)

# بدء الشراء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_id = context.args[0]
    except:
        await update.message.reply_text("Choose product from website. Example: /start p1")
        return

    if product_id in PRODUCTS:
        price = create_order(update.effective_chat.id, product_id)
        await update.message.reply_text(f"""
📦 Product: {PRODUCTS[product_id]['name']}

💰 Send: {price} USDT (TRC20)

💳 Address:
{WALLET}

⏳ Auto delivery after payment
""")
    else:
        await update.message.reply_text("Product not found")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot running"

async def setup_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    await application.bot.set_webhook(url=webhook_url)
    print(f"Webhook set to: {webhook_url}")

if __name__ == "__main__":
    # 1. شغل check_payments في ثريد منفصل
    threading.Thread(target=check_payments, daemon=True).start()

    # 2. اضبط الهوك
    asyncio.run(setup_webhook())

    # 3. شغل Flask
    app.run(host="0.0.0.0", port=PORT)
