import telebot
from telebot import types

# --- الإعدادات الصحيحة بناءً على صورك ---
TOKEN = "8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I"
ADMIN_ID = 7020070481  # معرف رامي سمير
CHANNEL_ID = -1003223634521

bot = telebot.TeleBot(TOKEN)

# --- 1. لوحات التحكم (Keyboards) ---

def admin_keyboard():
    """لوحة التحكم الكاملة للمدير - إدارة كل المتجر"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        "➕ إضافة منتج جديد", "📦 إدارة الطلبات",
        "💰 خصومات الجملة", "🏷️ خصومات التجزئة",
        "👥 إدارة الموظفين", "📊 التقارير اليومية",
        "🎧 خدمة العملاء", "🛍️ تصفح كزبون"
    )
    return markup

def user_store_keyboard():
    """واجهة المتجر الاحترافية (تصميم سلة ماريا)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # ترتيب الأزرار والرموز تماماً مثل الصور التي أرفقتها
    markup.add(
        types.KeyboardButton("📱 تصفح المتجر 🛍️"),
        types.KeyboardButton("📢 قناتنا"),
        types.KeyboardButton("🛒 السلة"),
        types.KeyboardButton("📞 خدمة العملاء")
    )
    return markup

# --- 2. معالجة الأوامر والرسائل ---

@bot.message_handler(commands=['start', 'panel'])
def start_command(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "🛡️ أهلاً رامي سمير. تم تفعيل لوحة الإدارة الشاملة لـ @Stormarketing_bot", 
            reply_markup=admin_keyboard()
        )
    else:
        # نص ترحيبي مطابق لأسلوب متجر ماريا
        welcome_text = "أهلاً بك في متجرنا! 👋\n\nاستخدم القائمة بالأسفل للتصفح ومتابعة طلباتك 👇"
        bot.send_message(message.chat.id, welcome_text, reply_markup=user_store_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text_interactions(message):
    user_id = message.from_user.id
    text = message.text

    # --- ردود أفعال لوحة المدير ---
    if user_id == ADMIN_ID:
        if text == "➕ إضافة منتج جديد":
            bot.reply_to(message, "📸 من فضلك أرسل صورة المنتج مع السعر والوصف للرفع.")
        elif text == "📊 التقارير اليومية":
            bot.reply_to(message, "📈 جاري سحب بيانات المبيعات الحالية...")
        elif text == "🛍️ تصفح كزبون":
            bot.send_message(message.chat.id, "معاينة واجهة الزبائن:", reply_markup=user_store_keyboard())

    # --- ردود أفعال لوحة المتجر (الزبائن) ---
    if text == "📱 تصفح المتجر 🛍️":
        markup = types.InlineKeyboardMarkup()
        # زر يفتح المتجر كصفحة ويب داخلية (WebApp)
        markup.add(types.InlineKeyboardButton("🛍️ اضغط هنا لفتح المتجر", web_app=types.WebAppInfo(url="https://yourstore.com")))
        bot.send_message(message.chat.id, "تفضل بزيارة متجرنا الإلكتروني السريع 👇", reply_markup=markup)

    elif text == "📞 خدمة العملاء":
        support_msg = "مركز التواصل والدعم الفني 📞\n\nنحن هنا لمساعدتك! ساعات العمل:\n⏰ يومياً من 11 صباحاً حتى 9 مساءً."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 تواصل معنا واتساب", url="https://wa.me/201277123567"))
        bot.send_message(message.chat.id, support_msg, reply_markup=markup)

    elif text == "🛒 السلة":
        bot.send_message(message.chat.id, "🛒 سلتك فارغة حالياً. ابدأ بالتسوق!")

# --- 3. تشغيل البوت ---
if __name__ == "__main__":
    print("🚀 البوت @Stormarketing_bot يعمل الآن بتصميم المتجر الاحترافي...")
    bot.infinity_polling()
    
