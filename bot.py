import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعريف الحالات (الخطوات)
PHOTO, PRICE, CATEGORY, DESCRIPTION, SIZES, PREVIEW = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً بك في لوحة تحكم التاجر 🏪\nإليك الأوامر المتاحة:",
        reply_markup=ReplyKeyboardMarkup([['➕ إضافة منتج جديد']], resize_keyboard=True)
    )

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1️⃣ أرسل صورة المنتج (أو صور متعددة ثم اضغط 'تم')")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    context.user_data['photo'] = photo_file
    await update.message.reply_text("✅ تم استقبال الصورة. \n2️⃣ الآن أرسل **سعر المنتج** (مثلاً: 45 ج.م):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("3️⃣ اختر **القسم** أو اكتبه (مثلاً: سلاسل، خواتم):")
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("4️⃣ أرسل **وصف المنتج** بالتفصيل:")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    await update.message.reply_text("5️⃣ أرسل **المقاسات المتاحة** (مثلاً: M, L, XL):")
    return SIZES

async def get_sizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sizes'] = update.message.text
    
    # بناء المعاينة
    preview_text = (
        f"🔍 **معاينة المنتج قبل النشر:**\n\n"
        f"📝 الوصف: {context.user_data['description']}\n"
        f"🏷 القسم: #{context.user_data['category']}\n"
        f"📏 المقاسات: {context.user_data['sizes']}\n"
        f"💰 السعر: {context.user_data['price']}"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ نشر الآن", callback_query_handler="publish"),
         InlineKeyboardButton("❌ تعديل", callback_query_handler="edit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo=context.user_data['photo'],
        caption=preview_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return PREVIEW

# إضافة بقية الدوال الخاصة بالنشر والتعديل هنا...

def main():
    # ضع التوكن الخاص بك هنا الذي حصلت عليه من BotFather
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" 
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^➕ إضافة منتج جديد$'), add_product_start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            SIZES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sizes)],
        },
        fallbacks=[CommandHandler('cancel', start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
