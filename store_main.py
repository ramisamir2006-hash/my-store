import os
import threading
import logging
import pyTelegramBotAPI
from pyTelegramBotAPI import types
from flask import Flask

# --- 1. إعدادات الربط النهائية (تأكد من التوكن الصحيح) ---
BOT_TOKEN = '8557404137:AAHB30k_Hzj9Chh_-MEQpa3NhCpQaZfJtSM'
ADMIN_ID = 7020070481  # آيدي المالك الخاص بك
MY_CHANNEL = '@RamySamir2026Gold'
SUPPORT_USER = '@RamiSamir2024'

# إعداد البوت
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# إعداد السجلات (Logs) للمراقبة في Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 2. إعداد Flask (لإبقاء السيرفر حياً وتجنب فشل الـ Build) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "<h1>Rami Store Bot is Active! ✅</h1>"

def run_flask():
    # المنصة تقرأ المنفذ من المتغيرات البيئية (Port)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 3. معالجة الأوامر وصلاحيات المسؤول ---
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📦 إدارة المنتجات", "🛍 عرض الطلبات")
        markup.add("📣 إرسال رسالة للكل", "⚙️ الإعدادات")
        bot.send_message(user_id, "أهلاً بك يا سيد رامي في لوحة تحكم متجرك 👑", reply_markup=markup)
    else:
        bot.send_message(user_id, f"مرحباً بك في متجرنا! 🛍\nللتواصل مع الدعم الفني: {SUPPORT_USER}")

# --- 4. تشغيل النظام بالكامل ---
if __name__ == '__main__':
    try:
        # تشغيل سيرفر الويب في الخلفية
        threading.Thread(target=run_flask, daemon=True).start()
        logger.info("✅ Flask server started successfully.")
        
        # حل مشكلة الـ Conflict (حذف الـ Webhook القديم)
        bot.remove_webhook()
        logger.info(f"🚀 Bot started for Admin ID: {ADMIN_ID}")
        
        # تشغيل البوت مع خاصية تخطي التحديثات القديمة لتجنب التعليق
        bot.infinity_polling(skip_pending=True)
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")

