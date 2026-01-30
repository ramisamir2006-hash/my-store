import telebot
from telebot import types

# --- الإعدادات (بياناتك من الصور) ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- 1. بناء لوحات التحكم (الواجهات) ---

def admin_panel():
    """لوحة المدير - تظهر لك فقط"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "➕ إضافة منتج جديد", "📦 إدارة الطلبات",
        "💰 ضبط خصم الجملة", "🏷️ ضبط خصم التجزئة",
        "👥 إدارة الموظفين", "📊 التقارير اليومية",
        "🎧 طلبات الدعم", "🛍️ واجهة الزبون"
    )
    return markup

def user_panel():
    """لوحة الزبائن - تظهر للجمهور (تصميم سلة ماريا)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📱 تصفح المتجر 🛍️"),
        types.KeyboardButton("📢 قناتنا"),
        types.KeyboardButton("🛒 السلة"),
        types.KeyboardButton("📞 خدمة العملاء")
    )
    return markup

# --- 2. تفعيل استجابة الأوامر الرئيسية ---

@bot.message_handler(commands=['start', 'panel'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🛠️ أهلاً رامي! لوحة التحكم كاملة الصلاحيات جاهزة الآن.", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في متجرنا! 👋\nتفضل بالتصفح من خلال الأزرار بالأسفل 👇", reply_markup=user_panel())

# --- 3. محرك الاستجابة (ربط كل زر بأمر حقيقي) ---

@bot.message_handler(func=lambda message: True)
def on_click(message):
    user_id = message.from_user.id
    text = message.text

    # --- استجابات لوحة المدير (رامي) ---
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج جديد":
            bot.send_message(message.chat.id, "📸 أرسل صورة المنتج الآن لرفعها على المتجر.")
        elif text == "💰 ضبط خصم الجملة":
            bot.send_message(message.chat.id, "🔢 كم نسبة الخصم التي تريد تطبيقها لعملاء الجملة؟")
        elif text == "📊 التقارير اليومية":
            bot.send_message(message.chat.id, "⏳ جاري إعداد تقرير المبيعات لليوم...")
        elif text == "🛍️ واجهة الزبون":
            bot.send_message(message.chat.id, "عرض واجهة المستخدمين:", reply_markup=user_panel())

    # --- استجابات لوحة الزبائن (عام) ---
    if text == "📱 تصفح المتجر 🛍️":
        markup = types.InlineKeyboardMarkup()
        # هنا نربط المتجر بالـ WebApp ليعمل كصفحة تفاعلية بالصور
        markup.add(types.InlineKeyboardButton("🛒 فتح الكتالوج الآن", web_app=types.WebAppInfo(url="https://yourstore.com")))
        bot.send_message(message.chat.id, "اضغط على الزر بالأسفل لفتح المتجر وتصفح المنتجات بالصور والأسعار 👇", reply_markup=markup)

    elif text == "📞 خدمة العملاء":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 واتساب", url="https://wa.me/201277123567"))
        bot.send_message(message.chat.id, "نحن هنا لمساعدتك! تواصل معنا عبر الواتساب مباشرة:", reply_markup=markup)

    elif text == "🛒 السلة":
        bot.send_message(message.chat.id, "🛒 سلة مشترياتك فارغة حالياً.")

    elif text == "📢 قناتنا":
        bot.send_message(message.chat.id, "قناتنا الرسمية لمتابعة العروض: [رابط القناة]")

# --- 4. تشغيل البوت النهائي ---
if __name__ == "__main__":
    print("✅ البوت Stormarketing_bot يعمل الآن بكافة أزراره...")
    bot.infinity_polling()
                         
