from flask import Flask
from threading import Thread
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# هذا السيرفر الوهمي عشان Render ما يطفي البوت
app = Flask('')

@app.route('/')
def home():
    return "Leen Shop Bot is alive!"

def run():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# كود البوت حقك يبدأ من هنا
BOT_TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً فيك في متجر لين 🌸\nاكتبي /help للمساعدة')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أوامر البوت:\n/start - بداية\n/help - المساعدة')

if __name__ == '__main__':
    keep_alive()  # شغلي السيرفر الوهمي أول
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    
    print("Bot is running...")
    application.run_polling()
