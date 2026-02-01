import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# إعداد السجلات لمراقبة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعريف مراحل العمل
PHOTO, PRICE, CATEGORY, DESCRIPTION, SIZES, PREVIEW = range(6)

# بيانات أساسية (يجب تعبئتها)
BOT_TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtl8XAFSRUy rX3I" # التوكن من صورتك الأولى
CHANNEL_ID = "@YourChannelUsername" # اسم معرف قناتك يبدأ بـ @

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 أهلاً بك في لوحة تحكم متجرك.\nاضغط على الزر بالأسفل للبدء:",
        reply_markup=ReplyKeyboardMarkup([['➕ إضافة منتج جديد']], resize_keyboard=True)
    )
    return ConversationHandler.END

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1️⃣ أرسل صورة المنتج الآن:")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("2️⃣ ممتاز! الآن أرسل **السعر** (مثلاً: 45 ج.م):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("3️⃣ ما هو **قسم المنتج**؟ (مثلاً: سلاسل، خواتم):")
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("4️⃣ اكتب **وصف المنتج**:")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    await update.message.reply_text("5️⃣ حدد **المقاسات** المتاحة:")
    return SIZES

async def get_sizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sizes'] = update.message.text
    
    # بناء نص المنشور النهائي
    caption = (
        f"{context.user_data['description']}\n\n"
        f"\\# {context.user_data['category'].replace(' ', '_')}\n"
        f"📏 المقاسات: {context.user_data['sizes']}\n\n"
        f"💰 **السعر: {context.user_data['price']}**"
    )
    context.user_data['final_caption'] = caption

    # أزرار المعاينة للمدير
    keyboard = [
        [InlineKeyboardButton("✅ نشر في القناة", callback_data="publish")],
        [InlineKeyboardButton("❌ إلغاء وتعديل", callback_data="cancel")]
    ]
    
    await update.message.reply_photo(
        photo=context.user_data['photo'],
        caption=f"🔍 **معاينة المنشور:**\n\n{caption}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return PREVIEW

async def publish_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # أزرار العميل (التي تظهر للناس في القناة)
    client_keyboard = [
        [InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/YourAdminUsername")], # رابط مراسلة الأدمن
        [InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url="https://t.me/YourChannelUsername")],
        [InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/YourAdminUsername")]
    ]

    # النشر الفعلي في القناة
    await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=context.user_data['photo'],
        caption=context.user_data['final_caption'],
        reply_markup=InlineKeyboardMarkup(client_keyboard),
        parse_mode="Markdown"
    )
    
    await query.edit_message_caption(caption="✅ تم النشر بنجاح في القناة!")
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^➕ إضافة منتج جديد$'), add_product_start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            SIZES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sizes)],
            PREVIEW: [CallbackQueryHandler(publish_to_channel, pattern="^publish$")]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
    
