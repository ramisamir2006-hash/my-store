import json
import sqlite3
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE"
ADMIN_ID = 7020070481  # هويتك كمدير

# --- (3) إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, details TEXT, total REAL)''')
    conn.commit()
    conn.close()

# استقبال الطلب من الواجهة
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    user = update.effective_user
    
    # حفظ في قاعدة البيانات
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id, details, total) VALUES (?, ?, ?)",
                   (user.id, str(data['items']), data['total']))
    conn.commit()
    conn.close()

    # إرسال رسالة للعميل
    await update.message.reply_text(f"شكراً {user.first_name}! تم استلام طلبك بمبلغ {data['total']} ج.م")

    # إرسال تنبيه للمدير (رامي)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🚨 **طلب جديد!**\nالعميل: {user.first_name}\nالمبلغ: {data['total']}\nالتفاصيل: {data['items']}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ضع رابط صفحة الويب التي أنشأتها هنا
    web_app_url = "https://your-github-username.github.io/" 
    keyboard = [[InlineKeyboardButton("فتح المتجر 🛒", web_app=WebAppInfo(url=web_app_url))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("أهلاً بك في متجرنا!", reply_markup=reply_markup)

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
  
