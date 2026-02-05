import os, telebot, threading
from telebot import types
from flask import Flask

# --- الإعدادات ---
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@RamySamir2026Gold" # قناتك الرسمية
bot = telebot.TeleBot(TOKEN)
user_data = {} # لتخزين بيانات المنتج مؤقتاً أثناء الإدخال

@app.route('/')
def home(): return "Store Engine is Running"

# --- لوحة التحكم الرئيسية (تظهر للمدير فقط) ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج جديد", "📊 تقارير المبيعات", "⚙️ إعدادات المتجر")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 أهلاً بك في لوحة تحكم متجرك المتطور.", reply_markup=admin_keyboard())

# --- نظام جمع بيانات المنتج (سؤال تلو الآخر) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def add_product_step1(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 خطوة 1: أرسل صورة المنتج.")
    bot.register_next_step_handler(message, process_photo)

def process_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ يرجى إرسال صورة!")
        return bot.register_next_step_handler(message, process_photo)
    user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✏️ خطوة 2: أرسل اسم المنتج.")
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "💰 خطوة 3: أرسل السعر (أرقام فقط).")
    bot.register_next_step_handler(message, process_price)

def process_price(message):
    user_data[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📏 خطوة 4: أرسل المقاسات المتاحة (مثلاً: 60، 65، 70).")
    bot.register_next_step_handler(message, process_sizes)

def process_sizes(message):
    user_data[message.chat.id]['sizes'] = message.text
    # --- المعاينة قبل النشر ---
    data = user_data[message.chat.id]
    preview_text = (f"📝 **معاينة المنتج قبل النشر:**\n\n"
                    f"📦 الاسم: {data['name']}\n"
                    f"💰 السعر: {data['price']} ج.م\n"
                    f"📏 المقاسات: {data['sizes']}\n\n"
                    f"هل تود النشر الآن في القناة؟")
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تأكيد ونشر", callback_data="confirm_publish"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_publish"))
    
    bot.send_photo(message.chat.id, data['photo'], caption=preview_text, reply_markup=markup, parse_mode="Markdown")

# --- تنفيذ النشر في القناة بأزرار احترافية ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "confirm_publish":
        data = user_data[call.message.chat.id]
        
        # إنشاء أزرار المقاسات والشراء للقناة [كما في الصورة المرجعية]
        markup = types.InlineKeyboardMarkup(row_width=3)
        size_btns = [types.InlineKeyboardButton(f"مقاس {s.strip()}", callback_data=f"buy_{s.strip()}") for s in data['sizes'].split('،' if '،' in data['sizes'] else ',')]
        markup.add(*size_btns)
        markup.add(types.InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/RamySamir2026"),
                   types.InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url="https://ramisamir2006-hash.github.io"))
        markup.add(types.InlineKeyboardButton("📜 عرض السلة", callback_data="view_cart"))

        caption = (f"✨ {data['name']}\n\n"
                   f"💰 السعر: {data['price']} ج.م\n"
                   f"✅ متوفر الآن! اطلب قبل نفاذ الكمية.")
        
        bot.send_photo(CHANNEL_ID, data['photo'], caption=caption, reply_markup=markup)
        bot.answer_callback_query(call.id, "✅ تم النشر في القناة بنجاح!")
        bot.send_message(call.message.chat.id, "🚀 تم النشر!", reply_markup=admin_keyboard())

# --- تشغيل السيرفر والبوت (حل Koyeb النهائى) ---
if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
