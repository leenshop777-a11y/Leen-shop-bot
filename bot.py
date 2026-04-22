import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== 1. حط توكن البوت حقك هنا =====
TOKEN = " 8432218715:AAGCaMGfnGc6pXfiOUf2reCRu1ThzvENGk4" # ⚠️ من BotFather

# ===== 2. منتجاتك الحقيقية - جاهزة =====
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
        "price_ar":"27"دولار
        "price_en": "$27",
        "desc_ar": "برنامج لين سليم سيكريت برو الاحترافي. تواصل معنا لمعرفة السعر والتفاصيل.",
        "desc_en": "Leen Slim Secret Pro program. Contact us for price and details.",
        "link": "https://drive.google.com/file/d/1ZD9XWSD1jmczhJix7DbZ_EJ0ccAvyLRt/view?usp=drivesdk"
    }
}

# ===== 3. نصوص البوت باللغتين =====
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

# ===== 4. دوال البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("العربية 🇸🇦", callback_data='lang_ar')],
        [InlineKeyboardButton("English 🇺🇸", callback_data='lang_en')]
    ]
    await update.message.reply_text(TEXTS["ar"]["welcome
