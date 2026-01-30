import telebot
from telebot import types
import json
from datetime import datetime

# --- إعداداتك الأساسية ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
CHANNEL_ID = "@RamySamir2026Gold"
ADMIN_ID = 7020070481

bot = telebot.TeleBot(TOKEN)

# --- لوحة تحكم المدير السفلية (Reply Keyboard) ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        types.KeyboardButton("📊 التقارير اليومية"),
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("👥 العملاء والحظر"),
        types.KeyboardButton("➕ إضافة منتج جديد"),
        types.KeyboardButton("💬 الاستفسارات"),
        types.KeyboardButton("💰 ضبط الخصومات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    ]
    markup.add(*btns)
    return markup

def user_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🛍️ دخول المتجر"), types.KeyboardButton("📞 الدعم الفني"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً يا رامي! لوحة التحكم كاملة تحت أمرك 👇", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في مجوهرات رامي سمير ✨", reply_markup=user_keyboard())

# --- استقبال البيانات من المتجر (النشر والأوردرات) ---
@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    data = json.loads(message.web_app_data.data)
    
    # 1. حالة النشر التلقائي (حتى 10 صور)
    if data.get("action") == "publish":
        caption = f"✨ **{data['name']}** ✨\n\n📝 {data['desc']}\n\n📏 المقاسات: {data['sizes']}\n💰 السعر: {data['price']} ج.م\n🏷 القسم: #{data['cat']}\n\n🔥 {data.get('marketing_text', '')}"
        media = []
        for i, url in enumerate(data['imgs']):
            if i == 0: media.append(types.InputMediaPhoto(url, caption=caption, parse_mode="Markdown"))
            else: media.append(types.InputMediaPhoto(url))
        
        bot.send_media_group(CHANNEL_ID, media)
        bot.send_message(ADMIN_ID, "✅ تم النشر في القناة بنجاح!")

    # 2. حالة استقبال أوردر جديد ببيانات الشحن
    elif data.get("action") == "order":
        msg = f"🚨 **أوردر جديد!**\n👤 العميل: {data['customer']}\n📞 هاتف: {data['phone']}\n📍 عنوان: {data['address']}\n🚚 استلام: {data['type']}\n⏰ موعد: {data['time']}\n💰 الإجمالي: {data['total']} ج.م\n📦 المنتجات:\n"
        for item in data['items']:
            msg += f"- {item['name']} (مقاس: {item['selectedSize']})\n"
        bot.send_message(ADMIN_ID, msg)

# --- تشغيل البوت ---
print("✅ البوت شغال ومرتبط بالقناة...")
bot.polling()
