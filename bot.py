import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

# إعداد السجلات لمتابعة أداء البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعريف مراحل إدخال بيانات المنتج
PHOTO, PRICE, CATEGORY, DESCRIPTION, SIZES, PREVIEW = range(6)

# --- البيانات الأساسية الخاصة بك ---
BOT_TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtl8XAFSRUyrX3I" 
CHANNEL_ID = "@RamySamir2026Gold"  # اسم قناتك المعدل
ADMIN_USERNAME = "RamySamir2026Gold" # اسم المستخدم الخاص بك لتلقي الطلبات
# ----------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 أهلاً بك في لوحة تحكم متجر الحريمي.\nاستخدم الزر بالأسفل لإضافة منتجاتك:",
        reply_markup=ReplyKeyboardMarkup([['➕ إضافة منتج جديد']], resize_keyboard=True)
    )
    return ConversationHandler.END

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1️⃣ أرسل صورة المنتج الآن:")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("2️⃣ ممتاز! أرسل الآن **السعر** (مثال: 45 ج.م):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("3️⃣ اختر **القسم** أو اكتبه (مثال: سلاسل، خواتم):")
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("4️⃣ أرسل **وصف المنتج** بالتفصيل:")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    await update.message.reply_text("5️⃣ حدد **المقاسات** المتاحة لهذا المنتج:")
    return SIZES

async def get_sizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sizes'] = update.message.text
    
    # بناء شكل المنشور النهائي
    caption = (
        f"{context.user_data['description']}\n\n"
        f"\\# {context.user_data['category'].replace(' ', '_')}\n"
        f"📏 المقاسات: {context.user_data['sizes']}\n\n"
        f"💰 **السعر: {context.user_data['price']}**"
    )
    context.user_data['final_caption'] = caption

    # أزرار التحكم للمدير
    keyboard = [
        [InlineKeyboardButton("✅ نشر في القناة الآن", callback_data="publish_now")],
        [InlineKeyboardButton("❌ إلغاء العملية", callback_data="cancel_post")]
    ]
    
    await update.message.reply_photo(
        photo=context.user_data['photo'],
        caption=f"🔍 **معاينة المنشور:**\n\n{caption}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return PREVIEW

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "publish_now":
        # أزرار العميل التي تظهر في القناة
        client_buttons = [
            [InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/{ADMIN_USERNAME}")],
            [InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("💬 استفسار / مساعدة", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]

        # إرسال الصورة والبيانات للقناة
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=context.user_data['photo'],
            caption=context.user_data['final_caption'],
            reply_markup=InlineKeyboardMarkup(client_buttons),
            parse_mode="Markdown"
        )
        await query.edit_message_caption(caption="✅ تم النشر بنجاح في القناة!")
    
    elif query.data == "cancel_post":
        await query.edit_message_caption(caption="❌ تم إلغاء المنشور.")
    
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
            PREVIEW: [CallbackQueryHandler(handle_callback)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    
    print("البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()
    
