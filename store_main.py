import json
import os
import threading
import logging
from flask import Flask
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, CallbackContext
)
from datetime import datetime

# --- إعدادات متجر رامي (RAMI STORE) ---
OWNER_ID = 7020070481
BOT_TOKEN = "8557404137:AAHB30k_Hzj9Chh_-MEQpa3NhCpQaZfJtSM"
MY_CHANNEL = "@RamySamir2026Gold"
SUPPORT_USER = "@RamiSamir2024"
STORE_NAME = "متجر رامي 🛍️"
CURRENCY = "ج.م" # الجنيه المصري

# ملفات البيانات JSON
produk_file = "produk.json"
saldo_file = "saldo.json"
deposit_file = "pending_deposit.json"
riwayat_file = "riwayat.json"
statistik_file = "statistik.json"

# إعداد Flask لضمان استقرار البوت على Koyeb
flask_app = Flask(__name__)
@flask_app.route('/')
def health_check(): return "البوت يعمل بكفاءة! ✅"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- دالات معالجة البيانات ---
def load_json(file):
    if not os.path.exists(file):
        return [] if file == "pending_deposit.json" else {}
    with open(file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content: return [] if file == "pending_deposit.json" else {}
        return json.loads(content)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- القائمة الرئيسية ---
async def send_main_menu(context, chat_id, user):
    saldo = load_json(saldo_file)
    statistik = load_json(statistik_file)
    s = saldo.get(str(user.id), 0)
    uid_str = str(user.id)
    jumlah = statistik.get(uid_str, {}).get("jumlah", 0)
    total = statistik.get(uid_str, {}).get("nominal", 0)

    text = (
        f"👋 مرحباً بك في *{STORE_NAME}*!\n\n"
        f"👤 العميل: {user.full_name}\n"
        f"🆔 الآيدي: `{user.id}`\n"
        f"💰 رصيدك: {s:,} {CURRENCY}\n"
        f"📦 مشترياتك: {jumlah}\n"
        f"📊 إجمالي مدفوعاتك: {total:,} {CURRENCY}"
    )

    keyboard = [
        [InlineKeyboardButton("📋 قائمة المنتجات", callback_data="list_produk"),
         InlineKeyboardButton("🛒 المخزون", callback_data="cek_stok")],
        [InlineKeyboardButton("💳 شحن رصيد", callback_data="deposit")],
        [InlineKeyboardButton("📢 قناة المتجر", url=f"https://t.me/{MY_CHANNEL.replace('@','')}")],
        [InlineKeyboardButton("ℹ️ معلومات البوت", callback_data="info_bot")],
    ]
    if user.id == OWNER_ID:
        keyboard.append([InlineKeyboardButton("🛠 لوحة تحكم الإدارة", callback_data="admin_panel")])

    await context.bot.send_message(
        chat_id=chat_id, text=text,
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

# --- معلومات البوت ---
async def handle_info_bot(update, context):
    query = update.callback_query
    text = (
        f"📖 *معلومات {STORE_NAME}*\n"
        "╽─────────────────────────────╮\n"
        f"├ 🧠 *الاسم*: `{STORE_NAME}`\n"
        f"├ 👨‍💻 *المالك*: {SUPPORT_USER}\n"
        "├ 🛒 *الوظيفة*: بيع حسابات رقمية تلقائياً\n"
        "├ ⚙️ *الميزات*: تسليم فوري، دفع بالجنيه المصري\n"
        f"├ 🗓️ *تحديث*: {datetime.now().year}\n"
        "╰─────────────────────────────╯\n\n"
        f"💬 *للدعم الفني:* {SUPPORT_USER}"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 العودة للقائمة", callback_data="back_to_produk")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def start(update: Update, context: CallbackContext):
    await send_main_menu(context, update.effective_chat.id, update.effective_user)

# --- تشغيل النظام ---
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_info_bot, pattern="info_bot"))
    # ملاحظة: يمكنك إضافة باقي معالجات الأزرار (CallbackHandlers) هنا بنفس الطريقة
    
    print(f"🚀 {STORE_NAME} يعمل الآن باللغة العربية والجنيه المصري...")
    app.run_polling()

if __name__ == "__main__":
    main()
