import json
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# الإعدادات الخاصة بك
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
ADMIN_ID = 7020070481 
# الرابط الذي حصلت عليه
MY_STORE_URL = "https://ramisamir2006-hash.github.io/my-store/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ظهور الأزرار الرئيسية أسفل الشاشة كما في صورة سلة ماريا"""
    keyboard = [
        [KeyboardButton("📱 تصفح المتجر", web_app=WebAppInfo(url=MY_STORE_URL))],
        [KeyboardButton("🛒 السلة"), KeyboardButton("💬 خدمة العملاء")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "أهلاً بك في متجر رامي سمير! 👋\nاستخدم القائمة بالأسفل للتسوق ومتابعة طلباتك 👇",
        reply_markup=reply_markup
    )

async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الرد على أمر /store بإرسال زر المتجر داخل الرسالة"""
    keyboard = [[InlineKeyboardButton("🛍️ فتح المتجر (المعرض)", web_app=WebAppInfo(url=MY_STORE_URL))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("تفضل بزيارة متجرنا الإلكتروني السريع 👇", reply_markup=reply_markup)

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استلام الطلب من المتجر وإرساله لك كمدير"""
    data = json.loads(update.effective_message.web_app_data.data)
    user = update.effective_user
    
    # رسالة للمدير
    order_msg = f"🚨 طلب جديد من: {user.first_name}\n💰 الإجمالي: {data['total']} ج.م\n📦 المنتجات: {data['items']}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=order_msg)
    
    # رسالة للعميل
    await update.message.reply_text("✅ تم استلام طلبك بنجاح! سنتواصل معك قريباً.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("store", store_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_order))
    
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
