import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ====== الإعدادات | Settings ======
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ====== بياناتك | Your Data ======
CARDD_URL = "https://leenshop777.carrd.co"
WHATSAPP_NUMBER = "967782737225"
# ====== بياناتك | Your Data ======

# ====== النصوص | Texts ======
TEXTS = {
    "start": """
أهلاً بك في متجر لين | Welcome to Leen Shop 🛒

من الصفر إلى ألف دولار | From Zero to $1000

اختر من القائمة: | Choose an option:
    """,
    
    "help": """
أوامر بوت متجر لين | Leen Shop Bot Commands

/start - القائمة الرئيسية | Main menu
/help - عرض المساعدة | Show help
/contact - تواصل معنا | Contact us

للتسوق اضغط "زيارة المتجر" | To shop click "Visit Store"
    """,
    
    "contact": f"""
تواصل معنا | Contact Us

واتساب | WhatsApp: https://wa.me/{WHATSAPP_NUMBER}
تيليجرام | Telegram: @LeenShopSupport

أوقات العمل: 9 ص - 9 م | Working hours: 9 AM - 9 PM
    """,
    
    "about": """
متجر لين | Leen Shop

نساعدك تبدأ رحلتك من الصفر إلى ألف دولار
We help you start your journey from zero to $1000

منتجات رقمية بجودة عالية | High quality digital products
تحميل فوري بعد الدفع | Instant download after payment
    """
}

# ====== الأزرار | Buttons ======
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("زيارة المتجر | Visit Store 🛒", url=CARDD_URL)],
        [InlineKeyboardButton("تواصل واتساب | WhatsApp 📞", url=f"https://wa.me/{WHATSAPP_NUMBER}")],
        [InlineKeyboardButton("عن المتجر | About ℹ️", callback_data='about')],
        [InlineKeyboardButton("مساعدة | Help ❓", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    keyboard = [[InlineKeyboardButton("رجوع للقائمة | Back to Menu 🔙", callback_data='start')]]
    return InlineKeyboardMarkup(keyboard)

# ====== الأوامر | Commands ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["start"], reply_markup=main_menu_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["help"], reply_markup=back_keyboard())

# ====== الأزرار | Button Handler ======
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start':
        await query.edit_message_text(TEXTS["start"], reply_markup=main_menu_keyboard())
    elif query.data == 'about':
        await query.edit_message_text(TEXTS["about"], reply_markup=back_keyboard())
    elif query.data == 'help':
        await query.edit_message_text(TEXTS["help"], reply_markup=back_keyboard())

# ====== تشغيل البوت | Run Bot ======
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
