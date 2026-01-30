import telebot
from telebot import types
import json
from datetime import datetime

# --- إعدادات الربط النهائية ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
CHANNEL_ID = "@RamySamir2026Gold"  # معرف قناتك
ADMIN_ID = 7020070481             # معرفك الشخصي (رامي سمير)

bot = telebot.TeleBot(TOKEN)

# --- 1. لوحات التحكم (Reply Keyboards) ---

def admin_keyboard():
    """لوحة تحكم المدير رامي التي تظهر أسفل الشاشة"""
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
    """لوحة تحكم الزبائن العادية"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🛍️ دخول المتجر"),
        types.KeyboardButton("📞 الدعم الفني")
    )
    return markup

# --- 2. الأوامر الأساسية ---

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "أهلاً يا أستاذ رامي! لوحة الإدارة جاهزة للعمل.. ماذا تريد أن تفعل اليوم؟", 
            reply_markup=admin_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id, 
            "مرحباً بك في مجوهرات رامي سمير الذهبية ✨\nنقدم لك أفخم الموديلات بأسعار مميزة.", 
            reply_markup=user_keyboard()
        )

# --- 3. معالجة بيانات المتجر (النشر والطلبات) ---

@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        
        # أ- معالجة طلب النشر في القناة
        if data.get("action") == "publish":
            publish_to_channel(data)
            bot.reply_to(message, "✅ تم النشر في القناة بنجاح يا رامي!")

        # ب- معالجة طلب شراء جديد
        elif data.get("action") == "order":
            send_order_to_admin(data)
            bot.reply_to(message, "✅ تم إرسال طلبك بنجاح! سيتم التواصل معك قريباً.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ حدث خطأ أثناء استقبال البيانات: {str(e)}")

# --- 4. الوظائف التشغيلية ---

def publish_to_channel(p):
    """وظيفة تنسيق ونشر المنتج في القناة مع 10 صور وأزرار"""
    caption = (
        f"✨ **{p['name']}** ✨\n\n"
        f"📝 {p['desc']}\n\n"
        f"📏 المقاسات المتاحة: {p['sizes']}\n"
        f"💰 السعر: {p['price']} ج.م\n"
        f"🏷 القسم: #{p.get('cat', 'مجوهرات')}\n\n"
        f"🔥 {p.get('marketing_text', 'قطعة فريدة تليق بجمالك.. اطلبيها الآن!')}"
    )

    # تجهيز ميديا الصور (حتى 10)
    media = []
    for i, url in enumerate(p['imgs']):
        if i == 0:
            media.append(types.InputMediaPhoto(url, caption=caption, parse_mode="Markdown"))
        else:
            media.append(types.InputMediaPhoto(url))

    if media:
        # إرسال ألبوم الصور
        bot.send_media_group(CHANNEL_ID, media)
        
        # إرسال زر الشراء تحت الألبوم
        markup = types.InlineKeyboardMarkup()
        # ملاحظة: يجب التأكد من ضبط رابط المتجر في BotFather ليعمل الزر
        markup.add(types.InlineKeyboardButton("🛒 اطلب المنتج الآن", url=f"https://t.me/{bot.get_me().username}/app"))
        bot.send_message(CHANNEL_ID, "للحجز والاستفسار اضغط على الزر 👇", reply_markup=markup)

def send_order_to_admin(order):
    """إرسال تفاصيل الأوردر كاملة إلى رامي"""
    msg = (
        f"🚨 **أوردر جديد يا رامي!**\n\n"
        f"👤 العميل: {order['customer']}\n"
        f"📞 الهاتف: {order['phone']}\n"
        f"📍 العنوان: {order['address']}\n"
        f"🚚 النوع: {'توصيل' if order['type']=='delivery' else 'استلام من المحل'}\n"
        f"⏰ الموعد: {order['time']}\n"
        f"--------------------------\n"
        f"📦 المنتجات المطلوبة:\n"
    )
    for item in order['items']:
        msg += f"- {item['name']} (مقاس: {item['selectedSize']})\n"
    
    msg += f"\n💰 الإجمالي: {order['total']} ج.م"
    bot.send_message(ADMIN_ID, msg)

# --- 5. الرد على أزرار لوحة التحكم ---

@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == "📊 التقارير اليومية":
            bot.send_message(ADMIN_ID, "📈 تقرير المبيعات اليوم:\n- عدد الطلبات: 0\n- الإجمالي: 0 ج.م\n(يتم التحديث فور إتمام عمليات حقيقية)")
        elif message.text == "➕ إضافة منتج جديد":
            bot.send_message(ADMIN_ID, "تفضل بفتح المتجر واستخدام لوحة الإدارة لإضافة المنتج والقسم الجديد.")
        # يمكنك إضافة ردود لباقي الأزرار هنا بنفس الطريقة
    
    elif message.text == "📞 الدعم الفني":
        bot.send_message(message.chat.id, "أهلاً بك.. ارسل استفسارك الآن وسيرد عليك الأستاذ رامي في أقرب وقت.")

# --- بدء التشغيل ---
print("✅ تم الدمج بنجاح.. البوت يعمل الآن ومرتبط بالقناة @RamySamir2026Gold")
bot.polling(none_stop=True)
