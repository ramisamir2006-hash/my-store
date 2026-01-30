import telebot
from telebot import types

# --- الإعدادات الجديدة ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

# قائمة الموظفين المصرح لهم (أضف الـ IDs هنا)
staff_list = [] 

bot = telebot.TeleBot(TOKEN)

# --- 1. بناء لوحات التحكم (Keyboards) ---

def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📊 التقارير اليومية"),
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("👥 الموظفين"),
        types.KeyboardButton("➕ إضافة منتج"),
        types.KeyboardButton("💰 الخصومات"),
        types.KeyboardButton("🛍️ حالة المتجر")
    )
    return markup

def get_staff_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("💬 الاستفسارات"),
        types.KeyboardButton("🛍️ حالة المتجر")
    )
    return markup

def get_user_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💍 المنتجات المتاحة"),
        types.KeyboardButton("📞 تواصل معنا")
    )
    return markup

# --- 2. معالجة الأوامر (Handlers) ---

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "مرحباً يا رامي! تم تفعيل لوحة الإدارة الكاملة لبوت @Ramysamir2026_bot ✨", 
            reply_markup=get_admin_keyboard()
        )
    elif user_id in staff_list:
        bot.send_message(
            message.chat.id, 
            "أهلاً بك (موظف مسؤول).", 
            reply_markup=get_staff_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك في بوت مجوهرات رامي سمير الرسمي ✨\nيسعدنا خدمتك.", 
            reply_markup=get_user_keyboard()
        )

# --- 3. معالجة النصوص والرد على الأزرار ---

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text

    # ردود فعل لأوامر المدير فقط
    if user_id == ADMIN_ID:
        if text == "📊 التقارير اليومية":
            bot.reply_to(message, "📈 جاري سحب بيانات التقارير من قاعدة البيانات...")
        elif text == "👥 الموظفين":
            bot.reply_to(message, "👥 قائمة الموظفين الحالية فارغة. يمكنك إضافة موظف جديد عبر البرمجة.")
    
    # ردود فعل عامة للجميع
    if text == "💍 المنتجات المتاحة":
        bot.send_message(message.chat.id, "💎 قريباً سيتم عرض كتالوج المجوهرات هنا.")
    elif text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, "للتواصل المباشر مع الإدارة: @Ramysamir2026")

# --- 4. تشغيل البوت ---
if __name__ == "__main__":
    print("--- البوت يعمل الآن بالتوكن الجديد ---")
    bot.infinity_polling()
    
