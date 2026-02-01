import telebot
from supabase import create_client

# الإعدادات
TOKEN = "8395659007:AAFlSG4TWEQnBixfabDpkjLkol5ytFri9D0"
URL = "رابط_مشروعك_من_supabase"
KEY = "مفتاح_anon_من_supabase"
CHANNEL = "@RamySamir2026Gold"
WEBSITE = "https://ramisamir2006-hash.github.io"

bot = telebot.TeleBot(TOKEN)
db = create_client(URL, KEY)

@bot.message_handler(commands=['start'])
def welcome(message):
    msg = (f"مرحباً بك في لوحة تحكم {WEBSITE}\n\n"
           "🔸 لإضافة منتج أرسل:\n"
           "اسم المنتج - سعر قطاعي - سعر جملة - رابط الصورة\n\n"
           "🔸 للحصول على تقرير أرسل: /report")
    bot.reply_to(message, msg)

@bot.message_handler(commands=['report'])
def send_report(message):
    # تقرير سريع بعدد المنتجات
    res = db.table("products").select("id", count="exact").execute()
    count = res.count
    bot.reply_to(message, f"📊 تقرير my-store اليومي:\n✅ عدد المنتجات المعروضة: {count}")

@bot.message_handler(func=lambda m: "-" in m.text)
def handle_add(message):
    try:
        # معالجة النص
        data = [i.strip() for i in message.text.split("-")]
        name, retail, wholesale, img = data[0], data[1], data[2], data[3]

        # 1. تحديث قاعدة البيانات (الموقع)
        db.table("products").insert({
            "name": name, "price_retail": retail, 
            "price_wholesale": wholesale, "image_url": img
        }).execute()

        # 2. النشر في القناة
        caption = f"✨ {name}\n💰 قطاعي: {retail} ج.م\n📦 جملة: {wholesale} ج.م\n\n🌐 اطلب الآن: {WEBSITE}"
        bot.send_photo(CHANNEL, img, caption=caption)
        
        bot.reply_to(message, "✅ تم تحديث الموقع والنشر في القناة بنجاح!")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ في البيانات. تأكد من وجود 3 فواصل (-)\nالخطأ: {e}")

print("my-store bot is active...")
bot.polling()
