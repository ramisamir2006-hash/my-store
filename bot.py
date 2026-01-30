import telebot
from telebot import types
import json

# --- الإعدادات النهائية المدمجة ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
CHANNEL_ID = -1003223634521       # القناة الجديدة
ADMIN_ID = 7020070481             # رامي سمير

staff_list = [] 
bot = telebot.TeleBot(TOKEN)

# --- لوحات التحكم ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        types.KeyboardButton("📊 التقارير اليومية"),
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("👥 الموظفين (إضافة/حذف)"),
        types.KeyboardButton("➕ إضافة منتج جديد"),
        types.KeyboardButton("💰 ضبط الخصومات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    ]
    markup.add(*btns)
    return markup

def user_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("🛍️ دخول المتجر"), types.KeyboardButton("📞 الدعم الفني"))
    return markup

# --- الأوامر الأساسية ---
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً يا رامي! لوحة الإدارة جاهزة.", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في مجوهرات رامي سمير ✨", reply_markup=user_keyboard())

# --- معالجة البيانات والنشر بالقناة ---
@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        data = json.loads(message.web_app_data.data)
        if data.get("action") == "publish":
            bot.send_message(CHANNEL_ID, f"✨ {data['name']}\n💰 {data['price']} ج.م")
            bot.reply_to(message, "✅ تم النشر في القناة.")
    except:
        bot.reply_to(message, "❌ حدث خطأ في معالجة البيانات.")

# --- بدء التشغيل ---
print("✅ البوت يعمل بنجاح...")
bot.polling(none_stop=True)
