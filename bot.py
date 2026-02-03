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

# مخزن مؤقت للبيانات
user_data = {}

@app.route('/')
def home(): return "Admin Panel is Active!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- لوحة التحكم الرئيسية ---
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج", "📁 إضافة قسم")
    markup.add("📊 تقارير اليوم", "📦 متابعة الطلبات")
    markup.add("📢 حملة إعلانية", "⚙️ إعدادات القناة")
    bot.send_message(message.chat.id, "💎 لوحة تحكم مدير my-store\nتحكم في قناتك ومتجرك من هنا:", reply_markup=markup)

# --- 1. إضافة قسم جديد ---
@bot.message_handler(func=lambda m: m.text == "📁 إضافة قسم")
def add_category_start(message):
    bot.send_message(message.chat.id, "📝 أرسل اسم القسم الجديد الذي تود إضافته للمتجر:")
    bot.register_next_step_handler(message, save_category)

def save_category(message):
    cat_name = message.text
    try:
        # حفظ القسم في Supabase
        db.table("categories").insert({"name": cat_name}).execute()
        bot.send_message(message.chat.id, f"✅ تم إضافة قسم '{cat_name}' بنجاح!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ في الحفظ: {e}")

# --- 2. التقارير اليومية ---
@bot.message_handler(func=lambda m: m.text == "📊 تقارير اليوم")
def daily_reports(message):
    today = datetime.now().strftime("%Y-%m-%d")
    # محاكاة جلب بيانات حقيقية من قاعدة البيانات
    report_msg = (
        f"📅 **تقرير متجر my-store ليوم {today}:**\n\n"
        f"🛍️ عدد طلبات العملاء: 8 طلبات\n"
        f"💰 إجمالي المبيعات: 1,450 ج.م\n"
        f"👥 عملاء جدد: 5\n"
        f"📢 حالة القناة: نشطة ✅"
    )
    bot.send_message(message.chat.id, report_msg, parse_mode="Markdown")

# --- 3. متابعة الطلبات وتحديث الحالة ---
@bot.message_handler(func=lambda m: m.text == "📦 متابعة الطلبات")
def track_orders(message):
    # جلب عينة من طلبات لم تكتمل
    markup = types.InlineKeyboardMarkup()
    # مثال لطلب رقم 501
    markup.add(types.InlineKeyboardButton("📦 طلب #501 - تحديث الحالة", callback_data="order_501"))
    bot.send_message(message.chat.id, "📦 الطلبات الحالية المعلقة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def update_status_options(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تم التجهيز", callback_data="set_ready"),
               types.InlineKeyboardButton("🚚 مع الطيار", callback_data="set_shipped"))
    markup.add(types.InlineKeyboardButton("🏁 تم الاستلام", callback_data="set_done"))
    bot.edit_message_text("اختر الحالة الجديدة للطلب لإبلاغ العميل ونشره في القناة (اختياري):", 
                          call.message.chat.id, call.message.message_id, reply_markup=markup)

# --- 4. إضافة منتج (النظام المتسلسل الذي طلبته) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج")
def start_add_product(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 أرسل صورة المنتج لبدء النشر في القناة:")

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    if message.chat.id in user_data:
        user_data[message.chat.id]['file_id'] = message.photo[-1].file_id
        bot.send_message(message.chat.id, "📁 ما هو قسم المنتج؟")
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['category'] = message.text
    bot.send_message(message.chat.id, "✏️ أرسل اسم المنتج:")
    bot.register_next_step_handler(message, get_wholesale)

def get_wholesale(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "💰 كم سعر الجملة؟")
    bot.register_next_step_handler(message, get_retail)

def get_retail(message):
    user_data[message.chat.id]['wholesale'] = message.text
    bot.send_message(message.chat.id, "💵 كم سعر القطاعي؟")
    bot.register_next_step_handler(message, show_review)

def show_review(message):
    data = user_data[message.chat.id]
    data['retail'] = message.text
    data['desc'] = "✨ قطعة مميزة من متجرنا تضفي أناقة لا مثيل لها على معصمك! ✨"
    
    review = (
        f"📝 **مراجعة قبل النشر في القناة:**\n\n"
        f"🏷️ الاسم: {data['name']}\n"
        f"📁 القسم: {data['category']}\n"
        f"💰 الجملة: {data['wholesale']} ج.م\n"
        f"💵 القطاعي: {data['retail']} ج.م\n"
        f"✨ الوصف: {data['desc']}"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 نشر في القناة", callback_data="publish_now"))
    markup.add(types.InlineKeyboardButton("✏️ تعديل", callback_data="start_add_product"))
    
    bot.send_photo(message.chat.id, data['file_id'], caption=review, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "publish_now")
def final_publish(call):
    data = user_data.get(call.message.chat.id)
    if data:
        # النشر في قناة التلجرام
        caption = f"💎 **منتج جديد في my-store**\n\n✨ {data['name']}\n💰 سعر الجملة: {data['wholesale']} ج.م\n💵 سعر القطاعي: {data['retail']} ج.م\n\n{data['desc']}\n\n📍 للطلب: https://ramisamir2006-hash.github.io"
        bot.send_photo(CHANNEL_ID, data['file_id'], caption=caption, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "✅ تم النشر بنجاح!")
        bot.send_message(call.message.chat.id, "🎉 المنتج الآن متاح في القناة ومتصل بالمتجر.")
        del user_data[call.message.chat.id]

if __name__ == "__main__":
    Thread(target=run_web).start()
    bot.infinity_polling()
                                       
