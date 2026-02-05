import os, telebot, threading
from telebot import types
from flask import Flask

# --- الإعدادات الأساسية ---
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@RamySamir2026Gold"  # قناتك العامة للعملاء
STAFF_GROUP_ID = -1002376483563   # ID جروب الموظفين (تأكد من إضافة البوت فيه كأدمن)
STAFF_LINK = "https://t.me/+Zu6NKNYqTgVkZGFk"
ADMIN_ID = 5664157143 # ضع معرفك الشخصي هنا ليكون لك صلاحية فصل الموظفين

bot = telebot.TeleBot(TOKEN)
user_data = {}  # لتخزين بيانات المنتج مؤقتاً

@app.route('/')
def home(): return "Store Engine is Running and Healthy"

# --- نظام الصلاحيات ---
def is_staff(user_id):
    try:
        member = bot.get_chat_member(STAFF_GROUP_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

# --- لوحة التحكم (للمدير والموظفين) ---
def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if user_id == ADMIN_ID or is_staff(user_id):
        markup.add("➕ إضافة منتج جديد", "📊 التقارير")
    if user_id == ADMIN_ID:
        markup.add("👥 إدارة الموظفين")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 أهلاً بك في لوحة تحكم متجر ماريا.", 
                     reply_markup=main_keyboard(message.from_user.id))

# --- إدارة الموظفين (للمدير فقط) ---
@bot.message_handler(func=lambda m: m.text == "👥 إدارة الموظفين")
def manage_staff(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔗 رابط جروب التوظيف", url=STAFF_LINK))
        bot.send_message(message.chat.id, "👨‍💼 **إدارة الفريق:**\n\n1. لإضافة موظف: أرسل له الرابط للدخول.\n2. لفصل موظف: قم بطرده من الجروب وسيفقد صلاحياته فوراً.", 
                         reply_markup=markup, parse_mode="Markdown")

# --- نظام إضافة المنتج (سؤال تلو الآخر) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def add_product_start(message):
    if not (message.from_user.id == ADMIN_ID or is_staff(message.from_user
                                                         
