import telebot
from telebot import types

# --- إعدادات البوت النهائية ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# قائمة الموظفين (يمكنك إضافة IDs هنا)
staff_list = []

# --- 1. لوحات التحكم (Keyboards) ---

def admin_keyboard():
    """لوحة المدير العام"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "📊 التقارير اليومية", "📦 إدارة الطلبات",
        "👥 الموظفين", "➕ إضافة منتج جديد",
        "💰 ضبط الخصومات", "🛍️ فتح المتجر"
    )
    return markup

def staff_keyboard():
    """لوحة الموظفين"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("📦 إدارة الطلبات", "💬 الاستفسارات", "🛍️ فتح المتجر")
    return markup

def user_keyboard():
    """لوحة الزبائن"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💍 تصفح المجوهرات", "📞 تواصل معنا")
    return markup

# --- 2. الأوامر الأساسية ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً بك يا رامي في لوحة تحكم Stormarketing_bot 🛡️", reply_markup=admin_keyboard())
    elif user_id in staff_list:
        bot.send_message(message.chat.id, "أهلاً بك (موظف مسؤول).", reply_markup=staff_keyboard())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في مجوهرات رامي سمير ✨\nيسعدنا تصفحك لمنتجاتنا.", reply_markup=user_keyboard())

# --- 3. معالجة ضغطات الأزرار ---

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    if text == "📊 التقارير اليومية" and user_id == ADMIN_ID:
        bot.reply_to(message, "📈 جاري استخراج تقارير المبيعات لليوم...")
    
    elif text == "💍 تصفح المجوهرات":
        bot.send_message(message.chat.id, "💎 جاري تحميل الكتالوج... يمكنك قريباً رؤية القطع المتاحة.")

    elif text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, "يمكنك التواصل مباشرة مع الإدارة هنا: @Ramysamir2026")

    elif text == "🛍️ فتح المتجر":
        bot.reply_to(message, "✅ تم إرسال إشعار بفتح المتجر للزبائن.")

# --- 4. تشغيل البوت ---
if __name__ == "__main__":
    print("✅ البوت Stormarketing_bot يعمل الآن بدون أي أخطاء...")
    bot.infinity_polling()
    
