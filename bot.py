import telebot
from telebot import types

# --- الإعدادات النهائية المعتمدة ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- لوحات التحكم (Keyboards) ---

def admin_panel():
    """لوحة التحكم الشاملة للمدير"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "➕ إضافة منتج جديد", "📦 إدارة الطلبات",
        "💰 خصم الجملة", "🏷️ خصم التجزئة",
        "🎧 خدمة العملاء", "📊 التقارير",
        "🛍️ فتح المتجر", "👥 إدارة الموظفين"
    )
    return markup

def user_panel():
    """لوحة الزبائن العامة"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💍 تصفح المجوهرات", "📞 تواصل معنا")
    return markup

# --- معالجة الأوامر (Handlers) ---

@bot.message_handler(commands=['start', 'panel'])
def start_message(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛡️ أهلاً بك يا رامي. لوحة التحكم المركزية جاهزة:", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في متجر مجوهرات رامي سمير ✨", reply_markup=user_panel())

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text

    # استجابات لوحة المدير
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج جديد":
            bot.reply_to(message, "ارسل صورة المنتج مع الوصف والسعر للرفع.")
        elif text == "💰 خصم الجملة":
            bot.reply_to(message, "أدخل نسبة الخصم الجديدة لعملاء الجملة (%)")
        elif text == "📊 التقارير":
            bot.reply_to(message, "📈 جاري معالجة بيانات المبيعات...")
        elif text == "🎧 خدمة العملاء":
            bot.reply_to(message, "📩 تم فتح قسم استفسارات الزبائن.")

    # استجابات لوحة الزبائن
    if text == "💍 تصفح المجوهرات":
        bot.send_message(message.chat.id, "💎 جاري تحميل أحدث الموديلات...")
    elif text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, "للتواصل المباشر مع الإدارة: @Ramysamir2026")

# --- تشغيل البوت ---
if __name__ == "__main__":
    print("--- البوت @Stormarketing_bot يعمل الآن بنجاح ---")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
