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

# الإعدادات الأساسية
TOKEN = os.getenv("TOKEN")
WALLET = "TNLtMGhQbTWpHkwKiWuAMMC95hhe6e1Qkn"

app = Flask(__name__)

# مسار بسيط للتأكد أن السيرفر Live
@app.route('/')
def home():
    return "Bot is Running Live!"

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

# إعداد البوت
application = Application.builder().token(TOKEN).build()

def generate_price(base):
    return round(base + random.uniform(0.01, 0.09), 2)

def create_order(chat_id, product_id):
    price = generate_price(PRODUCTS[product_id]["price"])
    cursor.execute("INSERT INTO orders (chat_id, product_id, price) VALUES (?,?,?)",
                   (chat_id, product_id, price))
    conn.commit()
    return price

# (هنا تضع بقية الدوال الخاصة بالتعامل مع العمليات و tronscan كما كانت في كودك)

async def start_bot():
    """تشغيل البوت بنظام Polling في الخلفية"""
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

if __name__ == "__main__":
    # تشغيل البوت في خيط (Thread) منفصل لكي لا يتوقف Flask
    threading.Thread(target=lambda: asyncio.run(start_bot())).start()
    
    # تشغيل Flask على المنفذ الذي يحدده Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
