import telebot
from telebot import types

# --- إعدادات البوت النهائية ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير (المدير)
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# قائمة الموظفين (يمكنك إضافة IDs الموظفين هنا لاحقاً)
staff_list = []

# --- 1. بناء لوحات التحكم (Keyboards) ---

def admin_keyboard():
    """لوحة التحكم الكاملة للمدير"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "📊 التقارير اليومية", "📦 إدارة الطلبات",
        "👥 الموظفين", "➕ إضافة منتج جديد",
        "💰 ضبط الخصومات", "🛍️ فتح المتجر"
    )
    return markup

def user_keyboard():
    """لوحة تحكم الزبائن"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("💍 تصفح المجوهرات", "📞 تواصل معنا")
    return markup

# --- 2. الأوامر والردود ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "أهلاً بك يا رامي! أنت الآن في لوحة التحكم المركزية لبوت @Stormarketing_bot 🛡️", 
            reply_markup=admin_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك في متجر مجوهرات رامي سمير ✨\nيسعدنا خدمتك عبر الأزرار أدناه:", 
            reply_markup=user_keyboard()
        )

@bot.message_handler(func=lambda message: True)
def handle_interaction(message):
    user_id = message.from_user.id
    text = message.text

    # منطق المدير
    if user_id == ADMIN_ID:
        if text == "📊 التقارير اليومية":
            bot.reply_to(message, "📈 جاري سحب تقارير المبيعات وتحليل البيانات...")
        elif text == "👥 الموظفين":
            bot.reply_to(message, "👥 قائمة الموظفين الحالية فارغة. يمكنك إضافة مساعدين من الكود.")
    
    # منطق الزبائن
    if text == "💍 تصفح المجوهرات":
        bot.send_message(message.chat.id, "💎 الكتالوج يتم تحديثه حالياً، ترقبوا أجمل القطع قريباً.")
    elif text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, "للتواصل المباشر مع رامي سمير: @Ramysamir2026")

# --- 3. تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 البوت @Stormarketing_bot متصل الآن ويعمل كمسؤول...")
    bot.infinity_polling()
    
