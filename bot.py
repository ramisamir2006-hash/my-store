import os, telebot, threading
from telebot import types
from flask import Flask

# --- إعدادات المنصة المخصصة لـ @Stormarketing_bot ---
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@RamySamir2026Gold"  # قناتك العامة
STAFF_GROUP_ID = -1002376483563   # جروب الموظفين
STAFF_LINK = "https://t.me/+Zu6NKNYqTgVkZGFk"

# المسؤول الأول (أنت)
ADMIN_ID = 7020070481 

bot = telebot.TeleBot(TOKEN)
user_data = {}  # مخزن مؤقت للبيانات

@app.route('/')
def home(): return "Stormarketing Bot is Active"

# --- دالة التحقق من الصلاحيات ---
def is_authorized(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(STAFF_GROUP_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

# --- 1. واجهة صفحة البوت الرئيسية (زراير التحكم) ---
def main_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج جديد", "📊 تقارير المبيعات")
    markup.add("📁 إدارة الأقسام", "👥 فريق العمل (الموظفين)")
    markup.add("🖼️ تغيير غلاف المتجر", "⚙️ الإعدادات العامة")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    # شكل ترحيبي احترافي في صفحة البوت
    welcome_msg = (
        f"🤖 **مرحباً بك في لوحة تحكم Stormarketing_bot**\n\n"
        f"🆔 **ID:** `{message.from_user.id}`\n"
        f"🔗 **Username:** @Stormarketing_bot\n"
        f"🏳️ **Lang:** AR 🇪🇬\n"
        f"---------------------------\n"
        f"استخدم الأزرار أدناه لإدارة متجرك ونشر المنتجات."
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=main_admin_keyboard(), parse_mode="Markdown")

# --- 2. نظام إضافة المنتج (سؤال تلو الآخر) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def start_add(message):
    if not is_authorized(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ عذراً، هذا القسم مخصص للإدارة فقط.")
    
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 **الخطوة 1:** أرسل صورة المنتج (Photo):")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message
