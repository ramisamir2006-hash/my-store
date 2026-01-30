import telebot
from telebot import types
import json
from datetime import datetime

# --- إعدادات الربط النهائية ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
CHANNEL_ID = "@RamySamir2026Gold"  # معرف قناتك
ADMIN_ID = 7020070481             # رامي سمير (المدير العام)

# قائمة الموظفين (يتم تخزين IDs الموظفين المسموح لهم بالعمل هنا)
staff_list = [] 

bot = telebot.TeleBot(TOKEN)

# --- 1. لوحات التحكم السفلية (Reply Keyboards) ---

def admin_keyboard():
    """لوحة المدير العام (رامي) - تشمل إدارة الموظفين والتقارير"""
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
    """لوحة الموظفين - مهام محددة للمساعدة في العمل"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [
        types.KeyboardButton("📦 إدارة الطلبات"),
        types.KeyboardButton("💬 الاستفسارات"),
        types.KeyboardButton("🛍️ فتح المتجر")
    ]
    markup.add(*btns)
    return markup

def user_keyboard():
    """لوحة الزبائن العادية"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🛍️ دخول المتجر"),
        types.KeyboardButton("📞 الدعم الفني")
    )
    return markup

# --- 2. الأوامر الأساسية ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "أهلاً يا رامي! لوحة الإدارة العامة جاهزة للعمل..", reply_markup=admin_keyboard())
    elif user_id in staff_list:
        bot.send_message(message.chat.id, "أهلاً بك (موظف مسؤول). لوحة مهامك المخصصة جاهزة.", reply_markup=staff_keyboard())
    else:
        bot.send_message(message.chat.id, "مرحباً بك في مجوهرات رامي سمير ✨\nتفضل بتصفح أحدث الموديلات.", reply_markup=user_keyboard())

# --- 3. إدارة الموظفين (صلاحية حصرية لرامي فقط) ---

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
        msg = bot.send_message(ADMIN_ID, "أرسل الآن ID الموظف الجديد (يمكنه الحصول عليه من @userinfobot):")
        bot.register_next_step_handler(msg, process_add_staff)
    elif call.data == "del_staff":
        msg = bot.send_message(ADMIN_ID, "أرسل ID الموظف الذي تريد سحب الصلاحيات منه:")
        bot.register_next_step_handler(msg, process_del_staff)
    elif call.data == "list_staff":
        staff_str = "\n".join([f"• {s}" for s in staff_list]) if staff_list else "لا يوجد موظفين حالياً."
        bot.send_message(ADMIN_ID, f"قائمة المسؤولين الحاليين:\n{staff_str}")

def process_add_staff(message):
    try:
        new_id = int(message.text)
        if new_id not in staff_list:
            staff_list.append(new_id)
            bot.send_message(ADMIN_ID, f"✅ تم منح صلاحيات الموظف لـ {new_id} بنجاح.")
        else:
            bot.send_message(ADMIN_ID, "هذا الشخص مضاف بالفعل كمسؤول.")
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ! يرجى إرسال أرقام الـ ID فقط.")

def process_del_staff(message):
    try:
        target_id = int(message.text)
        if target_id in staff_list:
            staff_list.remove(target_id)
            bot.send_message(ADMIN_ID, f"❌ تم حذف الموظف {target_id} وسحب صلاحياته.")
        else:
            bot.send_message(ADMIN_ID, "هذا المعرف غير موجود في القائمة.")
    except:
        bot.send_message(ADMIN_ID, "❌ خطأ في الإدخال.")

# --- 4. معالجة بيانات المتجر (النشر والطلبات) ---

@bot.message_handler(content_types=['web_app_data'])
def handle_app_data(message):
    user_id = message.from_user.id
    # التحقق من الصلاحية (رامي أو موظف)
    if user_id != ADMIN_ID and user_id not in staff_list:
        return

    try:
        data = json.loads(message.web_app_data.data)
        
        # أ- نشر منتج جديد (دعم 10 صور وأزرار)
        if data.get("action") == "publish":
            publish_to_channel(data)
            bot.reply_to(message, "✅ تم النشر في القناة بنجاح وتنسيق المنشور.")

        # ب- استقبال أوردر جديد
        elif data.get("action") == "order":
            send_order_to_team(data)
            bot.reply_to(message, "✅ تم إرسال طلبك للإدارة، سيتم التواصل معك قريباً.")

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ خطأ في معالجة البيانات: {str(e)}")

# --- 5. وظائف التشغيل الفنية ---

def publish_to_channel(p):
    """تنسيق المنشور بـ 10 صور وإرساله للقناة"""
    caption = (
        f"✨ **{p['name']}** ✨\n\n"
        f"📝 {p['desc']}\n\n"
        f"📏 المقاسات: {p['sizes']}\n"
        f"💰 السعر: {p['price']} ج.م\n"
        f"🏷 القسم: #{p.get('cat', 'مجوهرات')}\n\n"
        "🔥 قطعة فريدة تليق بجمالك.. اطلبيها الآن!"
    )

    media = []
    for i, url in enumerate(p['imgs']):
        if i == 0:
            media.append(types.InputMediaPhoto(url, caption=caption, parse_mode="Markdown"))
        else:
            media.append(types.InputMediaPhoto(url))

    if media:
        bot.send_media_group(CHANNEL_ID, media)
        # إضافة زر الشراء تحت الألبوم
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 اطلب المنتج الآن", url=f"https://t.me/{bot.get_me().username}/app"))
        bot.send_message(CHANNEL_ID, "للحجز أو الاستفسار اضغط على الزر 👇", reply_markup=markup)

def send_order_to_team(order):
    """إرسال تفاصيل الأوردر لرامي ولكل الموظفين"""
    msg = (
        f"🚨 **أوردر جديد!**\n\n"
        f"👤 العميل: {order['customer']}\n"
        f"📞 الهاتف: {order['phone']}\n"
        f"📍 العنوان: {order['address']}\n"
        f"🚚 النوع: {order.get('type', 'شحن')}\n"
        f"--------------------------\n"
        f"📦 المنتجات المطلوبة:\n"
    )
    for item in order['items']:
        msg += f"- {item['name']} (مقاس: {item['selectedSize']})\n"
    
    msg += f"\n💰 الإجمالي: {order['total']} ج.م"
    
    # إرسال للمدير العام
    bot.send_message(ADMIN_ID, msg)
    # إرسال للموظفين
    for staff_id in staff_list:
        try: bot.send_message(staff_id, msg)
        except: pass

# --- الرد على أزرار التقارير والدعم ---
@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    if message.from_user.id == ADMIN_ID:
        if message.text == "📊 التقارير اليومية":
            bot.send_message(ADMIN_ID, "📈 تقرير اليوم: الأداء مستقر (سيتم ربط المبيعات الفعلية قريباً).")
    
    if message.text == "📞 الدعم الفني":
        bot.send_message(message.chat.id, "أهلاً بك.. ارسل استفسارك الآن وسيقوم أحد المسؤولين بالرد عليك.")

# --- بدء التشغيل ---
print("✅ تم الدمج بنجاح.. البوت يعمل الآن بنظام الموظفين والنشر المتطور.")
bot.polling(none_stop=True)
