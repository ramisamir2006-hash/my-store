import json
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات الأساسية ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
ADMIN_ID = 7020070481  # هويتك كمدير (رامي سمير)
WEB_APP_URL = "https://ramisamir2006-hash.github.io/my-store/"

# إعداد السجلات (Logs) لمراقبة الأخطاء على Koyeb
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة الترحيب والأزرار الرئيسية عند تشغيل البوت"""
    user_name = update.effective_user.first_name
    
    # أزرار القائمة السفلية (مثل التي ظهرت في صورك)
    keyboard = [
        [KeyboardButton("🛍️ تصفح المتجر الآن", web_app=WebAppInfo(url=WEB_APP_URL))],
        ["📦 طلباتي", "💬 خدمة العملاء"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"أهلاً بك يا {user_name} في متجر رامي سمير! 👋\n\n"
        "أنا مساعدك الذكي للمتجر 🤖، يمكنك تصفح المنتجات وطلبها مباشرة من خلال الزر بالأسفل 👇",
        reply_markup=reply_markup
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """استلام بيانات الطلب من المتجر وإرسالها للمدير"""
    # استخراج البيانات القادمة من الواجهة (JavaScript)
    data = json.loads(update.effective_message.web_app_data.data)
    user = update.effective_user
    
    # تفاصيل الطلب لتظهر بشكل منظم
    items_details = "\n".join([f"- {item['name']}: {item['price']} ج.م" for item in data['items']])
    total_price = data['total']

    # 1. إرسال تأكيد للعميل
    await update.message.reply_text(
        f"✅ تم استلام طلبك بنجاح يا {user.first_name}!\n\n"
        f"تفاصيل الطلب:\n{items_details}\n\n"
        f"💰 الإجمالي: {total_price} ج.م\n"
        "سنتواصل معك قريباً لتأكيد الشحن."
    )

    # 2. إرسال تنبيه فوري للمدير (رامي سمير) ببيانات العميل
    admin_message = (
        f"🚨 **طلب جديد من المتجر!**\n\n"
        f"👤 العميل: {user.first_name} (@{user.username})\n"
        f"🆔 معرف العميل: {user.id}\n\n"
        f"📦 المنتجات:\n{items_details}\n\n"
        f"💵 المبلغ الإجمالي: {total_price} ج.م"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات الدعم الفني كما في صورك"""
    help_text = (
        "📍 **مركز التواصل والدعم الفني**\n\n"
        "نحن هنا لمساعدتك! يمكنك التواصل معنا عبر:\n"
        "📞 هاتف: 201277123567\n"
        "⏰ ساعات العمل: من 11 صباحاً حتى 9 مساءً"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    """تشغيل البوت"""
    app = Application.builder().token(TOKEN).build()

    #Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("💬 خدمة العملاء"), help_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    print("✅ البوت يعمل الآن ومتصل بالمتجر...")
    app.run_polling()

if __name__ == "__main__":
    main()
