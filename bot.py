import os
import telebot
from supabase import create_client

# سحب البيانات من إعدادات السيرفر (Environment Variables)
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL = "@RamySamir2026Gold"
WEBSITE = "https://ramisamir2006-hash.github.io"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, f"مرحباً بك في لوحة تحكم {WEBSITE}\nأرسل المنتج كالتالي:\nاسم - سعر قطاعي - سعر جملة - رابط صورة")

@bot.message_handler(func=lambda m: "-" in m.text)
def handle_add(message):
    try:
        data = [i.strip() for i in message.text.split("-")]
        name, retail, wholesale, img = data[0], data[1], data[2], data[3]

        db.table("products").insert({
            "name": name, "price_retail": retail, 
            "price_wholesale": wholesale, "image_url": img
        }).execute()

        caption = f"✨ {name}\n💰 قطاعي: {retail} ج.م\n📦 جملة: {wholesale} ج.م\n🌐 {WEBSITE}"
        bot.send_photo(CHANNEL, img, caption=caption)
        bot.reply_to(message, "✅ تم التحديث والنشر!")
    except Exception as e:
        bot.reply_to(message, "❌ تأكد من التنسيق: اسم - سعر - سعر - رابط")

print("Bot is running...")
bot.polling()
