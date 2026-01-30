import telebot
from telebot import types
import json
from datetime import datetime

# --- إعدادات الربط الأساسية ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
CHANNEL_ID = "@RamySamir2026Gold" 
ADMIN_ID = 7020070481             # رامي سمير (المدير العام)

# قائمة الموظفين (يتم تخزين معرفات الموظفين هنا)
staff_list = [] 

bot = telebot.TeleBot(TOKEN)

# --- 1. لوحات التحكم (Reply Keyboards) ---

def admin_keyboard():
    """لوحة المدير العام (رامي)"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        types.KeyboardButton("📊 التقارير اليومية"),
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("👥 الموظفين (إضافة/حذف)"),
        types.KeyboardButton("➕ إضافة منتج جديد"),
        types.KeyboardButton("💰 ضبط الخصومات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    ]
    markup.add(*btns)
    return markup

def staff_keyboard():
    """لوحة الموظفين المسؤولين"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("💬 الاستفسارات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    ]
    markup.add(*btns)
    return markup

def user_keyboard():
    """لوحة الزبائن العامة"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🛍️ دخول المتجر"),
        types.KeyboardButton("📞 الدعم الفني")
    )
    return markup

# --- 2. الأوامر الأساسية (Start) ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً يا رامي! لوحة الإدارة العامة جاهزة للعمل..", reply_markup=admin_keyboard())
    elif user_id in staff_list:
        bot.send_message(message.chat.id, "أهلاً بك (موظف مسؤول). لوحة مهامك المخصصة جاهزة.", reply_markup=staff_keyboard())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في مجوهرات رامي سمير ✨\nتفضل بتصفح أحدث الموديلات.", reply_markup=user_keyboard())

# --- 3. نظام إدارة الموظفين (حصري للمدير) ---

@bot.message_handler(func=lambda message: message.text == "👥 الموظفين (إضافة/حذف)")
def manage_staff(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة موظف جديد", callback_data="add_staff"))
    markup.add(types.InlineKeyboardButton("➖ حذف موظف حالي", callback_data="del_staff"))
    markup.add(types.InlineKeyboardButton("📜 قائمة الموظفين", callback_data="list_staff"))
    
    bot.send_message(ADMIN_ID, "إدارة طاقم العمل والمسؤولين:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["add_staff", "del_staff", "list_staff"])
def staff_callbacks(call):
    if call.data == "add_staff":
        msg = bot.send_message(ADMIN_ID, "أرسل الآن ID الموظف الجديد (أرقام فقط):")
        bot.register_next_step_handler(msg, process_add_staff)
    elif call.data == "del_staff":
        msg = bot.send_message(ADMIN_ID, "أرسل ID الموظف الذي تريد حذفه:")
        bot.register_next_step_handler(msg, process_del_staff)
    elif call.data == "list_staff":
        staff_str = "\n".join([f"• {s}" for s in staff_list]) if staff_list else "لا يوجد موظفين حالياً."
        bot.send_message(ADMIN_ID, f"قائمة المسؤولين الحاليين:\n{staff_str}")

def process_add_staff(message):
    try:
        new_id = int(message.text)
        if new_id not in staff_list:
            staff_list.append(new_id)
            bot.send_message(ADMIN_ID, f"✅ تم إضافة {new_id} لقائمة الموظفين.")
        else:
            bot.send_message(ADMIN_ID, "هذا الشخص مضاف بالفعل.")
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ! يرجى إرسال أرقام الـ ID فقط.")

def process_del_staff(message):
    try:
        target_id = int(message.text)
        if target_id in staff_list:
            staff_list.remove(target_id)
            bot.send_message(ADMIN_ID, f"❌ تم حذف الموظف {target_id}.")
        else:
            bot.send_message(ADMIN_ID, "المعرف غير موجود.")
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ في الإدخال.")

# --- 4. معالجة بيانات المتجر (النشر والطلبات) ---

@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID and user_id not in staff_list: return

    try:
        data = json.loads(message.web_app_data.data)
        
        # نشر منتج جديد
        if data.get("action") == "publish":
            publish_to_channel(data)
            bot.reply_to(message, "✅ تم النشر بنجاح في القناة.")

        # استقبال أوردر جديد
        elif data.get("action") == "order":
            send_order_to_team(data)
            bot.reply_to(message, "✅ تم إرسال طلبك للإدارة.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطأ: {str(e)}")

# --- 5. وظائف التشغيل ---

def publish_to_channel(p):
    """تنسيق وإرسال المنتج للقناة (دعم 10 صور)"""
    caption = (
        f"✨ **{p['name']}** ✨\n\n"
        f"📝 {p['desc']}\n\n"
        f"📏 المقاسات: {p['sizes']}\n"
        f"💰 السعر: {p['price']} ج.م\n"
        f"🏷 القسم: #{p.get('cat', 'مجوهرات')}\n\n"
        "🔥 اطلبيها الآن قبل نفاذ الكمية!"
    )
    media = []
    for i, url in enumerate(p['imgs']):
        if i == 0: media.append(types.InputMediaPhoto(url, caption=caption, parse_mode="Markdown"))
        else: media.append(types.InputMediaPhoto(url))
    
    if media:
        bot.send_media_group(CHANNEL_ID, media)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 اطلب المنتج الآن", url=f"https://t.me/{bot.get_me().username}/app"))
        bot.send_message(CHANNEL_ID, "للحجز أو الاستفسار اضغط هنا 👇", reply_markup=markup)

def send_order_to_team(order):
    """توزيع الطلبات على المدير والموظفين"""
    msg = (
        f"🚨 **أوردر جديد!**\n\n"
        f"👤 العميل: {order['customer']}\n"
        f"📞 الهاتف: {order['phone']}\n"
        f"📍 العنوان: {order['address']}\n"
        f"🚚 النوع: {order.get('type', 'شحن')}\n"
        f"--------------------------\n"
        f"📦 المنتجات:\n"
    )
    for item in order['items']:
        msg += f"- {item['name']} (مقاس: {item['selectedSize']})\n"
    msg += f"\n💰 الإجمالي: {order['total']} ج.م"
    
    bot.send_message(ADMIN_ID, msg)
    for s_id in staff_list:
        try: bot.send_message(s_id, msg)
        except: pass

# --- 6. معالجة الأزرار النصية ---

@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == "📊 التقارير اليومية":
            bot.send_message(ADMIN_ID, "📈 تقرير اليوم: الأداء مستقر والحمد لله.")
    
    if message.text == "📞 الدعم الفني":
        bot.send_message(message.chat.id, "أهلاً بك.. ارسل استفسارك وسيرد عليك أحد المسؤولين.")

# --- بدء التشغيل النهائي ---
print("✅ النظام مدمج وشغال بالكامل...")
bot.polling(none_stop=True)
    
