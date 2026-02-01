import os
import telebot
from supabase import create_client
from telebot import types

# سحب البيانات آلياً من إعدادات Koyeb
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- لوحة التحكم (الأزرار) ---
@bot.message_handler(commands=['start', 'menu'])
def start_panel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍️ إضافة منتج", "📊 التقارير", "📁 إضافة قسم", "💡 تسويق")
    bot.send_message(message.chat.id, "✅ متصل بملف: 70mkt1o8v...\n💎 لوحة تحكم my-store جاهزة:", reply_markup=markup)

# --- معالجة إضافة المنتجات ---
@bot.message_handler(func=lambda m: "-" in m.text)
def add_item(message):
    try:
        parts = [i.strip() for i in message.text.split("-")]
        cat, name, retail, wholesale, img = parts
        db.table("products").insert({
            "category": cat, "name": name, "price_retail": retail, 
            "price_wholesale": wholesale, "image_url": img
        }).execute()
        
        caption = f"✨ {name}\n💰 جملة: {wholesale} ج.م\n📍 https://ramisamir2006-hash.github.io"
        bot.send_photo(CHANNEL, img, caption=caption)
        bot.reply_to(message, "✅ تم النشر بنجاح!")
    except:
        bot.reply_to(message, "⚠️ خطأ في التنسيق! (قسم - اسم - قطاعي - جملة - رابط)")

# تشغيل البوت بنظام Infinity لضمان عدم التوقف
bot.infinity_polling()
