import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعريف الخطوات
PHOTO, PRICE, CATEGORY, DESCRIPTION, SIZES, PREVIEW = range(6)

# --- بياناتك الأساسية ---
BOT_TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtl8XAFSRUyrX3I"
CHANNEL_ID = "@RamySamir2026Gold" 
ADMIN_USERNAME = "RamySamir2026Gold" 
# -----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 لوحة تحكم متجر الحريمي\nاضغط على الزر للبدء:",
        reply_markup=ReplyKeyboardMarkup([['➕ إضافة منتج جديد']], resize_keyboard=True)
    )
    # ملاحظة: حذفنا ConversationHandler.END هنا لضمان عدم كسر التسلسل
    return ConversationHandler.END

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1️⃣ أرسل صورة المنتج الآن:")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data['photo'] = update.message.photo[-1].file_id
        await update.message.reply_text("2️⃣ أرسل **السعر** (مثال: 150):")
        return PRICE
    else:
        await update.message.reply_text("الرجاء إرسال صورة صحيحة.")
        return PHOTO

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("3️⃣ أرسل **القسم** (مثال: سلاسل، خواتم):")
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
    
    caption = (
        f"{context.user_data['description']}\n\n"
        f"🏷 القسم: #{context.user_data['category'].replace(' ', '_')}\n"
        f"📏 المقاسات: {context.user_data['sizes']}\n\n"
        f"💰 **السعر: {context.user_data['price']}**"
    )
    context.user_data['final_caption'] = caption

    keyboard = [[InlineKeyboardButton("✅ نشر في القناة", callback_data="publish"),
                 InlineKeyboardButton("❌ إلغاء وتعديل", callback_data="cancel")]]
    
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

    if query.data == "publish":
        client_buttons = [
            [InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/{ADMIN_USERNAME}")],
            [InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url=f"https://t.me/{CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("💬 استفسار / مساعدة", url=f"https://t.me/{ADMIN_USERNAME}")]
        ]
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=context.user_data['photo'], 
                                   caption=context.user_data['final_caption'], reply_markup=InlineKeyboardMarkup(client_buttons), parse_mode="Markdown")
        await query.edit_message_caption(caption="✅ تم النشر بنجاح في القناة!")
    else:
        await query.edit_message_caption(caption="❌ تم إلغاء العملية.")
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
    application.run_polling()

if __name__ == '__main__':
    main()
    
