import os, telebot, threading
from telebot import types
from flask import Flask

# --- الإعدادات ---
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@RamySamir2026Gold" 
STAFF_GROUP_ID = -1002376483563 
ADMIN_ID = 5664157143 # تأكد من وضع ID حسابك هنا

bot = telebot.TeleBot(TOKEN)
temp_product = {} # مخزن مؤقت لعملية الإضافة والتعديل

@app.route('/')
def home(): return "Store Engine is Fully Active"

# --- 1. لوحة تحكم المدير والموظفين ---
def main_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج جديد", "📊 التقارير")
    markup.add("📁 إدارة الأقسام", "👥 الموظفين")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "💎 أهلاً بك في لوحة التحكم الشاملة لمتجر ماريا.", 
                     reply_markup=main_admin_keyboard())

# --- 2. نظام إضافة المنتج التفاعلي (سؤال تلو الآخر) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج جديد")
def start_add(message):
    temp_product[message.chat.id] = {}
    bot.send_message(message.chat.id, "📸 **1. أرسل صورة المنتج:**")
    bot.register_next_step_handler(message, process_photo)

def process_photo(message):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ خطأ! أرسل صورة.")
        return bot.register_next_step_handler(message, process_photo)
    temp_product[message.chat.id]['photo'] = message.photo[-1].file_id
    bot.send_message(message.chat.id, "✏️ **2. أرسل اسم المنتج:**")
    bot.register_next_step_handler(message, process_name)

def process_name(message):
    temp_product[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "💰 **3. أرسل السعر (مثال: 89):**")
    bot.register_next_step_handler(message, process_price)

def process_price(message):
    temp_product[message.chat.id]['price'] = message.text
    bot.send_message(message.chat.id, "📏 **4. أرسل المقاسات المتاحة (افصل بينها بفاصلة مثل: 70, 65, 60):**")
    bot.register_next_step_handler(message, process_sizes)

def process_sizes(message):
    temp_product[message.chat.id]['sizes'] = message.text
    send_preview(message)

# --- 3. نظام المعاينة والتعديل قبل النشر ---
def send_preview(message):
    data = temp_product[message.chat.id]
    preview_text = (f"🔍 **معاينة المنتج النهائية:**\n\n"
                    f"📦 الاسم: {data['name']}\n"
                    f"💰 السعر: {data['price']} ج.م\n"
                    f"📏 المقاسات: {data['sizes']}\n\n"
                    "هل البيانات صحيحة؟ يمكنك التعديل أو النشر فوراً.")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ تأكيد ونشر في القناة", callback_data="final_publish"),
               types.InlineKeyboardButton("✏️ تعديل الصورة", callback_data="edit_photo"))
    markup.add(types.InlineKeyboardButton("✏️ تعديل الاسم/السعر", callback_data="edit_text"),
               types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_post"))
    
    bot.send_photo(message.chat.id, data['photo'], caption=preview_text, reply_markup=markup, parse_mode="Markdown")

# --- 4. تنفيذ النشر للعملاء بأزرار المقاسات الاحترافية ---
@bot.callback_query_handler(func=lambda call: True)
def handle_actions(call):
    chat_id = call.message.chat.id
    
    if call.data == "final_publish":
        data = temp_product.get(chat_id)
        if not data: return
        
        # إنشاء أزرار المقاسات للعميل
        markup = types.InlineKeyboardMarkup(row_width=3)
        sizes_list = data['sizes'].split(',')
        size_btns = [types.InlineKeyboardButton(f"🛒 مقاس {s.strip()}", callback_data=f"order_{s.strip()}_{data['name']}") for s in sizes_list]
        markup.add(*size_btns)
        
        # أزرار الدعم والمعرض
        markup.add(types.InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/RamySamir2026"),
                   types.InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url="https://ramisamir2006-hash.github.io"))
        markup.add(types.InlineKeyboardButton("📜 عرض السلة", callback_data="view_cart"))
        
        caption = (f"🆕 **منتج جديد متوفر الآن!**\n\n"
                   f"✨ {data['name']}\n"
                   f"💰 السعر: {data['price']} ج.م\n"
                   f"🚚 التوصيل متاح لجميع المحافظات.")
        
        bot.send_photo(CHANNEL_ID, data['photo'], caption=caption, reply_markup=markup, parse_mode="Markdown")
        bot.send_message(chat_id, "✅ تم النشر بنجاح في القناة بالأزرار الاحترافية!", reply_markup=main_admin_keyboard())

    elif call.data.startswith("order_"):
        # إرسال تفاصيل الطلب لجروب الموظفين
        details = call.data.split("_")
        customer = f"👤 عميل: @{call.from_user.username or call.from_user.id}\n🛍️ طلب: {details[2]}\n📏 مقاس: {details[1]}"
        bot.send_message(STAFF_GROUP_ID, f"🔔 **طلب شراء جديد وصل!**\n\n{customer}")
        bot.answer_callback_query(call.id, "✅ تم إرسال طلبك لفريق العمل.")

    elif call.data == "edit_photo":
        bot.send_message(chat_id, "📸 أرسل الصورة الجديدة الآن:")
        bot.register_next_step_handler(call.message, process_photo)

# --- 5. تشغيل السيرفر والبوت ---
if __name__ == "__main__":
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
        
