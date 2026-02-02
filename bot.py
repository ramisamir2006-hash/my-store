import os
import telebot
from telebot import types
from supabase import create_client

# جلب الإعدادات من Koyeb Variables
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# لوحة التحكم الرئيسية
@bot.message_handler(commands=['start', 'menu'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج", "📊 تقارير", "📁 أقسام", "💡 تسويق")
    bot.send_message(message.chat.id, "💎 أهلاً بك في لوحة تحكم my-store\nاختر من الأزرار بالأسفل:", reply_markup=markup)

# إضافة منتج (تنسيق بسيط لتجنب الأخطاء)
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج")
def add_hint(message):
    bot.reply_to(message, "أرسل البيانات بهذا التنسيق:\nالقسم - الاسم - سعر قطاعي - سعر جملة - رابط الصورة")

# استقبال البيانات والنشر
@bot.message_handler(func=lambda m: "-" in m.text)
def process_data(message):
    try:
        parts = [i.strip() for i in message.text.split("-")]
        if len(parts) == 5:
            cat, name, retail, wholesale, img = parts
            
            # حفظ في الموقع
            db.table("products").insert({
                "category": cat, "name": name, 
                "price_retail": retail, "price_wholesale": wholesale, 
                "image_url": img
            }).execute()
            
            # نشر في القناة
            caption = f"✨ {name}\n💰 جملة: {wholesale} ج.م\n📍 https://ramisamir2006-hash.github.io"
            bot.send_photo(CHANNEL, img, caption=caption)
            bot.reply_to(message, "✅ تم النشر وتحديث المتجر!")
        else:
            bot.reply_to(message, "⚠️ تأكد من وجود 4 فواصل (-) بين البيانات")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

# التقارير
@bot.message_handler(func=lambda m: m.text == "📊 تقارير")
def report(message):
    res = db.table("products").select("id", count="exact").execute()
    bot.reply_to(message, f"📈 إجمالي المنتجات في متجر my-store: {res.count}")

# تشغيل البوت
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
