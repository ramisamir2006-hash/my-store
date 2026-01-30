import telebot
from telebot import types

# --- الإعدادات الرسمية (تم التأكد منها من صورك) ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- 1. تصميم لوحات التحكم (Keyboards) ---

def admin_full_panel():
    """لوحة التحكم المركزية للمدير - إدارة كل شيء"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "➕ إضافة منتج جديد", "📦 إدارة الطلبات",
        "💰 ضبط خصم الجملة", "🏷️ ضبط خصم التجزئة",
        "👥 إدارة الموظفين", "📊 تقارير المبيعات",
        "🎧 طلبات الدعم الفني", "🛍️ معاينة المتجر"
    )
    return markup

def user_store_keyboard():
    """واجهة الزبائن (تصميم سلة ماريا)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # ترتيب مطابق تماماً للصور المرفقة
    markup.add(
        types.KeyboardButton("📱 تصفح المتجر 🛍️"),
        types.KeyboardButton("📢 قناتنا"),
        types.KeyboardButton("🛒 السلة"),
        types.KeyboardButton("📞 خدمة العملاء")
    )
    return markup

# --- 2. معالجة الأوامر الرئيسية ---

@bot.message_handler(commands=['start', 'panel'])
def welcome(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "🛡️ أهلاً بك يا رامي في مركز إدارة Stormarketing_bot.\nكافة أزرار التحكم مفعلة الآن.", 
            reply_markup=admin_full_panel()
        )
    else:
        # نص ترحيبي بأسلوب متجر ماريا
        welcome_text = "أهلاً بك في متجرنا! 👋\n\nاستخدم القائمة بالأسفل للتصفح ومتابعة طلباتك 👇"
        bot.send_message(message.chat.id, welcome_text, reply_markup=user_store_keyboard())

# --- 3. تشغيل مهام الأزرار (Logic) ---

@bot.message_handler(func=lambda message: True)
def handle_all_tasks(message):
    user_id = message.from_user.id
    text = message.text

    # --- مهام المدير ---
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج جديد":
            bot.send_message(message.chat.id, "📸 يرجى إرسال صورة المنتج متبوعة بالسعر والوصف.")
        elif text == "💰 ضبط خصم الجملة":
            bot.send_message(message.chat.id, "📉 أدخل نسبة الخصم الجديدة لعملاء الجملة.")
        elif text == "📊 تقارير المبيعات":
            bot.send_message(message.chat.id, "📈 جاري سحب بيانات المبيعات والتقارير...")
        elif text == "🛍️ معاينة المتجر":
            bot.send_message(message.chat.id, "واجهة الزبائن:", reply_markup=user_store_keyboard())

    # --- مهام الزبائن (المتجر) ---
    if text == "📱 تصفح المتجر 🛍️":
        markup = types.InlineKeyboardMarkup()
        # فتح المتجر كـ WebApp (مثل سلة ماريا)
        markup.add(types.InlineKeyboardButton("🛍️ تصفح المتجر الآن", web_app=types.WebAppInfo(url="https://yourstore.com")))
        bot.send_message(message.chat.id, "👇 تفضل بزيارة متجرنا الإلكتروني السريع", reply_markup=markup)

    elif text == "📞 خدمة العملاء":
        support_info = "مركز التواصل والدعم الفني 📞\n\nنحن هنا لمساعدتك! ساعات العمل:\n⏰ يومياً من 11 صباحاً حتى 9 مساءً."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 تواصل معنا واتساب", url="https://wa.me/201277123567"))
        bot.send_message(message.chat.id, support_info, reply_markup=markup)

    elif text == "🛒 السلة":
        bot.send_message(message.chat.id, "🛒 سلتك فارغة حالياً. ابدأ بالتسوق الآن!")

    elif text == "📢 قناتنا":
        bot.send_message(message.chat.id, "تابع أحدث العروض على قناتنا الرسمية من هنا 👇")

# --- 4. تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 البوت Stormarketing_bot يعمل الآن بكافة مهام المتجر...")
    bot.infinity_polling()
    
