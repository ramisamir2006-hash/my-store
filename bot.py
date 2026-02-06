import os, telebot, threading, sqlite3
from telebot import types
from flask import Flask

# --- إعدادات المنصة المخصصة لـ @Stormarketing_bot ---
app = Flask(__name__)
TOKEN = "8395659007:AAF3cxAE3jj8ffg16G8TTrzsqqQIiZBHZPA" # التوكن الخاص بك
CHANNEL_ID = "@RamySamir2026Gold" 
STAFF_GROUP_ID = -1002376483563 
ADMIN_ID = 7020070481 # معرفك كمدير

bot = telebot.TeleBot(TOKEN)
user_data = {} 

# --- 1. إدارة قاعدة البيانات (SQLite) ---
def init_db():
    conn = sqlite3.connect('store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price TEXT, photo TEXT, sizes TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home(): return "Stormarketing System is Fully Loaded"

# --- 2. لوحة التحكم الرئيسية ---
def main_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج جديد", "📊 تقارير المبيعات")
    markup.add("📁 إدارة الأقسام", "👥 فريق العمل (الموظفين)")
    markup.add("🖼️ تغيير غلاف المتجر", "⚙️ الإعدادات العامة")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        welcome = f"🤖 **أهلاً بك يا مدير رامي في لوحة التحكم.**\nID: `{message.from_user.id}`"
        bot.send_message(message.chat.id, welcome, reply_markup=main_admin_keyboard(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "🏪 أهلاً بك في متجر ماريا. تصفح القناة لمشاهدة المنتجات.")

# --- 3. نظام إضافة المنتج (التدفق الكامل) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def start_add(message):
    if message.from_user.id != ADMIN_ID: return
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 **1. أرسل صورة المنتج الآن:**")
    bot.register_next_step_handler(message, get_photo)

def get_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "⚠️ أرسل صورة صحيحة!")
        return bot.register_next_step_handler(message, get_photo)
    user_data[message.chat.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✏️ **2. أرسل اسم المنتج ووصفه:**")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "💰 **3. أرسل السعر (أرقام فقط):**")
    bot.register_next_step_handler(message, get_price)

def get_price(message):
    user_data[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📏 **4. أرسل المقاسات (مثلاً: 60, 70, 80):**")
    bot.register_next_step_handler(message, get_sizes)

def get_sizes(message):
    user_data[message.chat.id]['sizes'] = message.text
    send_preview(message)

# --- 4. المعاينة والتعديل قبل النشر ---
def send_preview(message):
    data = user_data[message.chat.id]
    preview = (f"🔍 **معاينة المنتج قبل النشر:**\n\n"
               f"📦 الاسم: {data['name']}\n"
               f"💰 السعر: {data['price']} ج.م\n"
               f"📏 المقاسات: {data['sizes']}")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد ونشر", callback_data="confirm_pub"),
               types.InlineKeyboardButton("✏️ تعديل الصورة", callback_data="edit_pic"))
    markup.add(types.InlineKeyboardButton("✏️ تعديل النص", callback_data="edit_txt"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_pub"))
    
    bot.send_photo(message.chat.id, data['photo'], caption=preview, reply_markup=markup)

# --- 5. تنفيذ العمليات وأزرار العملاء الاحترافية ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    if call.data == "confirm_pub":
        data = user_data.get(chat_id)
        if not data: return
        
        # حفظ في الداتابيز فعلياً
        conn = sqlite3.connect('store.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, photo, sizes) VALUES (?, ?, ?, ?)",
                  (data['name'], data['price'], data['photo'], data['sizes']))
        conn.commit()
        conn.close()

        # إنشاء أزرار المقاسات للقناة (مثل الصور المرجعية)
        markup = types.InlineKeyboardMarkup(row_width=3)
        sizes = data['sizes'].split(',')
        btns = [types.InlineKeyboardButton(f"🛒 مقاس {s.strip()}", callback_data=f"buy_{s.strip()}_{data['name']}") for s in sizes]
        markup.add(*btns)
        markup.add(types.InlineKeyboardButton("💬 استفسار", url="https://t.me/RamySamir2026"),
                   types.InlineKeyboardButton("🏪 المعرض", url="https://ramisamir2006-hash.github.io"))
        
        caption = f"🆕 **{data['name']}**\n\n💰 السعر: {data['price']} ج.م\n📦 اطلبي الآن عبر الأزرار أدناه 👇"
        bot.send_photo(CHANNEL_ID, data['photo'], caption=caption, reply_markup=markup, parse_mode="Markdown")
        bot.edit_message_caption("🚀 تم النشر في القناة بنجاح!", chat_id, call.message.message_id)

    elif call.data.startswith("buy_"):
        info = call.data.split("_")
        bot.send_message(STAFF_GROUP_ID, f"🔔 **طلب جديد!**\n👤 من: @{call.from_user.username}\n🛍️ المنتج: {info[2]}\n📏 المقاس: {info[1]}")
        bot.answer_callback_query(call.id, "✅ تم إرسال طلبك للموظفين.")

# --- تشغيل النظام ---
if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    
