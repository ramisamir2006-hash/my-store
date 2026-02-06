import os, telebot, threading, sqlite3
from telebot import types
from flask import Flask

# --- إعدادات الربط النهائية ---
app = Flask(__name__)
TOKEN = "8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk" # التوكن الجديد
CHANNEL_ID = "@RamySamir2026Gold" # قناة النشر العامة
STAFF_GROUP_ID = -1002376483563 # جروب استلام طلبات العملاء
ADMIN_ID = 7020070481 # معرف المدير (رامي)

bot = telebot.TeleBot(TOKEN)
user_data = {} 

# --- 1. نظام قاعدة البيانات (تعمل 24 ساعة) ---
def init_db():
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, photo TEXT, sizes TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. ربط واجهة الموقع (index.html) ---
@app.route('/')
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "System is Online - index.html not found"

# --- 3. لوحة تحكم المدير (الأزرار الرئيسية) ---
def main_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج جديد", "📊 تقارير المبيعات")
    markup.add("👥 فريق العمل", "⚙️ الإعدادات")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "👋 **أهلاً بك يا مدير رامي**\nالداتابيز نشطة ونظام النشر جاهز.", 
                         reply_markup=main_admin_keyboard(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🏪 مرحباً بك في متجرنا. تابع القناة لمشاهدة المنتجات.")

# --- 4. عملية إضافة منتج والنشر في القناة ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def start_add(message):
    if message.from_user.id != ADMIN_ID: return
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 **1. أرسل صورة المنتج:**")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ خطأ! أرسل صورة.")
        return bot.register_next_step_handler(message, get_photo)
    user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✏️ **2. أرسل اسم المنتج ووصفه:**")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "💰 **3. أرسل السعر (بالجنيه):**")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_data[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📏 **4. أرسل المقاسات (افصل بينها بفاصلة ,):**")
    bot.register_next_step_handler(message, get_sizes)

def get_sizes(message):
    user_data[message.chat.id]['sizes'] = message.text
    data = user_data[message.chat.id]
    
    # معاينة قبل النشر
    preview = f"📦 المنتج: {data['name']}\n💰 السعر: {data['price']} ج.م\n📏 المقاسات: {data['sizes']}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تأكيد ونشر في القناة", callback_data="publish_now"))
    bot.send_photo(message.chat.id, data['photo'], caption=f"🔍 **معاينة:**\n{preview}", reply_markup=markup, parse_mode="Markdown")

# --- 5. معالجة النشر واستلام طلبات العملاء ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "publish_now":
        data = user_data.get(call.message.chat.id)
        if data:
            # إنشاء أزرار المقاسات للقناة
            markup = types.InlineKeyboardMarkup(row_width=2)
            for s in data['sizes'].split(','):
                markup.add(types.InlineKeyboardButton(f"🛒 طلب مقاس {s.strip()}", callback_data=f"order_{s.strip()}_{data['name']}"))
            
            caption = f"✨ **{data['name']}**\n💰 السعر: {data['price']} ج.م\n\nاطلبي الآن عبر الضغط على المقاس 👇"
            bot.send_
    
