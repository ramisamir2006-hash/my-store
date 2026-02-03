import os
import telebot
from telebot import types
from supabase import create_client
from flask import Flask
from threading import Thread

# إعداد سيرفر وهمي لإبقاء Koyeb سعيداً (تجنب Unhealthy)
app = Flask('')
@app.route('/')
def home():
    return "My-Store Bot is Online!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# جلب الإعدادات
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# لوحة التحكم الشاملة للمدير
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة قسم", "📦 المخزون", "➕ إضافة منتج", "🖼️ المنتجات")
    markup.add("📊 تقارير", "🎟️ خصم", "👥 العملاء", "📢 حملة إعلانية")
    bot.send_message(message.chat.id, "💎 لوحة تحكم my-store الشاملة\nاختر المهمة:", reply_markup=markup)

# --- إدارة العملاء والرسائل الجماعية ---
@bot.message_handler(func=lambda m: m.text == "👥 العملاء")
def list_clients(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 إرسال للكل", callback_data="broadcast_all"))
    markup.add(types.InlineKeyboardButton("👤 تحديد عميل", callback_data="select_user"))
    bot.send_message(message.chat.id, "قائمة العملاء والتحكم:", reply_markup=markup)

# --- التقارير التفصيلية ---
@bot.message_handler(func=lambda m: m.text == "📊 تقارير")
def full_report(message):
    # محاكاة لبيانات الزوار والطلبات
    report = (
        "📈 **تقرير my-store اليومي**\n\n"
        "🛍️ عدد الطلبات: 12 طلب\n"
        "👥 عدد الزوار الجدد: 45 زائر\n"
        "🕒 أوقات الذروة: 09:00 PM - 11:00 PM\n"
        "✅ الطلبات المكتملة: 8"
    )
    bot.reply_to(message, report, parse_mode="Markdown")

# --- تحديث حالة الطلب ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("status_"))
def update_order_status(call):
    status_map = {
        "status_ready": "تم التجهيز ✅",
        "status_shipped": "مع الطيار 🚚",
        "status_delivered": "تم الاستلام 🏁"
    }
    new_status = status_map.get(call.data)
    bot.answer_callback_query(call.id, f"تم التحديث إلى: {new_status}")
    bot.edit_message_text(f"حالة الطلب الجديدة: {new_status}", call.message.chat.id, call.message.message_id)

# تشغيل السيرفر والبوت معاً
if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    print("Bot is starting...")
    bot.infinity_polling()
                     
