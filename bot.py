import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "ضعي_التوكن_حق_البوت_هنا"
WALLET = "THcyK4g5HzhwJQ7c8a9NNMXb9EnrM9qZBh"

FILES = {
    "fashion": {"name": "دليل الأزياء الراقية", "price": 4, "link": "حطي_رابط_PDF_1"},
    "projects": {"name": "300 فكرة مشروع", "price": 3, "link": "حطي_رابط_PDF_2"},
    "richdad": {"name": "ملخص كتاب الأب الغني", "price": 2, "link": "حطي_رابط_PDF_3"},
    "habits": {"name": "كتاب العادات الذرية", "price": 3, "link": "حطي_رابط_PDF_4"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(f"{v['name']} - {v['price']}$", callback_data=k)] for k,v in FILES.items()]
    await update.message.reply_text("مرحبا في متجر Leen 🌸\nاختاري الكتاب:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = FILES[query.data]
    text = f"📚 {item['name']}\n💵 السعر: {item['price']}$ USDT\n\n🔸 حولي المبلغ على محفظة TRC20:\n`{WALLET}`\n\nبعد التحويل أرسلي صورة الإيصال هنا"
    await query.edit_message_text(text, parse_mode='Markdown')
    context.user_data['waiting_for'] = query.data

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'waiting_for' in context.user_data:
        item = FILES[context.user_data['waiting_for']]
        await update.message.reply_text(f"تم استلام الإيصال ✅\nجاري التحقق...\n\n📥 رابط التحميل:\n{item['link']}")
        context.user_data.clear()
    else:
        await update.message.reply_text("اضغطي /start أول")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.run_polling()
