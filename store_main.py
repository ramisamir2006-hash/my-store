import json
import os
import threading
import logging
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

# --- 1. الإعدادات الأساسية (تأكد من التوكن الصحيح هنا) ---
OWNER_ID = 7020070481
BOT_TOKEN = "8557404137:AAHB30k_Hzj9Chh_-MEQpa3NhCpQaZfJtSM"
MY_CHANNEL = "@RamySamir2026Gold"
SUPPORT_USER = "@RamiSamir2024"
STORE_NAME_AR = "متجر رامي للمجوهرات 🛍️"
STORE_NAME_EN = "Rami Jewelry Store 🛍️"
CURRENCY_AR = "ج.م"
CURRENCY_EN = "EGP"

# ملفات البيانات
FILES = {
    "user_lang": "user_lang.json",
    "produk": "produk.json",
    "saldo": "saldo.json",
    "statistik": "statistik.json",
    "riwayat": "riwayat.json"
}

# --- 2. إعداد Flask لضمان استقرار السيرفر ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot is Live! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- 3. إدارة البيانات JSON ---
def init_db():
    for f in FILES.values():
        if not os.path.exists(f):
            with open(f, "w", encoding="utf-8") as file:
                json.dump({}, file)

def load_json(file_key):
    file_path = FILES[file_key]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def save_json(file_key, data):
    with open(FILES[file_key], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_lang(uid):
    langs = load_json("user_lang")
    return langs.get(str(uid), "ar")

# --- 4. معالجات الأوامر (Handlers) ---
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    lang = get_lang(uid)
    
    saldo_data = load_json("saldo")
    stats_data = load_json("statistik")
    
    saldo = saldo_data.get(uid, 0)
    purchases = stats_data.get(uid, {}).get("jumlah", 0)
    
    if lang == "ar":
        text = (f"👋 مرحباً بك في *{STORE_NAME_AR}*\n\n"
                f"👤 العميل: {user.full_name}\n"
                f"💰 رصيدك: {saldo:,} {CURRENCY_AR}\n"
                f"📦 مشترياتك: {purchases}\n"
                f"📢 القناة: {MY_CHANNEL}")
        buttons = [
            [InlineKeyboardButton("📋 قائمة المنتجات", callback_data="list_produk"),
             InlineKeyboardButton("🛒 المخزون", callback_data="cek_stok")],
            [InlineKeyboardButton("💳 شحن رصيد", callback_data="deposit"),
             InlineKeyboardButton("🌐 Change Language", callback_data="set_lang")],
            [InlineKeyboardButton("ℹ️ معلومات", callback_data="info_bot")]
        ]
    else:
        text = (f"👋 Welcome to *{STORE_NAME_EN}*\n\n"
                f"👤 Client: {user.full_name}\n"
                f"💰 Balance: {saldo:,} {CURRENCY_EN}\n"
                f"📦 Purchases: {purchases}\n"
                f"📢 Channel: {MY_CHANNEL}")
        buttons = [
            [InlineKeyboardButton("📋 Product List", callback_data="list_produk"),
             InlineKeyboardButton("🛒 Stock", callback_data="cek_stok")],
            [InlineKeyboardButton("💳 Top Up", callback_data="deposit"),
             InlineKeyboardButton("🌐 تغيير اللغة", callback_data="set_lang")],
            [InlineKeyboardButton("ℹ️ Information", callback_data="info_bot")]
        ]

    if int(uid) == OWNER_ID:
        admin_btn = "🛠 لوحة التحكم" if lang == "ar" else "🛠 Admin Panel"
        buttons.append([InlineKeyboardButton(admin_btn, callback_data="admin_panel")])

    kb = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="Markdown")

async def handle_lang_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    uid = str(query.from_user.id)
    new_lang = "ar" if query.data == "lang_ar" else "en"
    
    langs = load_json("user_lang")
    langs[uid] = new_lang
    save_json("user_lang", langs)
    
    msg = "تم تحديث اللغة!" if new_lang == "ar" else "Language Updated!"
    await query.answer(msg)
    await send_main_menu(update, context)

async def set_lang_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = [[InlineKeyboardButton("العربية 🇪🇬", callback_data="lang_ar"),
                InlineKeyboardButton("English 🇺🇸", callback_data="lang_en")]]
    await query.edit_message_text("اختر لغتك / Choose your language:", reply_markup=InlineKeyboardMarkup(buttons))

# --- 5. تشغيل البوت ---
def main():
    init_db()
    # تشغيل Flask في خلفية لـ Render/Koyeb
    threading.Thread(target=run_flask, daemon=True).start()
    
    # بناء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()
    
    # الروابط
    app.add_handler(CommandHandler("start", send_main_menu))
    app.add_handler(CallbackQueryHandler(set_lang_menu, pattern="set_lang"))
    app.add_handler(CallbackQueryHandler(handle_lang_selection, pattern="lang_ar|lang_en"))
    app.add_handler(CallbackQueryHandler(send_main_menu, pattern="back_home"))
    
    print(f"🚀 {STORE_NAME_AR} يعمل الآن...")
    app.run_polling(drop_pending_updates=True) # هذا السطر يحل مشكلة الـ Conflict

if __name__ == "__main__":
    main()
