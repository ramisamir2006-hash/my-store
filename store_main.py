import telebot
from telebot import types
import sqlite3
from flask import Flask
import threading  
import os
import time


# ==========================================
# 1. إعدادات الهوية (رامي سمير)
# ==========================================
TOKEN = '8212982429:AAFL_IVxbBfmPFm1ymq67nKYMpR59VTt7as'
ADMIN_ID = 7020070481
MY_CHANNEL = '@RamySamir2026Gold'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# ==========================================
# 2. نظام قاعدة البيانات (مفصل وممل)
# ==========================================
def full_database_initialization():
    connection = sqlite3.connect('ramy_gold_ultimate_fixed.db', check_same_thread=False)
    cursor = connection.cursor()
    
    # جدول المنتجات الكامل
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        category TEXT, 
        wholesale_price REAL, 
        online_price REAL, 
        retail_price REAL, 
        media_file_id TEXT, 
        media_file_type TEXT
    )""")
    
    # جدول تسجيل العملاء للإعلانات الخارجية
    cursor.execute("CREATE TABLE IF NOT EXISTS all_clients (client_id INTEGER PRIMARY KEY)")
    
    # جدول رتب العملاء (أسعار مخصصة)
    cursor.execute("CREATE TABLE IF NOT EXISTS client_roles (user_id INTEGER PRIMARY KEY, role_type TEXT DEFAULT 'online')")
    
    # جدول سلة التسوق
    cursor.execute("CREATE TABLE IF NOT EXISTS user_cart (uid INTEGER, pid INTEGER)")
    
    # جدول إعدادات النظام (النشر التلقائي)
    cursor.execute("CREATE TABLE IF NOT EXISTS bot_settings (key_name TEXT PRIMARY KEY, val_status TEXT)")
    cursor.execute("INSERT OR IGNORE INTO bot_settings (key_name, val_status) VALUES ('auto_post_config', 'ON')")
    
    connection.commit()
    return connection

db_connection = full_database_initialization()

# مخازن البيانات المؤقتة
temp_admin_data = {}
temp_broadcast_data = {}
temp_order_data = {}

# ==========================================
# 1. معالج ضغطات أزرار لوحة التحكم
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("btn_"))
def handle_admin_dashboard(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ عذراً، هذه اللوحة للمدير فقط.")
        return

    # --- إضافة منتج (صورة أو فيديو) ---
    if call.data in ["btn_add_photo", "btn_add_video"]:
        temp_admin_data[call.from_user.id] = {'media_type': 'photo' if "photo" in call.data else 'video'}
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "📍 أرسل اسم المنتج الجديد:")
        bot.register_next_step_handler(msg, process_step_wholesale)

    # --- تبديل حالة النشر التلقائي ---
    elif call.data == "btn_toggle_post":
        cursor = db_connection.cursor()
        cursor.execute("SELECT val_status FROM bot_settings WHERE key_name='auto_post_config'")
        current = cursor.fetchone()[0]
        new_status = "OFF" if current == "ON" else "ON"
        cursor.execute("UPDATE bot_settings SET val_status=? WHERE key_name='auto_post_config'", (new_status,))
        db_connection.commit()
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=build_admin_dashboard_keyboard())
        bot.answer_callback_query(call.id, f"🔄 تم تغيير حالة النشر إلى: {new_status}")

    # --- جرد وتعديل المتجر ---
    elif call.data == "btn_inventory":
        bot.answer_callback_query(call.id, "📦 جاري تحميل المخزن...")
        show_inventory_list(call.message)

    # --- إحصائيات القناة والبوت ---
    elif call.data == "btn_stats":
        cursor = db_connection.cursor()
        users_count = cursor.execute("SELECT COUNT(*) FROM all_clients").fetchone()[0]
        prods_count = cursor.execute("SELECT COUNT(*) FROM products_table").fetchone()[0]
        stats_text = f"📊 **إحصائيات متجر رامي سمير:**\n\n👥 عدد المستخدمين: {users_count}\n📦 عدد المنتجات: {prods_count}"
        bot.send_message(call.message.chat.id, stats_text)
        bot.answer_callback_query(call.id)

    # --- تحديث النظام ---
    elif call.data == "btn_update_system":
        bot.answer_callback_query(call.id, "⚙️ يتم الآن تحديث قواعد البيانات...")
        full_database_initialization()
        bot.send_message(call.message.chat.id, "✅ النظام مستقر وتم تحديث كافة قواعد البيانات.")

    # --- إدارة رتب الأسعار ---
    elif call.data == "btn_roles":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, "🆔 أرسل ID العميل الذي تريد تغيير رتبته:")
        bot.register_next_step_handler(msg, process_role_change)

    # --- الإعلانات (داخلي/خارجي) ---
    elif call.data in ["btn_ad_internal", "btn_ad_external"]:
        target = "البوت" if "internal" in call.data else "القناة"
        bot.answer_callback_query(call.id)
        msg = bot.send_message(call.message.chat.id, f"📢 أرسل نص الإعلان الموجه لـ {target}:")
        if "internal" in call.data:
            bot.register_next_step_handler(msg, send_internal_ad)
        else:
            bot.register_next_step_handler(msg, send_external_channel_ad)

# ==========================================
# 1. معالج الأزرار (لوحة التحكم) - الربط الفعلي
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    uid = call.from_user.id
    
    # التحقق من أن المستخدم هو رامي (الأدمن) للأزرار الحساسة
    if uid == ADMIN_ID:
        if call.data == "btn_add_photo":
            temp_admin_data[uid] = {'media_type': 'photo'}
            msg = bot.send_message(call.message.chat.id, "📍 أرسل اسم المنتج الجديد:")
            bot.register_next_step_handler(msg, process_step_wholesale)
            bot.answer_callback_query(call.id)

        elif call.data == "btn_add_video":
            temp_admin_data[uid] = {'media_type': 'video'}
            msg = bot.send_message(call.message.chat.id, "📍 أرسل اسم المنتج الجديد:")
            bot.register_next_step_handler(msg, process_step_wholesale)
            bot.answer_callback_query(call.id)

        elif call.data == "btn_inventory":
            bot.answer_callback_query(call.id, "📦 جاري فتح المخزن...")
            # استدعاء دالة الجرد
            show_inventory_to_admin(call.message)

        elif call.data == "btn_stats":
            cursor = db_connection.cursor()
            u_count = cursor.execute("SELECT COUNT(*) FROM all_clients").fetchone()[0]
            p_count = cursor.execute("SELECT COUNT(*) FROM products_table").fetchone()[0]
            bot.send_message(call.message.chat.id, f"📊 إحصائياتك الحالية:\n👥 عملاء: {u_count}\n📦 منتجات: {p_count}")
            bot.answer_callback_query(call.id)

        elif call.data == "btn_toggle_post":
            cursor = db_connection.cursor()
            cursor.execute("SELECT val_status FROM bot_settings WHERE key_name='auto_post_config'")
            current = cursor.fetchone()[0]
            new_status = "OFF" if current == "ON" else "ON"
            cursor.execute("UPDATE bot_settings SET val_status=? WHERE key_name='auto_post_config'", (new_status,))
            db_connection.commit()
            # تحديث لوحة التحكم لتظهر الحالة الجديدة
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=build_admin_dashboard_keyboard())
            bot.answer_callback_query(call.id, f"🔄 النشر التلقائي الآن: {new_status}")

    # --- أزرار العملاء (سلة المشتريات والاستفسار) ---
    if call.data.startswith("client_add_cart_"):
        pid = call.data.split("_")[3]
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO user_cart (uid, pid) VALUES (?, ?)", (uid, pid))
        db_connection.commit()
        bot.answer_callback_query(call.id, "✅ تم الإضافة للسلة!", show_alert=False)

    elif call.data == "client_view_cart":
        # كود عرض السلة للعميل
        show_user_cart(call.message)
        bot.answer_callback_query(call.id)

# ==========================================
# 2. دالة الجرد (المخزن)
# ==========================================
def show_inventory_to_admin(message):
    cursor = db_connection.cursor()
    products = cursor.execute("SELECT id, name, online_price FROM products_table ORDER BY id DESC LIMIT 10").fetchall()
    if not products:
        bot.send_message(message.chat.id, "المخزن فارغ.")
        return
    for p in products:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❌ حذف", callback_data=f"del_prod_{p[0]}"))
        bot.send_message(message.chat.id, f"📦 المنتج: {p[1]}\n💰 السعر: {p[2]} ج.م", reply_markup=kb)

# ==========================================
# 3. معالج الحذف (من الجرد)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("del_prod_"))
def delete_product_process(call):
    pid = call.data.split("_")[2]
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM products_table WHERE id=?", (pid,))
    db_connection.commit()
    bot.answer_callback_query(call.id, "تم الحذف بنجاح")
    bot.delete_message(call.message.chat.id, call.message.message_id)


# ==========================================
# 4. واجهة أزرار العميل (الرئيسية مع الإضافات المطلوبة)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("client_"))
def handle_client_actions(call):
    uid = call.from_user.id
    
    # 1. زر إضافة منتج للسلة
    if call.data.startswith("client_add_cart_"):
        product_id = call.data.split("_")[3]
        cursor = db_connection.cursor()
        cursor.execute("INSERT INTO user_cart (uid, pid) VALUES (?, ?)", (uid, product_id))
        db_connection.commit()
        bot.answer_callback_query(call.id, "✅ تم إضافة المنتج لسلتك بنجاح!", show_alert=True)

    # 2. زر عرض السلة
    elif call.data == "client_view_cart":
        cursor = db_connection.cursor()
        cursor.execute("""SELECT p.name, p.online_price FROM user_cart c 
                       JOIN products_table p ON c.pid = p.id WHERE c.uid = ?""", (uid,))
        items = cursor.fetchall()
        if not items:
            bot.send_message(uid, "🛒 سلتك فارغة حالياً.")
        else:
            msg = "🛒 **محتويات سلتك:**\n\n"
            total = 0
            for i in items:
                msg += f"- {i[0]} : {i[1]} ج.م\n"
                total += i[1]
            bot.send_message(uid, f"{msg}\n💰 **الإجمالي:** {total} ج.م")
        bot.answer_callback_query(call.id)

    # 3. زر الاستفسار (يرسل رسالة للأدمن)
    elif call.data == "client_help":
        bot.answer_callback_query(call.id, "سيتم تحويلك لمحادثة الإدارة.")
        bot.send_message(uid, "💬 أرسل استفسارك الآن وسيرد عليك رامي سمير في أقرب وقت.")
        # إشعار للأدمن
        bot.send_message(ADMIN_ID, f"🔔 هناك عميل جديد (@{call.from_user.username}) يستفسر عن منتج في القناة.")



#def process_add_step_final_save(message):
# ==========================================
# 5. الجزء الخاص بعملية الحفظ والنشر التلقائي
# ==========================================

#def final_save_and_post(message):
    uid = message.from_user.id

    data = temp_admin_data.get(uid)
    if not data: return

    # استخراج ملف الميديا (صورة أو فيديو)
    file_id = message.photo[-1].file_id if message.photo else (message.video.file_id if message.video else None)
    
    if not file_id:
        bot.send_message(message.chat.id, "❌ خطأ: لم يتم التعرف على الصورة أو الفيديو.")
        return

    # 1. الحفظ في قاعدة البيانات أولاً
    cursor = db_connection.cursor()
    cursor.execute("""INSERT INTO products_table 
        (name, category, wholesale_price, online_price, retail_price, media_file_id, media_file_type) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""", 
        (data['name'], data['cat'], data['wholesale'], data['online'], data['retail'], file_id, data['media_type']))
    db_connection.commit()
    product_id = cursor.lastrowid # جلب رقم المنتج لربطه بالأزرار

    # 2. عملية النشر التلقائي في القناة (MY_CHANNEL)
    cursor.execute("SELECT val_status FROM bot_settings WHERE key_name='auto_post_config'")
    auto_status = cursor.fetchone()
    
    if auto_status and auto_status[0] == "ON":
        try:
            # تصميم الأزرار الملحقة بالمنشور في القناة
            channel_kb = types.InlineKeyboardMarkup(row_width=2)
            btn_cart = types.InlineKeyboardButton("🛒 إضافة للسلة", callback_data=f"client_add_cart_{product_id}")
            btn_store = types.InlineKeyboardButton("🏥 فتح المتجر", url=f"https://t.me/{bot.get_me().username}")
            btn_help = types.InlineKeyboardButton("💬 استفسار / مساعدة", callback_data="client_help")
            btn_view_cart = types.InlineKeyboardButton("📋 عرض السلة", callback_data="client_view_cart")
            
            channel_kb.add(btn_cart, btn_store)
            channel_kb.add(btn_help, btn_view_cart)

            # نص المنشور
            caption = f"💎 **{data['name']}**\n📂 القسم: {data['cat']}\n💰 السعر: {data['online']} ج.م\n\n🚚 متاح الشحن لكافة المحافظات"

            # إرسال المنشور فعلياً للقناة
            if data['media_type'] == 'photo':
                bot.send_photo(MY_CHANNEL, file_id, caption=caption, reply_markup=channel_kb)
            else:
                bot.send_video(MY_CHANNEL, file_id, caption=caption, reply_markup=channel_kb)
                
            bot.send_message(message.chat.id, "✅ تم الحفظ ونشر المنتج في القناة بنجاح!")
            
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ تم الحفظ ولكن فشل النشر التلقائي.\nالسبب: تأكد أن البوت مشرف في القناة.\nالخطأ: {e}")
    else:
        bot.send_message(message.chat.id, "✅ تم حفظ المنتج في البوت (النشر التلقائي مغلق).")

    # العودة للوحة التحكم
    bot.send_message(message.chat.id, "👑 لوحة التحكم:", reply_markup=build_admin_dashboard_keyboard())
    
# ==========================================
# 6. نظام الإعلانات (داخلي / خارجي)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "btn_ad_internal")
def ad_internal_start(call):
    msg = bot.send_message(call.message.chat.id, "📢 أرسل نص الإعلان الداخلي (لمستخدمي البوت):")
    bot.register_next_step_handler(msg, ad_internal_execute)

def ad_internal_execute(message):
    cursor = db_connection.cursor()
    users = cursor.execute("SELECT client_id FROM all_clients").fetchall()
    count = 0
    for u in users:
        try:
            bot.send_message(u[0], f"🚨 **رسالة من الإدارة:**\n\n{message.text}")
            count += 1
        except: continue
    bot.send_message(ADMIN_ID, f"✅ تم إرسال الإعلان الداخلي لـ {count} مستخدم.")

@bot.callback_query_handler(func=lambda call: call.data == "btn_ad_external")
def ad_external_start(call):
    msg = bot.send_message(call.message.chat.id, "📢 أرسل النص الذي تريد نشره في القناة مباشرة:")
    bot.register_next_step_handler(msg, ad_external_execute)

def ad_external_execute(message):
    bot.send_message(MY_CHANNEL, message.text)
    bot.send_message(ADMIN_ID, "✅ تم النشر في القناة بنجاح.")

# ==========================================
# 7. نظام الإحصائيات (Stats)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "btn_stats")
def show_full_statistics(call):
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM all_clients")
    bot_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products_table")
    prods_total = cursor.fetchone()[0]
    
    stats_text = (f"📊 **إحصائيات متجر رامي سمير:**\n\n"
                  f"👥 مستخدمي البوت: {bot_users} شخص\n"
                  f"📦 إجمالي المنتجات: {prods_total} منتج\n"
                  f"📢 القناة: {MY_CHANNEL}\n"
                  f"🕒 التوقيت: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    bot.send_message(call.message.chat.id, stats_text, reply_markup=build_admin_dashboard_keyboard())

# ==========================================
# 8. نظام الجرد والتعديل (معدل ليعرض الصور كما في الصورة)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "btn_inventory")
def show_inventory_list(call):
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM products_table")
    all_items = cursor.fetchall()
    
    if not all_items:
        bot.send_message(call.message.chat.id, "المخزن فارغ.")
        return

    for item in all_items:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("❌ حذف المنتج", callback_data=f"delete_id_{item[0]}"))
        caption = f"📦 المنتج: {item[1]}\n💰 السعر: {item[4]}"
        
        if item[7] == 'photo':
            bot.send_photo(call.message.chat.id, item[6], caption=caption, reply_markup=kb)
        else:
            bot.send_video(call.message.chat.id, item[6], caption=caption, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_id_"))
def execute_product_deletion(call):
    target_id = call.data.split("_")[2]
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM products_table WHERE id=?", (target_id,))
    db_connection.commit()
    bot.answer_callback_query(call.id, "تم الحذف من المتجر")
    bot.delete_message(call.message.chat.id, call.message.message_id)

# ==========================================
# 9. زر النشر التلقائي والعرض الترويجي
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "btn_toggle_post")
def toggle_auto_post_status(call):
    cursor = db_connection.cursor()
    cursor.execute("SELECT val_status FROM bot_settings WHERE key_name='auto_post_config'")
    current = cursor.fetchone()[0]
    new_status = "OFF" if current == "ON" else "ON"
    cursor.execute("UPDATE bot_settings SET val_status=? WHERE key_name='auto_post_config'", (new_status,))
    db_connection.commit()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=build_admin_dashboard_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "btn_promo")
def promo_message_start(call):
    msg = bot.send_message(call.message.chat.id, "🔥 أرسل نص العرض الترويجي القوي:")
    bot.register_next_step_handler(msg, promo_message_execute)

def promo_message_execute(message):
    promo_msg = f"🌟 **عرض ترويجي من متجرنا!** 🌟\n\n{message.text}"
    bot.send_message(MY_CHANNEL, promo_msg)
    
    cursor = db_connection.cursor()
    users = cursor.execute("SELECT client_id FROM all_clients").fetchall()
    for u in users:
        try: bot.send_message(u[0], promo_msg)
        except: continue
    bot.send_message(ADMIN_ID, "✅ تم نشر العرض الترويجي بنجاح.")

# ==========================================
# 10. نظام رتب العملاء (الأسعار المخصصة)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "btn_roles")
def manage_roles_get_client_id(call):
    msg = bot.send_message(call.message.chat.id, "🆔 أرسل رقم (ID) العميل لتغيير فئة سعره:")
    bot.register_next_step_handler(msg, manage_roles_show_options)

def manage_roles_show_options(message):
    target_id = message.text
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("تاجر جملة", callback_data=f"set_role_{target_id}_wholesale"))
    kb.add(types.InlineKeyboardButton("عميل أونلاين", callback_data=f"set_role_{target_id}_online"))
    kb.add(types.InlineKeyboardButton("عميل محل", callback_data=f"set_role_{target_id}_retail"))
    bot.send_message(message.chat.id, f"اختر نوع السعر للعميل {target_id}:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_role_"))
def manage_roles_save_final(call):
    parts = call.data.split("_")
    cid = parts[2]
    rtype = parts[3]
    cursor = db_connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO client_roles (user_id, role_type) VALUES (?, ?)", (cid, rtype))
    db_connection.commit()
    bot.send_
