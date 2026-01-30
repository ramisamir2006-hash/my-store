import telebot
from telebot import types

# --- إعدادات البوت الرسمية المحدثة ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# قائمة الموظفين (يمكن إضافة IDs الموظفين هنا لاحقاً)
staff_list = []

# --- 1. بناء لوحات التحكم (Keyboards) ---

def admin_keyboard():
    """لوحة المدير العام - رامي"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "📊 التقارير اليومية", "📦 إدارة الطلبات",
        "👥 الموظفين", "➕ إضافة منتج جديد",
        "💰 الخصومات", "🛍️ فتح المتجر"
    )
    return markup

def user_keyboard():
    """لوحة الزبائن"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💍 تصفح المجوهرات", "📞 تواصل معنا")
    return markup

# --- 2. الأوامر واستجابة الأزرار ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "أهلاً بك يا رامي! تم تفعيل لوحة الإدارة الكاملة لـ @Stormarketing_bot ✨", 
            reply_markup=admin_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك في مجوهرات رامي سمير ✨\nيسعدنا تصفحك لمنتجاتنا عبر الأزرار أدناه.", 
            reply_markup=user_keyboard()
        )

@bot.message_handler(func=lambda message: True)
def handle_interaction(message):
    user_id = message.from_user.id
    text = message.text

    # استجابة للمدير (رامي)
    if user_id == ADMIN_ID:
        if text == "📊 التقارير اليومية":
            bot.reply_to(message, "📈 جاري سحب بيانات التقارير والطلبات لليوم...")
        elif text == "🛍️ فتح المتجر":
            bot.reply_to(message, "✅ تم تحديث حالة المتجر إلى (مفتوح).")

    # استجابة للزبائن
    if text == "💍 تصفح المجوهرات":
        bot.send_message(message.chat.id, "💎 الكتالوج الجديد سيتم عرضه هنا قريباً.")
    elif text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, "يمكنك التواصل المباشر مع الإدارة هنا: @Ramysamir2026")

# --- 3. تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 البوت @Stormarketing_bot متصل الآن بنجاح...")
    bot.infinity_polling()
    
