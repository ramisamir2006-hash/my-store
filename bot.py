import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# --- الإعدادات ---
TOKEN = '8234943697:AAGOJdQ0hL3f9XBS_2-ACvrb2Pnnpqsp7tw'
ADMIN_ID = 7020070481
CHANNEL_ID = '@mariajewelery' 

# مراحل المحادثة (الخطوات المنفصلة)
GET_PHOTO, GET_PRICE, GET_DETAILS, GET_CATEGORY, CONFIRM_PUBLISH = range(5)

# قائمة الأقسام (يمكنك تعديلها حسب رغبتك)
CATEGORIES = ["ذهب عيار 21", "أطقم كاملة", "خواتم", "انسيالات", "هدايا"]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- البداية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("✨ مرحباً بك في متجر ماريا للمجوهرات.")
        return

    keyboard = [[InlineKeyboardButton("➕ إضافة منتج جديد", callback_data='start_add')]]
    await update.message.reply_text("🎮 **لوحة التحكم**\nاضغط للبدء في تجهيز منتج للنشر:", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))

# --- الخطوة 1: استلام الصورة ---
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("📸 **1. أرسل صورة المنتج:**")
    return GET_PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p_photo'] = update.message.photo[-1].file_id
    await update.message.reply_text("💰 **2. أرسل سعر المنتج فقط:**")
    return GET_PRICE

# --- الخطوة 2: استلام السعر ---
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p_price'] = update.message.text
    await update.message.reply_text("✍️ **3. اكتب التفاصيل والكلمات التسويقية:**")
    return GET_DETAILS

# --- الخطوة 3: استلام التفاصيل ---
async def get_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p_desc'] = update.message.text
    # عرض قائمة الأقسام كأزرار كبيرة
    reply_markup = ReplyKeyboardMarkup([[cat] for cat in CATEGORIES], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("📂 **4. اختر القسم المناسب:**", reply_markup=reply_markup)
    return GET_CATEGORY

# --- الخطوة 4: استلام القسم وعمل المعاينة ---
async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['p_cat'] = update.message.text
    
    # تجهيز شكل المنشور النهائي للمعاينة
    preview_msg = (
        f"📂 القسم: {context.user_data['p_cat']}\n"
        f"✨ **{context.user_data['p_desc']}**\n\n"
        f"💰 السعر: {context.user_data['p_price']}\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"🛒 اطلب الآن: @ramysamir2006"
    )
    
    # حفظ النص النهائي للنشر
    context.user_data['final_caption'] = preview_msg
    
    keyboard = [
        [InlineKeyboardButton("✅ نشر في القناة", callback_data='confirm_pub')],
        [InlineKeyboardButton("❌ إلغاء وتعديل", callback_data='cancel_add')]
    ]
    
    await update.message.reply_photo(
        photo=context.user_data['p_photo'],
        caption=f"🔍 **معاينة المنشور:**\n\n{preview_msg}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    return CONFIRM_PUBLISH

# --- الخطوة الأخيرة: النشر الفعلي في القناة ---
async def publish_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'confirm_pub':
        # أزرار السلة والاستفسار تحت المنشور في القناة
        keyboard = [
            [InlineKeyboardButton("🛒 إضافة للسلة", callback_data="add_to_cart")],
            [InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/ramysamir2006"),
             InlineKeyboardButton("📋 عرض السلة", callback_data="view_cart")]
        ]
        
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=context.user_data['p_photo'],
            caption=context.user_data['final_caption'],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.reply_text("🚀 تم النشر في القناة بنجاح!", reply_markup=ReplyKeyboardRemove())
    else:
        await query.message.reply_text("تم الإلغاء. يمكنك البدء من جديد عبر /start", reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- التشغيل ---
def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add, pattern='^start_add$')],
        states={
            GET_PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            GET_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            GET_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_details)],
            GET_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_category)],
            CONFIRM_PUBLISH: [CallbackQueryHandler(publish_now)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
