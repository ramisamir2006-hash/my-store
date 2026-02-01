import os
import telebot
from supabase import create_client
from telebot import types # مهم جداً

# إعدادات الربط
TOKEN = os.getenv("BOT_TOKEN")
URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
KEY = os.getenv("SUPABASE_KEY")

bot = telebot.TeleBot(TOKEN)
db = create_client(URL, KEY)

# --- كود الأزرار المضمون ---
@bot.message_handler(commands=['start', 'restart', 'help'])
def control_panel(message):
    # مسح أي أزرار قديمة وإضافة الجديدة
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    
    markup.row(types.KeyboardButton("🛍️ إضافة منتج"), types.KeyboardButton("📊 التقارير"))
    markup.row(types.KeyboardButton("📁 إضافة قسم"), types.KeyboardButton("💡 كلمات تسويقية"))
    markup.row(types.KeyboardButton("🚀 حملة إعلانية"))
    
    bot.send_message(
        message.chat.id, 
        "✅ تم تفعيل لوحة تحكم my-store\nاختر من الأزرار بالأسفل للبدء:", 
        reply_markup=markup
    )

# بقية الكود الخاص بمعالجة الرسائل (handle_all) يوضع هنا...
