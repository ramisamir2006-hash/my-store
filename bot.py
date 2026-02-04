import os
import telebot
import threading
from telebot import types
from supabase import create_client
from flask import Flask

# --- إعدادات المنصة الأساسية ---
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
user_states = {}

# --- نظام الخصومات المطور ---
PROMO_CODES = {"RAMY2026": 0.15, "GOLD": 50}  # أكواد يدوية
DISCOUNT_LIMIT = 1500  # تفعيل الخصم الآلي عند شراء بضائع بـ 1500 ج.م فأكثر

@app.route('/')
def home():
    return "OCTO Platform is Healthy and Online"

# --- 1. أزرار القناة الاحترافية (تظهر للعملاء) ---
def get_client_buttons(prod_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    start_param = prod_name.replace(" ", "_")
    
    btn_buy = types.InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/Stormmarketing_bot?start=buy_{start_param}")
    btn_store = types.InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url="https://ramisamir2006-hash.github.io")
    btn_help = types.InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/RamySamir2026")
    btn_cart = types.InlineKeyboardButton("📜 عرض السلة", url=f"https://t.me/Stormmarketing_bot?start=cart")
    
    markup.add(btn_buy)
    markup.add(btn_help, btn_store)
    markup.add(btn_cart)
    return markup

# --- 2. لوحة تحكم المدير (إضافة المنتجات والتقارير) ---
def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج", "📊 التقارير", "📁 أقسام", "💡 تسويق")
    bot.send_message(chat_id, "💎 لوحة تحكم منصة my-store المحدثة:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_handler(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("buy_"):
        # مسار العميل عند الضغط على "إضافة للسلة" من القناة
        name = args[1].replace("buy_", "").replace("_", " ")
        user_states[message.chat.id] = {'prod': name, 'step': 'QTY'}
        bot.send_message(message.chat.id, f"🛍️ أهلاً بك! لطلب **{name}**، كم قطعة تريد؟")
    else:
        # مسار المدير
        show_main_menu(message.chat.id)

# --- 3. معالجة الطلب وحساب الخصومات ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'QTY')
def calc_total(message):
    try:
        qty = int(message.text)
        unit_price = 100  # بفرض السعر الافتراضي (يمكنك ربطه بالداتابيز)
        total = qty * unit_price
        
        discount = 0
        if total >= DISCOUNT_LIMIT:
            discount = total * 0.10  # خصم آلي 10%
            total -= discount
            bot.send_message(message.chat.id, f"🎊 تهانينا! حصلت على خصم آلي بقيمة {discount} ج.م لتجاوزك حد الـ 1500 ج.م")

        user_states[message.chat.id].update({'qty': qty, 'total': total, 'discount': discount, 'step': 'PROMO'})
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("لا يوجد كود")
        bot.send_message(message.chat.id, "🎁 هل لديك كود خصم مخصص لعملاء القناة؟ أرسله الآن أو اضغط الزر:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ من فضلك أرسل رقماً صحيحاً للكمية.")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'PROMO')
def apply_promo(message):
    code = message.text.upper()
    data = user_states[message.chat.id]
    
    if code in PROMO_CODES:
        promo_benefit = PROMO_CODES[code]
        deduction = data['total'] * promo_benefit if isinstance(promo_benefit, float) else promo_benefit
        data['total'] -= deduction
        data['discount'] += deduction
        bot.send_message(message.chat.id, f"✅ تم تطبيق الكود بنجاح! الإجمالي بعد الخصم الإضافي: {data['total']} ج.م")
    
    user_states[message.chat.id]['step'] = 'FINAL_INFO'
    bot.send_message(message.chat.id, "👤 من فضلك سجل بياناتك الآن (الاسم الثلاثي + الهاتف + العنوان بالتفصيل):")

# --- 4. معالجة إضافة منتج جديد (للمدير) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج")
def add_product_start(message):
    user_states[message.chat.id] = {'step': 'WAIT_PHOTO'}
    bot.send_message(message.chat.id, "📸 أرسل صورة المنتج لبدء النشر في القناة:")

@bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'WAIT_PHOTO')
def get_photo(message):
    user_states[message.chat.id].update({'photo': message.photo[-1].file_id, 'step': 'WAIT_NAME'})
    bot.send_message(message.chat.id, "✏️ أرسل اسم المنتج:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'WAIT_NAME')
def get_name(message):
    name = message.text
    photo = user_states[message.chat.id]['photo']
    
    # النشر التلقائي في القناة مع الأزرار الاحترافية
    bot.send_photo(CHANNEL_ID, photo, caption=f"✨ المنتج الجديد: {name}\n💰 السعر: سيتم تحديده عند الطلب", reply_markup=get_client_buttons(name))
    
    bot.send_message(message.chat.id, "✅ تم نشر المنتج بنجاح في القناة مع كافة أزرار التحكم والخصومات!")
    show_main_menu(message.chat.id)

# --- 5. تشغيل السيرفر والبوت (حل مشكلة Koyeb) ---
def start_bot_polling():
    print("🚀 Bot is Polling...")
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل البوت في Thread منفصل لضمان استمراره في الخلفية
    threading.Thread(target=start_bot_polling, daemon=True).start()
    # تشغيل سيرفر ويب Flask لاجتياز الـ Health Check في Koyeb
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
