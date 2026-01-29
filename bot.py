# أضف هذه الوظيفة داخل كود bot.py السابق
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id == ADMIN_ID:
        # لوحة تحكم المدير (رامي)
        keyboard = [
            [KeyboardButton("📊 التقرير اليومي"), KeyboardButton("➕ إضافة منتج جديد")],
            [KeyboardButton("📂 إضافة قسم جديد"), KeyboardButton("📦 متابعة الطلبات")],
            [KeyboardButton("📱 فتح واجهة المتجر كمدير", web_app=WebAppInfo(url=f"{MY_STORE_URL}?admin=true"))]
        ]
        msg = "مرحباً أيها المدير رامي! لوحة تحكم المتجر جاهزة:"
    else:
        # واجهة العميل العادي
        keyboard = [[KeyboardButton("🛍️ تصفح المتجر", web_app=WebAppInfo(url=MY_STORE_URL))]]
        msg = "أهلاً بك في متجر رامي سمير! تفضل بالتسوق:"

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(msg, reply_markup=reply_markup)
