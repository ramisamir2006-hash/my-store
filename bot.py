import os
import telebot
from telebot import types
from supabase import create_client
from flask import Flask
from threading import Thread
from datetime import datetime

# إعدادات السيرفر والبوت
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# مخزن مؤقت لبيانات (المدير والعملاء)
user_states = {}

@app.route('/')
def home(): return "Order System is Online!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- 1. جزء المدير: النشر في القناة بالأزرار ---
@bot.callback_query_handler(func=lambda call: call.data == "publish_now")
def publish_to_channel(call):
    data = user_states.get(call.message.chat.id)
    if data:
        markup = types.InlineKeyboardMarkup()
        # زر "إضافة للسلة" يوجه العميل للبوت مع معرف المنتج
        add_cart_url = f"https://t.me/{bot.get_me().username}?start=order_{data['name'].replace(' ', '_')}"
        markup.add(types.InlineKeyboardButton("🛒 إضافة للسلة", url=add_cart_url))
        markup.add(types.InlineKeyboardButton("🏪 فتح المتجر", url="https://ramisamir2006-hash.github.io"))
        
        caption = f"✨ **{data['name']}**\n💰 السعر: {data['retail']} ج.م\n\n{data['desc']}"
        bot.send_photo(CHANNEL_ID, data['photo'], caption=caption, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(call.message.chat.id, "✅ تم النشر في القناة بنجاح!")

# --- 2. جزء العميل: استقبال الطلب من القناة ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("order_"):
        product_name = args[1].replace("order_", "").replace("_", " ")
        user_states[message.chat.id] = {'order_product': product_name, 'step': 'QUANTITY'}
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("1", "2", "3", "4", "5")
        bot.send_message(message.chat.id, f"🛍️ لقد اخترت: {product_name}\nكم عدد القطع المطلوبة؟", reply_markup=markup)
    else:
        # لوحة تحكم المدير العادية (إذا كان الشخص هو المدير)
        start_admin_panel(message)

# --- 3. خطوات تسجيل بيانات العميل ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'QUANTITY')
def get_quantity(message):
    user_states[message.chat.id]['quantity'] = message.text
    user_states[message.chat.id]['step'] = 'DELIVERY_TYPE'
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚚 توصيل منزلي (دليفري)", "
# دالة إنشاء لوحة أزرار العميل (التي تظهر في الصورة)
def get_client_buttons(product_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # ربط زر "إضافة للسلة" بالبوت مباشرة لإتمام عملية الشراء
    # ملاحظة: استبدل YOUR_BOT_USERNAME باسم يوزر البوت الخاص بك
    btn_add_cart = types.InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/Stormmarketing_bot?start=order_{product_name}")
    
    # زر فتح المتجر الإلكتروني
    btn_store = types.InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url="https://ramisamir2006-hash.github.io")
    
    # زر التواصل المباشر للاستفسار
    btn_help = types.InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/RamySamir2026")
    
    # زر عرض السلة الخاصة بالعميل داخل البوت
    btn_view_cart = types.InlineKeyboardButton("📜 عرض السلة", url="https://t.me/Stormmarketing_bot?start=view_cart")

    markup.add(btn_add_cart)
    markup.add(btn_help, btn_store)
    markup.add(btn_view_cart)
    return markup
