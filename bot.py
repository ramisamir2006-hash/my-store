import telebot
from telebot import types
import json
from datetime import datetime

# --- إعدادات الربط (تأكد من صحة التوكن من BotFather) ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
ADMIN_ID = 7020070481             
CHANNEL_ID = -1003223634521       

# قائمة الموظفين (يتم إضافة ID الموظف هنا)
staff_list = [] 

bot = telebot.TeleBot(TOKEN)

# --- 1. لوحات التحكم (الكبسات) ---

def admin_keyboard():
    """لوحة تحكم المدير رامي"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📊 التقارير اليومية"),
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("👥 الموظفين (إضافة/حذف)"),
        types.KeyboardButton("➕ إضافة منتج جديد"),
        types.KeyboardButton("💰 ضبط الخصومات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    )
    return markup

def staff_keyboard():
    """لوحة تحكم الموظفين المسؤولين"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("💬 الاستفسارات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    )
    return markup

def user_keyboard():
    """لوحة تحكم الزبائن"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💍 المنتجات المتاحة"),
        types.KeyboardButton("📞 التواصل مع الدعم")
    )
    return markup

# --- 2. معالجة الأوامر والرسائل ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # التحقق من هوية المستخدم لإظهار اللوحة المناسبة
    if user_id == ADMIN_ID:
        bot.reply_to(message, "مرحباً بك يا مدير (رامي سمير) في لوحة تحكم @Ramysamir2026_bot", reply_markup=admin_keyboard())
    elif user_id in staff_list:
        bot.reply_to(message, "أهلاً بك (موظف مسؤول) في نظام الإدارة.", reply_markup=staff_keyboard())
    else:
        bot.reply_to(message, "مرحباً بك في بوت مجوهرات رامي سمير ✨", reply_markup=user_keyboard())

# مثال لمعالجة كبسة معينة
@bot.message_handler(func=lambda message: message.text == "📊 التقارير اليومية")
def reports(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "جاري تحضير التقارير لليوم...")
    else:
        bot.send_message(message.chat.id, "عذراً، لا تملك صلاحية الوصول للتقارير.")

# --- 3. تشغيل البوت ---
if __name__ == "__main__":
    print("✅ البوت يعمل الآن بدون أخطاء...")
    bot.infinity_polling()
    
