import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler
from supabase import create_client

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تعريف المراحل
PHOTO, PRICE, CATEGORY, DESCRIPTION, SIZES, PREVIEW = range(6)

# الإعدادات (تأكد من وضعها في Koyeb Variables)
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = "@RamySamir2026Gold"
ADMIN_USERNAME = "RamySamir2026Gold"

# ربط قاعدة البيانات
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏪 أهلاً بك في لوحة تحكم my-store.\nاضغط على الزر لإضافة منتج جديد:",
        reply_markup=ReplyKeyboardMarkup([['➕ إضافة منتج جديد']], resize_keyboard=True)
    )
    return ConversationHandler.END

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1️⃣ أرسل صورة المنتج الآن:")
    return PHOTO

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo_id'] = update.message.photo[-1].file_id
    # الحصول على رابط الصورة الفعلي لتخزينه في الموقع
    file = await context.bot.get_file(context.user_data['photo_id'])
    context.user_data['photo_url'] = file.file_path
    
    await update.message.reply_text("2️⃣ أرسل السعر (مثال: 150):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    await update.message.reply_text("3️⃣ اختر القسم (خواتم، سلاسل...):")
    return CATEGORY

async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("4️⃣ أرسل وصف المنتج:")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text
    await update.message.reply_text("5️⃣ حدد المقاسات المتاحة:")
    return SIZES

async def get_sizes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['sizes'] = update.message.text
    
    caption = (
        f"✨ *{context.user_data['description']}*\n\n"
        f"🏷 القسم: #{context.user_data['category'].replace(' ', '_')}\n"
        f"📏 المقاسات: {context.user_data['sizes']}\n"
        f"💰 السعر: {context.user_data['price']} ج.م"
    )
    context.user_data['final_caption'] = caption

    keyboard = [
        [InlineKeyboardButton("✅ نشر في القناة والموقع", callback_data="publish_now")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post")]
    ]
    
    await update.message.reply_photo(
        photo=context.user_data['photo_id'],
        caption=f"🔍 معاينة المنشور:\n\n{caption}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return PREVIEW

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "publish_now":
        # 1. الحفظ في قاعدة بيانات الموقع (Supabase)
        try:
            supabase.table("products").insert({
                "name": context.user_data['description'][:30],
                "category": context.user_data['category'],
                "price_wholesale": context.user_data['price'],
                "image_url": context.user_data['photo_url']
            }).execute()
        except Exception as e:
            logging.error(f"Supabase Error: {e}")

        # 2. النشر في القناة
        client_buttons = [[InlineKeyboardButton("🛒 اطلب الآن", url=f"https://t.me/{ADMIN_USERNAME}")]]
        await context.bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=context.user_data['photo_id'],
            caption=context.user_data['final_caption'],
            reply_markup=InlineKeyboardMarkup(client_buttons),
            parse_mode="Markdown"
        )
        await query.edit_message_caption(caption="✅ تم النشر في القناة وتحديث الموقع!")
    
    else:
        await query.edit_message_caption(caption="❌ تم إلغاء العملية.")
    
    return ConversationHandler.END

def main():
    if not BOT_TOKEN: return
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
