import os, telebot, threading
from telebot import types
from flask import Flask

# --- إعدادات المنصة المخصصة لـ @Stormarketing_bot ---
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@RamySamir2026Gold"  # قناتك العامة
STAFF_GROUP_ID = -1002376483563   # جروب الموظفين
STAFF_LINK = "https://t.me/+Zu6NKNYqTgVkZGFk"

# المسؤول الأول (أنت)
ADMIN_ID = 7020070481 

bot = telebot.TeleBot(TOKEN)
user_data = {}  # مخزن مؤقت للبيانات

@app.route('/')
def home(): return "Stormarketing Bot is Active"

# --- دالة التحقق من الصلاحيات ---
def is_authorized(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(STAFF_GROUP_ID, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except:
        return False

# --- 1. واجهة صفحة البوت الرئيسية (زراير التحكم) ---
def main_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج جديد", "📊 تقارير المبيعات")
    markup.add("📁 إدارة الأقسام", "👥 فريق العمل (الموظفين)")
    markup.add("🖼️ تغيير غلاف المتجر", "⚙️ الإعدادات العامة")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    # شكل ترحيبي احترافي في صفحة البوت
    welcome_msg = (
        f"🤖 **مرحباً بك في لوحة تحكم Stormarketing_bot**\n\n"
        f"🆔 **ID:** `{message.from_user.id}`\n"
        f"🔗 **Username:** @Stormarketing_bot\n"
        f"🏳️ **Lang:** AR 🇪🇬\n"
        f"---------------------------\n"
        f"استخدم الأزرار أدناه لإدارة متجرك ونشر المنتجات."
    )
    bot.send_message(message.chat.id, welcome_msg, reply_markup=main_admin_keyboard(), parse_mode="Markdown")

# --- 2. نظام إضافة المنتج (سؤال تلو الآخر) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def start_add(message):
    if not is_authorized(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ عذراً، هذا القسم مخصص للإدارة فقط.")
    
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 **الخطوة 1:** أرسل صورة المنتج (Photo):")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ خطأ! يرجى إرسال صورة المنتج.")
        return bot.register_next_step_handler(message, get_photo)
    user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✏️ **الخطوة 2:** أرسل اسم المنتج ووصفه:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "💰 **الخطوة 3:** أرسل السعر بالجنيه (أرقام فقط):")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_data[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📏 **الخطوة 4:** أرسل المقاسات المتاحة (افصلي بينها بفاصلة ,):")
    bot.register_next_step_handler(message, get_sizes)

def get_sizes(message):
    user_data[message.chat.id]['sizes'] = message.text
    # عرض المعاينة النهائية للمدير قبل النشر
    data = user_data[message.chat.id]
    preview = (f"🔍 **معاينة المنشور قبل النشر في القناة:**\n\n"
               f"📦 المنتج: {data['name']}\n"
               f"💰 السعر: {data['price']} ج.م\n"
               f"📏 المقاسات: {data['sizes']}")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد ونشر الآن", callback_data="publish"),
               types.InlineKeyboardButton("✏️ تعديل الصورة", callback_data="edit_p"))
    markup.add(types.InlineKeyboardButton("✏️ تعديل النص", callback_data="edit_t"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel"))
    
    bot.send_photo(message.chat.id, data['photo'], caption=preview, reply_markup=markup)

# --- 3. معالجة الأزرار التفاعلية والنشر ---
@bot.callback_query_handler(func=lambda call: True)
def callback_logic(call):
    if call.data == "publish":
        data = user_data.get(call.message.chat.id)
        if data:
            # إنشاء أزرار المقاسات للعميل في القناة
            markup = types.InlineKeyboardMarkup(row_width=3)
            sizes = data['sizes'].split(',')
            size_btns = [types.InlineKeyboardButton(f"🛒 مقاس {s.strip()}", callback_data=f"buy_{s.strip()}_{data['name']}") for s in sizes]
            markup.add(*size_btns)
            # أزرار الخدمات
            markup.add(types.InlineKeyboardButton("💬 استفسار", url="https://t.me/RamySamir2026"),
                       types.InlineKeyboardButton("🏪 المعرض", url="https://ramisamir2006-hash.github.io"))
            
            caption = f"✨ **{data['name']}**\n\n💰 السعر: {data['price']} ج.م\n\nاطلبي الآن عبر اختيار المقاس المناسب 👇"
            bot.send_photo(CHANNEL_ID, data['photo'], caption=caption, reply_markup=markup, parse_mode="Markdown")
            bot.send_message(call.message.chat.id, "🚀 تم النشر في القناة بنجاح!")

    elif call.data.startswith("buy_"):
        # إرسال تفاصيل طلب العميل لجروب الموظفين
        info = call.data.split("_")
        order_details = f"🔔 **طلب جديد:**\n👤 العميل: @{call.from_user.username}\n🛍️ المنتج: {info[2]}\n📏 المقاس: {info[1]}"
        bot.send_message(STAFF_GROUP_ID, order_details)
        bot.answer_callback_query(call.id, "✅ تم إرسال طلبك لفريق خدمة العملاء.")

# --- تشغيل البوت والسيرفر لـ Koyeb ---
if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    
