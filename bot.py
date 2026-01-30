import telebot
from telebot import types

# --- إعدادات البوت الرسمية ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- 1. بناء لوحات التحكم الشاملة ---

def super_admin_keyboard():
    """لوحة التحكم الشاملة للمدير - كافة الأزرار"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("➕ إضافة منتج جديد"),
        types.KeyboardButton("📦 إدارة الطلبات الحالية"),
        types.KeyboardButton("💰 خصومات الجملة"),
        types.KeyboardButton("🏷️ خصومات التجزئة"),
        types.KeyboardButton("🎧 خدمة العملاء (الدعم)"),
        types.KeyboardButton("👥 إدارة الموظفين"),
        types.KeyboardButton("📊 التقارير والمبيعات"),
        types.KeyboardButton("🛍️ حالة المتجر (فتح/إغلاق)")
    )
    return markup

def user_store_keyboard():
    """لوحة تحكم الزبائن (واجهة المتجر)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💍 عرض منتجات الجملة"),
        types.KeyboardButton("✨ عرض منتجات التجزئة"),
        types.KeyboardButton("📞 خدمة العملاء"),
        types.KeyboardButton("📜 طلباتي")
    )
    return markup

# --- 2. معالجة الأوامر ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "🛡️ أهلاً بك يا مدير (رامي). تم تفعيل كافة أزرار التحكم في المتجر الإلكتروني.", 
            reply_markup=super_admin_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك في متجر مجوهرات رامي سمير ✨\nتفضل باختيار القسم المناسب لك:", 
            reply_markup=user_store_keyboard()
        )

# --- 3. معالجة ضغطات الأزرار (أمثلة) ---

@bot.message_handler(func=lambda message: True)
def handle_all_buttons(message):
    user_id = message.from_user.id
    text = message.text

    # قسم الإدارة
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج جديد":
            bot.reply_to(message, "يرجى إرسال صورة المنتج مع الوصف والسعر.")
        elif text == "💰 خصومات الجملة":
            bot.reply_to(message, "أدخل نسبة الخصم الجديدة لعملاء الجملة (%)")
        elif text == "🏷️ خصومات التجزئة":
            bot.reply_to(message, "أدخل نسبة الخصم الجديدة لعملاء التجزئة (%)")
        elif text == "🎧 خدمة العملاء (الدعم)":
            bot.reply_to(message, "📩 تم تحويلك لقسم الاستفسارات الواردة من الزبائن.")

    # قسم الزبائن
    if text == "📞 خدمة العملاء":
        bot.send_message(message.chat.id, "لأي استفسار، تواصل مع المدير مباشرة: @Ramysamir2026")
    elif "عرض منتجات" in text:
        bot.send_message(message.chat.id, "💎 جاري تحميل الكتالوج... يرجى الانتظار.")

# --- 4. التشغيل ---
if __name__ == "__main__":
    print("🚀 البوت @Stormarketing_bot يعمل بكامل طاقته الآن...")
    bot.infinity_polling()
    
