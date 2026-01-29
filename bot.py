import telebot
from telebot import types
import json
from datetime import datetime, timedelta

# بيانات البوت والقناة
TOKEN = 'TOKEN_BOT_HERE' # ضع توكن بوتك هنا
CHANNEL_ID = '@RamySamir2026Gold' # معرف قناتك
ADMIN_ID = 7020070481 # الـ ID الخاص بك

bot = telebot.TeleBot(TOKEN)

# قواعد بيانات بسيطة (يمكن استبدالها بـ SQLite لاحقاً)
db = {"products": [], "orders": [], "banned_users": [], "customers": {}}

# 1. لوحة تحكم المدير (أوامر الحظر والتقارير)
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 تقرير اليوم", callback_data="rep_day"))
    markup.add(types.InlineKeyboardButton("📅 تقرير الأسبوعين", callback_data="rep_2weeks"))
    markup.add(types.InlineKeyboardButton("🚫 إدارة المحظورين", callback_data="manage_bans"))
    bot.send_message(message.chat.id, "مرحباً يا أستاذ رامي.. اختر الإجراء المطلوب:", reply_markup=markup)

# 2. استقبال البيانات من المتجر (الأوردرات والنشر)
@bot.message_handler(content_types=['web_app_data'])
def handle_webapp_data(message):
    data = json.loads(message.web_app_data.data)
    
    # إذا كانت البيانات أوردر جديد
    if "items" in data:
        order_id = len(db["orders"]) + 1
        db["orders"].append(data)
        
        # إشعار للمدير بالأوردر الجديد
        msg = f"🔔 أوردر جديد رقم #{order_id}\n"
        msg += f"👤 العميل: {data['customer']}\n"
        msg += f"📞 الهاتف: {data['phone']}\n"
        msg += f"📍 العنوان: {data['address']}\n"
        msg += f"🚚 النوع: {'شحن' if data['type']=='delivery' else 'استلام من المحل'}\n"
        msg += f"⏰ الموعد: {data['time']}\n"
        msg += f"💰 الإجمالي: {data['total']} ج.م"
        
        bot.send_message(ADMIN_ID, msg)
        bot.send_message(message.chat.id, "✅ تم استلام طلبك بنجاح! سيتم التواصل معك قريباً.")

# 3. وظيفة النشر التلقائي في القناة
def publish_to_channel(product):
    caption = f"✨ {product['name']}\n"
    caption += f"🗂 القسم: {product['cat']}\n"
    caption += f"📏 المقاسات: {product['sizes']}\n"
    caption += f"💰 السعر: {product['price']} ج.م\n\n"
    caption += "🛒 للطلب، افتح متجرنا الآن!"
    
    # إضافة أزرار شفافة تحت المنشور في القناة
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛍 تسوق الآن", url="https://t.me/YourBotName/app"))
    
    bot.send_message(CHANNEL_ID, caption, reply_markup=markup)

# 4. نظام الحظر (تلقائي)
@bot.message_handler(func=lambda m: m.from_user.id in db["banned_users"])
def check_ban(message):
    bot.send_message(message.chat.id, "❌ عذراً، لقد تم حظرك من استخدام هذا المتجر.")

# 5. تقارير المبيعات (كل أسبوعين ويومياً)
@bot.callback_query_handler(func=lambda call: call.data.startswith("rep_"))
def reports(call):
    now = datetime.now()
    if call.data == "rep_day":
        # تصفية أوردرات اليوم وحساب الإجمالي
        bot.answer_callback_query(call.id, "جاري استخراج تقرير اليوم...")
        # (هنا تضع منطق الحساب البرمجي)
    
    elif call.data == "rep_2weeks":
        limit = now - timedelta(days=14)
        bot.answer_callback_query(call.id, "جاري استخراج تقرير الأسبوعين الماضيين...")

bot.polling()
        
