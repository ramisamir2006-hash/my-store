import telebot
from telebot import types

# --- إعدادات البوت النهائية ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- لوحات التحكم (Keyboards) ---

def main_admin_keyboard():
    """لوحة تحكم المدير الشاملة - تظهر لك فقط"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "➕ إضافة منتج", "📦 إدارة الطلبات",
        "💰 خصم الجملة", "🏷️ خصم التجزئة",
        "👥 الموظفين", "📊 التقارير",
        "🎧 خدمة العملاء", "🛍️ تصفح المتجر كزبون"
    )
    return markup

def store_main_keyboard():
    """لوحة المتجر الرئيسية (مثل سلة ماريا) - تظهر للزبائن"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📱 تصفح المتجر 🛍️"),
        types.KeyboardButton("📢 قناتنا"),
        types.KeyboardButton("🛒 السلة"),
        types.KeyboardButton("📞 خدمة العملاء")
    )
    return markup

# --- معالجة الأوامر ---

@bot.message_handler(commands=['start', 'panel'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "🛡️ أهلاً بك يا رامي في لوحة تحكم Stormarketing المركزية.\nيمكنك إدارة المنتجات والخصومات من الأزرار أدناه.", 
            reply_markup=main_admin_keyboard()
        )
    else:
        # رسالة ترحيبية تشبه سلة ماريا
        welcome_msg = "أهلاً بك في متجرنا! 👋\n\nاستخدم القائمة بالأسفل للتصفح ومتابعة طلباتك 👇"
        bot.send_message(message.chat.id, welcome_msg, reply_markup=store_main_keyboard())

# --- معالجة ضغطات الأزرار ---

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    # --- أزرار الإدارة ---
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج":
            bot.reply_to(message, "ارسل صورة المنتج أولاً مع الوصف والسعر.")
        elif text == "💰 خصم الجملة":
            bot.reply_to(message, "أدخل نسبة الخصم الجديدة لطلبات الجملة.")
        elif text == "📊 التقارير":
            bot.reply_to(message, "📈 جاري سحب بيانات المبيعات الحالية...")
        elif text == "🛍️ تصفح المتجر كزبون":
            bot.send_message(message.chat.id, "عرض واجهة الزبون:", reply_markup=store_main_keyboard())

    # --- أزرار المتجر (للجميع) ---
    if text == "📱 تصفح المتجر 🛍️":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 اضغط هنا لفتح المتجر", web_app=types.WebAppInfo(url="https://your-website.com"))) # استبدله برابط موقعك
        bot.send_message(message.chat.id, "تفضل بزيارة متجرنا الإلكتروني السريع 👇", reply_markup=markup)

    elif text == "🛒 السلة":
        bot.send_message(message.chat.id, "🛒 سلتك فارغة حالياً.")

    elif text == "📞 خدمة العملاء":
        msg = "مركز التواصل والدعم الفني 📞\n\nنحن هنا لمساعدتك! ساعات العمل:\n⏰ يومياً من 11 صباحاً حتى 9 مساءً."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 تواصل معنا واتساب", url="https://wa.me/201277123567"))
        bot.send_message(message.chat.id, msg, reply_markup=markup)

    elif text == "📢 قناتنا":
        bot.send_message(message.chat.id, "تابعنا على قناتنا الرسمية لمشاهدة أحدث العروض 👇\nhttps://t.me/your_channel")

# --- التشغيل ---
if __name__ == "__main__":
    print("🚀 البوت يعمل الآن بتصميم المتجر الاحترافي...")
    bot.infinity_polling()
    
