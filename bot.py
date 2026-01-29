import json
import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- الإعدادات ---
TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
ADMIN_ID = 7020070481
CHANNEL_ID = "@RamySamir2026Gold" # ضع معرف قناتك هنا
WEB_APP_URL = "https://ramisamir2006-hash.github.io/my-store/"

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    # جداول المنتجات، الطلبات، والعملاء المحظورين
    cursor.execute('''CREATE TABLE IF NOT EXISTS products 
        (id INTEGER PRIMARY KEY, name TEXT, price REAL, cat TEXT, sizes TEXT, stock INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders 
        (id INTEGER PRIMARY KEY, user_id INTEGER, details TEXT, total REAL, date TEXT, type TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()

# --- لوحات التحكم ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # التحقق من الحظر
    conn = sqlite3.connect('store.db')
    is_banned = conn.execute('SELECT 1 FROM banned_users WHERE user_id=?', (user_id,)).fetchone()
    if is_banned:
        await update.message.reply_text("❌ عذراً، لقد تم حظرك من استخدام المتجر.")
        return

    if user_id == ADMIN_ID:
        keyboard = [
            [KeyboardButton("📊 التقارير (يومي/أسبوعي)"), KeyboardButton("📦 إدارة الطلبات")],
            [KeyboardButton("➕ إضافة منتج للقناة"), KeyboardButton("🚫 حظر عميل")],
            [KeyboardButton("⚙️ لوحة تحكم المتجر", web_app=WebAppInfo(url=f"{WEB_APP_URL}?admin=true"))]
        ]
        msg = "مرحباً يا مدير رامي. التحكم الكامل بين يديك:"
    else:
        keyboard = [
            [KeyboardButton("🛍️ دخول المتجر", web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton("💬 استفسار / دعم فني"), KeyboardButton("🛒 سلة المشتريات")]
        ]
        msg = "أهلاً بك في متجرنا! تفضل بتصفح الموديلات الجديدة:"

    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# --- نظام النشر في القناة وتتبع الأوردرات ---
async def handle_new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    user = update.effective_user
    
    # حساب الخصم (جملة أو تجزئة)
    order_type = data.get('type', 'retail') # retail أو wholesale
    discount = 0.15 if order_type == 'wholesale' else 0 # خصم 15% للجملة
    final_total = data['total'] * (1 - discount)

    # حفظ الطلب في قاعدة البيانات
    conn = sqlite3.connect('store.db')
    conn.execute('INSERT INTO orders (user_id, details, total, date, type) VALUES (?, ?, ?, ?, ?)',
                 (user.id, str(data['items']), final_total, datetime.now().strftime("%Y-%m-%d"), order_type))
    conn.commit()
    conn.close()

    # إخطار المدير
    admin_msg = f"🚨 **أوردر جديد ({order_type})**\n👤 العميل: {user.first_name}\n💰 الإجمالي بعد الخصم: {final_total} ج.م\n📦 التفاصيل: {data['items']}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)

# --- نظام التقارير ---
async def send_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    
    conn = sqlite3.connect('store.db')
    today = datetime.now().strftime("%Y-%m-%d")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    daily_total = conn.execute('SELECT SUM(total) FROM orders WHERE date=?', (today,)).fetchone()[0] or 0
    weekly_total = conn.execute('SELECT SUM(total) FROM orders WHERE date >= ?', (last_week,)).fetchone()[0] or 0
    
    report = f"📈 **تقارير المبيعات**\n\n💰 مبيعات اليوم: {daily_total} ج.م\n🗓️ مبيعات الأسبوع: {weekly_total} ج.م"
    await update.message.reply_text(report, parse_mode="Markdown")

# --- تشغيل البوت ---
def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_new_order))
    app.add_handler(MessageHandler(filters.Text("📊 التقارير (يومي/أسبوعي)"), send_reports))
    app.run_polling()

if __name__ == "__main__":
    main()
