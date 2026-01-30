import telebot
from telebot import types
import json

# --- إعدادات الربط ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
CHANNEL_ID = "@RamySamir2026Gold"  # معرف قناتك
ADMIN_ID = 7020070481             # معرفك الشخصي

bot = telebot.TeleBot(TOKEN)

# دالة استقبال البيانات من المتجر (Web App)
@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        
        # 1. حالة النشر الجديد في القناة
        if data.get("action") == "publish":
            publish_to_channel(data)
            bot.reply_to(message, "✅ تم نشر المنتج وتنسيقه في القناة بنجاح!")

        # 2. حالة استقبال أوردر جديد
        elif data.get("action") == "order":
            send_order_to_admin(data)
            bot.reply_to(message, "✅ تم إرسال طلبك للمدير رامي، سيتم التواصل معك قريباً.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطأ في معالجة البيانات: {str(e)}")

# دالة النشر في القناة (تدعم حتى 10 صور + أزرار)
def publish_to_channel(p):
    # تنسيق الرسالة (وصف تشويقي)
    caption = f"✨ **{p['name']}** ✨\n\n"
    caption += f"📝 {p['desc']}\n\n"
    caption += f"📏 المقاسات المتاحة: {p['sizes']}\n"
    caption += f"💰 السعر: {p['price']} ج.م\n"
    caption += f"🏷 القسم: #{p['cat']}\n\n"
    caption += "🔥 قطعة فريدة تليق بجمالك.. اطلبيها الآن!"

    # تجهيز مجموعة الصور
    media = []
    for i, url in enumerate(p['imgs']):
        if i == 0:
            media.append(types.InputMediaPhoto(url, caption=caption, parse_mode="Markdown"))
        else:
            media.append(types.InputMediaPhoto(url))

    # إرسال الصور للقناة
    if media:
        msgs = bot.send_media_group(CHANNEL_ID, media)
        
        # إضافة زر "اطلب الآن" تحت آخر صورة (اختياري)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 اطلب المنتج الآن", url=f"https://t.me/{bot.get_me().username}/app"))
        bot.send_message(CHANNEL_ID, "للحجز أو الاستفسار اضغط على الزر 👇", reply_markup=markup)

# دالة إرسال الطلب للمدير رامي
def send_order_to_admin(order):
    msg = f"🚨 **أوردر جديد يا رامي!**\n\n"
    msg += f"👤 العميل: {order['customer']}\n"
    msg += f"📞 الهاتف: {order['phone']}\n"
    msg += f"📍 العنوان: {order['address']}\n"
    msg += "--------------------------\n"
    msg += "📦 المنتجات:\n"
    for item in order['items']:
        msg += f"- {item['name']} (مقاس: {item['selectedSize']})\n"
    
    bot.send_message(ADMIN_ID, msg)

print("✅ البوت يعمل الآن ومرتبط بالقناة بنجاح...")
bot.polling()
