import telebot
from telebot import types

# --- إعدادات الربط ---
# التوكن الخاص ببوت Stormarketing_bot
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
# معرف رامي سمير (المدير)
ADMIN_ID = 7020070481             
CHANNEL_ID = -1003223634521       

bot = telebot.TeleBot(TOKEN)

# قائمة الموظفين (معرفاتهم الرقمية)
staff_list = [] 

# --- 1. دوال لوحات التحكم ---

def admin_keyboard():
    """لوحة تحكم المدير رامي"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📊 التقارير اليومية"),
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("👥 الموظفين"),
        types.KeyboardButton("➕ إضافة منتج جديد"),
        types.KeyboardButton("💰 ضبط الخصومات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    )
    return markup

def user_keyboard():
    """لوحة تحكم الزبائن"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💍 تصفح المجوهرات"),
        types.KeyboardButton("📞 تواصل معنا")
    )
    return markup

# --- 2. معالجة الأوامر والرسائل ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك يا رامي سمير في نظام إدارة Stormarketing_bot 🛡️", 
            reply_markup=admin_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك في مجوهرات رامي سمير ✨\nيسعدنا خدمتك.", 
            reply_markup=user_keyboard()
        )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text

    # استجابة لأزرار المدير
    if user_id == ADMIN_ID:
        if text == "📊 التقارير اليومية":
            bot.reply_to(message, "📈 جاري سحب البيانات... الرجاء الانتظار.")
        elif text == "👥 الموظفين":
            bot.reply_to(message, "👥 لا يوجد موظفون مضافون حالياً.")

    # استجابة لأزرار الزبائن
    if text == "💍 تصفح المجوهرات":
        bot.send_message(message.chat.id, "💎 الكتالوج الجديد سيتم رفعه قريباً.")
    elif text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, "يمكنك مراسلة رامي سمير مباشرة: @Ramysamir2026")

# --- 3. تشغيل البوت ---
if __name__ == "__main__":
    print("--- البوت @Stormarketing_bot يعمل الآن ---")
    bot.infinity_polling()
    
