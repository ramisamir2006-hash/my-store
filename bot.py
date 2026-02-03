import os
import telebot
from telebot import types
from supabase import create_client
from flask import Flask
from threading import Thread

# إعدادات السيرفر والبوت
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# مخزن مؤقت (تم تحسينه ليعمل بشكل أدق)
user_states = {}

@app.route('/')
def home(): return "Admin Panel is Active!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- لوحة التحكم الشاملة ---
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج", "📁 إضافة قسم")
    markup.add("📊 تقارير اليوم", "📦 متابعة الطلبات")
    markup.add("📢 حملة إعلانية", "⚙️ إعدادات")
    bot.send_message(message.chat.id, "💎 لوحة تحكم مدير my-store المحدثة\nاختر المهمة المطلوبة:", reply_markup=markup)

# --- نظام إضافة المنتج خطوة بخطوة ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج")
def add_product_step1(message):
    user_states[message.chat.id] = {'step': 'PHOTO'}
    bot.send_message(message.chat.id, "📸 الخطوة 1: أرسل صورة المنتج الآن:")

@bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'PHOTO')
def add_product_step2(message):
    user_states[message.chat.id]['photo'] = message.photo[-1].file_id
    user_states[message.chat.id]['step'] = 'CATEGORY'
    bot.send_message(message.chat.id, "📁 الخطوة 2: ما هو قسم المنتج؟ (أرسل الاسم فقط)")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'CATEGORY')
def add_product_step3(message):
    user_states[message.chat.id]['category'] = message.text
    user_states[message.chat.id]['step'] = 'NAME'
    bot.send_message(message.chat.id, "✏️ الخطوة 3: أرسل اسم المنتج:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'NAME')
def add_product_step4(message):
    user_states[message.chat.id]['name'] = message.text
    user_states[message.chat.id]['step'] = 'WHOLESALE'
    bot.send_message(message.chat.id, "💰 الخطوة 4: سعر الجملة؟")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'WHOLESALE')
def add_product_step5(message):
    user_states[message.chat.id]['wholesale'] = message.text
    user_states[message.chat.id]['step'] = 'RETAIL'
    bot.send_message(message.chat.id, "💵 الخطوة 5: سعر القطاعي؟")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'RETAIL')
def finalize_product(message):
    user_states[message.chat.id]['retail'] = message.text
    data = user_states[message.chat.id]
    
    # مراجعة البيانات
    review_msg = (
        f"🔍 **مراجعة المنتج النهائي:**\n\n"
        f"🏷️ الاسم: {data['name']}\n"
        f"📁 القسم: {data['category']}\n"
        f"💰 الجملة: {data['wholesale']} ج.م\n"
        f"💵 القطاعي: {data['retail']} ج.م\n\n"
        "✨ الوصف: قطعة فريدة مصممة بأعلى جودة."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 نشر في القناة", callback_data="pub_now"))
    markup.add(types.InlineKeyboardButton("⚙️ تعديل الكل", callback_data="restart_add"))
    
    bot.send_photo(message.chat.id, data['photo'], caption=review_msg, reply_markup=markup, parse_mode="Markdown")
    user_states[message.chat.id]['step'] = 'REVIEW'

# --- تنفيذ الأوامر (نشر / تحديث) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "pub_now":
        data = user_states.get(call.message.chat.id)
        if data:
            caption = f"✨ **{data['name']}**\n💰 جملة: {data['wholesale']}\n💵 قطاعي: {data['retail']}\n📍 اطلب هنا: https://ramisamir2006-hash.github.io"
            bot.send_photo(CHANNEL_ID, data['photo'], caption=caption)
            bot.answer_callback_query(call.id, "✅ تم النشر بنجاح!")
            del user_states[call.message.chat.id]
    elif call.data == "restart_add":
        add_product_step1(call.message)

# تشغيل البوت
if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
    
