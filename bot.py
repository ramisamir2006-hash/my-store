import os
import telebot
from supabase import create_client
from telebot import types

# تأكد من إضافة هذه المتغيرات في إعدادات Koyeb
TOKEN = os.getenv("BOT_TOKEN")
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
CHANNEL = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(URL, KEY)

@bot.message_handler(commands=['start'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🛍️ إضافة منتج", "📊 التقارير", "💡 كلمات تسويقية", "🚀 حملة إعلانية")
    bot.send_message(message.chat.id, "💎 لوحة تحكم my-store جاهزة:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🛍️ إضافة منتج")
def step1(message):
    bot.reply_to(message, "أرسل البيانات بالترتيب:\nالقسم - الاسم - قطاعي - جملة - رابط الصورة")

@bot.message_handler(func=lambda m: "-" in m.text)
def process_add(message):
    try:
        parts = [i.strip() for i in message.text.split("-")]
        cat, name, retail, wholesale, img = parts
        
        # 1. الحفظ في القاعدة
        db.table("products").insert({
            "category": cat, "name": name, "price_retail": retail, 
            "price_wholesale": wholesale, "image_url": img
        }).execute()
        
        # 2. النشر في القناة
        text = f"✨ {name}\n🏷️ القسم: {cat}\n💰 قطاعي: {retail} ج.م\n📦 جملة: {wholesale} ج.م\n📍 https://ramisamir2006-hash.github.io"
        bot.send_photo(CHANNEL, img, caption=text)
        bot.reply_to(message, "✅ تم النشر بنجاح!")
    except:
        bot.reply_to(message, "⚠️ خطأ! تأكد من وجود 4 فواصل (-)")

@bot.message_handler(func=lambda m: m.text == "📊 التقارير")
def report(message):
    res = db.table("products").select("id", count="exact").execute()
    bot.reply_to(message, f"📈 إحصائيات my-store:\nعدد المنتجات الحالية: {res.count}")

@bot.message_handler(func=lambda m: m.text == "💡 كلمات تسويقية")
def marketing(message):
    bot.reply_to(message, "💎 موديلات 2026 وصلت!\n🔥 خصم خاص للجملة\n✨ الأناقة تبدأ من my-store")

bot.polling()
