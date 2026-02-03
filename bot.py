import os
import telebot
from telebot import types
from supabase import create_client
from flask import Flask
from threading import Thread

# 1. إصلاح تشغيل Flask (إضافة logger لمنع رسائل التحذير المزعجة)
app = Flask(__name__)

@app.route('/')
def home():
    return "My-Store Bot is Online and Healthy!"

def run_web():
    # Koyeb يحتاج الاستماع على 0.0.0.0 والمنفذ الممرر في المتغيرات
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# جلب الإعدادات بأمان
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL = "@RamySamir2026Gold"

# التحقق من وجود التوكن قبل التشغيل لمنع الانهيار (Crash)
if not TOKEN or not SUPABASE_KEY:
    print("❌ خطأ: لم يتم العثور على المتغيرات البيئية (BOT_TOKEN أو SUPABASE_KEY)")
    exit(1)

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# لوحة التحكم الرئيسية
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة قسم", "📦 المخزون", "➕ إضافة منتج", "🖼️ المنتجات")
    markup.add("📊 تقارير", "🎟️ خصم", "👥 العملاء", "📢 حملة إعلانية")
    bot.send_message(message.chat.id, "💎 أهلاً بك في لوحة تحكم my-store\nاختر من الأزرار بالأسفل:", reply_markup=markup)

# --- إدارة العملاء ---
@bot.message_handler(func=lambda m: m.text == "👥 العملاء")
def list_clients(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 إرسال للكل", callback_data="broadcast_all"))
    markup.add(types.InlineKeyboardButton("👤 تحديد عميل", callback_data="select_user"))
    bot.send_message(message.chat.id, "إدارة العملاء:", reply_markup=markup)

# --- التقارير ---
@bot.message_handler(func=lambda m: m.text == "📊 تقارير")
def full_report(message):
    try:
        # محاولة جلب عدد المنتجات الحقيقي من Supabase
        res = db.table("products").select("id", count="exact").execute()
        total_products = res.count if res.count else 0
        
        report = (
            "📈 **تقرير my-store اليومي**\n\n"
            f"📦 إجمالي المنتجات: {total_products}\n"
            "🛍️ عدد طلبات اليوم: 12 (تجريبي)\n"
            "👥 عدد الزوار: 45 (تجريبي)\n"
            "✅ الحالة: السيرفر متصل"
        )
        bot.reply_to(message, report, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ أثناء جلب التقارير: {e}")

# --- تشغيل البوت والسيرفر معاً ---
if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل لضمان استجابة Koyeb Health Check
    t = Thread(target=run_web)
    t.daemon = True # لضمان إغلاق السيرفر عند إغلاق التطبيق
    t.start()
    
    print("🚀 Bot is starting with Flask server...")
    # استخدام non_stop لضمان عدم توقف البوت عند حدوث خطأ في الشبكة
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    
