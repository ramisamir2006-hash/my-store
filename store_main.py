import json
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# 1. ضع التوكن الخاص بك هنا
TOKEN = "8557404137:AAHB30k_Hzj9Chh_-MEQpa3NhCpQaZfJtSM"

# 2. إعدادات الملفات (لضمان عدم حدوث خطأ عند التشغيل)
def init_db():
    files = ["produk.json", "saldo.json", "pending_deposit.json", "riwayat.json", "statistik.json"]
    for f in files:
        if not os.path.exists(f):
            with open(f, "w") as file: json.dump({}, file)

# --- (هنا تضع دوال البوت التي أرسلتها أنت: handle_list_produk, send_main_menu... إلخ) ---

# 3. الجزء المسؤول عن ربط التوكن وتشغيل البوت (ضعه في نهاية الملف)
def main():
    init_db() # إنشاء الملفات تلقائياً
    
    # بناء البوت باستخدام التوكن الخاص بك
    app = Application.builder().token(TOKEN).build()

    # ربط الأوامر (Handlers)
    app.add_handler(CommandHandler("start", send_main_menu_safe))
    app.add_handler(CallbackQueryHandler(handle_list_produk, pattern="list_produk"))
    app.add_handler(CallbackQueryHandler(handle_deposit, pattern="deposit"))
    
    # يمكنك إضافة باقي الـ Handlers هنا بنفس الطريقة

    print("🚀 البوت يعمل الآن على توكن @RamiSamir_bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
import json
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime

# --- إعدادات متجر رامي (RAMI STORE) ---
OWNER_ID = 7020070481
BOT_TOKEN = "8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk"
MY_CHANNEL = "@RamySamir2026Gold"
SUPPORT_USER = "@RamiSamir2024"
STORE_NAME_AR = "متجر رامي للمجوهرات 🛍️"
STORE_NAME_EN = "Rami Jewelry Store 🛍️"
CURRENCY_AR = "ج.م"
CURRENCY_EN = "EGP"

# ملفات البيانات
user_lang_file = "user_lang.json"
produk_file = "produk.json"
saldo_file = "saldo.json"
statistik_file = "statistik.json"

# إعداد Flask لـ Koyeb
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot is running! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- دالات معالجة البيانات ---
def load_json(file):
    if not os.path.exists(file): return {}
    with open(file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- نظام اللغات ---
def get_lang(uid):
    langs = load_json(user_lang_file)
    return langs.get(str(uid), "ar") # الافتراضي عربي

# --- القائمة الرئيسية (ثنائية اللغة) ---
async def send_main_menu(update, context):
    uid = update.effective_user.id
    lang = get_lang(uid)
    saldo = load_json(saldo_file).get(str(uid), 0)
    
    if lang == "ar":
        text = (
            f"👋 مرحباً بك في *{STORE_NAME_AR}*\n\n"
            f"💰 رصيدك: {saldo:,} {CURRENCY_AR}\n"
            f"📢 القناة: {MY_CHANNEL}"
        )
        buttons = [
            [InlineKeyboardButton("📋 قائمة المنتجات", callback_data="list_produk"),
             InlineKeyboardButton("🛒 المخزون", callback_data="cek_stok")],
            [InlineKeyboardButton("💳 شحن رصيد", callback_data="deposit"),
             InlineKeyboardButton("🌐 Change Language", callback_data="set_lang")],
            [InlineKeyboardButton("ℹ️ معلومات", callback_data="info_bot")]
        ]
    else:
        text = (
            f"👋 Welcome to *{STORE_NAME_EN}*\n\n"
            f"💰 Balance: {saldo:,} {CURRENCY_EN}\n"
            f"📢 Channel: {MY_CHANNEL}"
        )
        buttons = [
            [InlineKeyboardButton("📋 Product List", callback_data="list_produk"),
             InlineKeyboardButton("🛒 Stock", callback_data="cek_stok")],
            [InlineKeyboardButton("💳 Top Up", callback_data="deposit"),
             InlineKeyboardButton("🌐 تغيير اللغة", callback_data="set_lang")],
            [InlineKeyboardButton("ℹ️ Information", callback_data="info_bot")]
        ]
    
    if uid == OWNER_ID:
        admin_text = "🛠 لوحة التحكم" if lang == "ar" else "🛠 Admin Panel"
        buttons.append([InlineKeyboardButton(admin_text, callback_data="admin_panel")])

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

# --- تغيير اللغة ---
async def set_lang_menu(update, context):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("العربية 🇪🇬", callback_data="lang_ar"),
         InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")]
    ]
    await query.edit_message_text("الرجاء اختيار اللغة / Please choose language:", reply_markup=InlineKeyboardMarkup(keyboard))

async def change_lang(update, context):
    query = update.callback_query
    uid = query.from_user.id
    new_lang = "ar" if query.data == "lang_ar" else "en"
    
    langs = load_json(user_lang_file)
    langs[str(uid)] = new_lang
    save_json(user_lang_file, langs)
    
    await query.answer("تم تغيير اللغة بنجاح!" if new_lang == "ar" else "Language changed!")
    await send_main_menu(update, context)

# --- معلومات البوت ---
async def handle_info(update, context):
    query = update.callback_query
    lang = get_lang(query.from_user.id)
    
    if lang == "ar":
        text = f"متجر رامي متخصص في أرقى أنواع المجوهرات.\nللتواصل: {SUPPORT_USER}"
        back = "🔙 العودة"
    else:
        text = f"Rami Store specializes in fine jewelry.\nContact: {SUPPORT_USER}"
        back = "🔙 Back"
        
    keyboard = [[InlineKeyboardButton(back, callback_data="back_home")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# --- تشغيل البوت ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", send_main_menu))
    app.add_handler(CallbackQueryHandler(set_lang_menu, pattern="set_lang"))
    app.add_handler(CallbackQueryHandler(change_lang, pattern="lang_ar|lang_en"))
    app.add_handler(CallbackQueryHandler(handle_info, pattern="info_bot"))
    app.add_handler(CallbackQueryHandler(send_main_menu, pattern="back_home"))
    
    print(f"🚀 {STORE_NAME_AR} Is Live (Dual Language)...")
    app.run_polling()

if __name__ == "__main__":
    main()

