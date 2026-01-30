import telebot
from telebot import types

# --- إعدادات الربط النهائية (المحدثة) ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير (المدير)
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- 1. لوحات التحكم (Keyboards) ---

def admin_keyboard():
    """لوحة التحكم الكاملة للمدير - تظهر لكافة أنحاء المتجر"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "➕ إضافة منتج جديد", "📦 إدارة الطلبات",
        "💰 خصم الجملة", "🏷️ خصم التجزئة",
        "👥 إدارة الموظفين", "📊 التقارير",
        "🎧 خدمة العملاء", "🛍️ عرض واجهة الزبون"
    )
    return markup

def user_store_keyboard():
    """واجهة المتجر للزبائن (تصميم سلة ماريا)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📱 تصفح المتجر 🛍️"),
        types.KeyboardButton("📢 قناتنا"),
        types.KeyboardButton("🛒 السلة"),
        types.KeyboardButton("📞 خدمة العملاء")
    )
    return markup

# --- 2. معالجة الأوامر والرسائل ---

@bot.message_handler(commands=['start', 'panel'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "🛡️ أهلاً بك يا رامي! تم تفعيل لوحة التحكم المركزية لمتجرك.", 
            reply_markup=admin_keyboard()
        )
    else:
        # نص ترحيبي مطابق لصور "سلة ماريا"
        welcome_text = "أهلاً بك في متجرنا! 👋\n\nاستخدم القائمة بالأسفل للتصفح ومتابعة طلباتك 👇"
        bot.send_message(message.chat.id, welcome_text, reply_markup=user_store_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_interactions(message):
    user_id = message.from_user.id
    text = message.text

    # --- منطق المدير (أزرار التحكم) ---
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج جديد":
            bot.reply_to(message, "📸 يرجى إرسال صورة المنتج مع السعر والوصف.")
        elif text == "💰 خصم الجملة":
            bot.reply_to(message, "أدخل نسبة الخصم الجديدة لعملاء الجملة (%)")
        elif text == "🏷️ خصم التجزئة":
            bot.reply_to(message, "أدخل نسبة الخصم الجديدة لعملاء التجزئة (%)")
        elif text == "🛍️ عرض واجهة الزبون":
            bot.send_message(message.chat.id, "هكذا يظهر المتجر للجمهور:", reply_markup=user_store_keyboard())

    # --- منطق الزبائن (واجهة المتجر) ---
    if text == "📱 تصفح المتجر 🛍️":
        markup = types.InlineKeyboardMarkup()
        # زر يفتح المتجر كصفحة داخلية (WebApp) كما في الصور
        markup.add(types.InlineKeyboardButton("🛍️ اضغط هنا لفتح المتجر", web_app=types.WebAppInfo(url="https://yourstore.com")))
        bot.send_message(message.chat.id, "تفضل بزيارة متجرنا الإلكتروني السريع 👇", reply_markup=markup)

    elif text == "📞 خدمة العملاء":
        support_msg = "مركز التواصل والدعم الفني 📞\n\nنحن هنا لمساعدتك! ساعات العمل:\n⏰ يومياً من 11 صباحاً حتى 9 مساءً."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 تواصل معنا واتساب", url="https://wa.me/201277123567"))
        bot.send_message(message.chat.id, support_msg, reply_markup=markup)

    elif text == "🛒 السلة":
        bot.send_message(message.chat.id, "🛒 سلتك فارغة حالياً.")

# --- 3. تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 البوت @Stormarketing_bot يعمل الآن بتصميم المتجر الاحترافي...")
    bot.infinity_polling()
    
