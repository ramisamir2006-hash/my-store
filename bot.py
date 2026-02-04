import os, telebot, types
from supabase import create_client
from flask import Flask
from threading import Thread

# إعدادات المنصة
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
user_states = {}

# نظام الخصومات
PROMO_CODES = {"RAMY2026": 0.15, "GOLD": 50} # أكواد يدوية
DISCOUNT_LIMIT = 1500 # خصم آلي عند 1500 ج.م

@app.route('/')
def home(): return "OCTO Platform Active"

# --- 1. أزرار القناة الاحترافية ---
def get_client_buttons(prod_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # رابط يفتح البوت مباشرة مع أمر الشراء
    start_param = prod_name.replace(" ", "_")
    btn_buy = types.InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/Stormmarketing_bot?start=buy_{start_param}")
    btn_store = types.InlineKeyboardButton("🏪 المعرض", url="https://ramisamir2006-hash.github.io")
    btn_help = types.InlineKeyboardButton("💬 استفسار", url="https://t.me/RamySamir2026")
    btn_cart = types.InlineKeyboardButton("📜 عرض السلة", url=f"https://t.me/Stormmarketing_bot?start=cart")
    
    markup.add(btn_buy)
    markup.add(btn_help, btn_store)
    markup.add(btn_cart)
    return markup

# --- 2. معالجة الطلب والخصومات ---
@bot.message_handler(commands=['start'])
def start_handler(message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("buy_"):
        name = args[1].replace("buy_", "").replace("_", " ")
        user_states[message.chat.id] = {'prod': name, 'step': 'QTY'}
        bot.send_message(message.chat.id, f"🛍️ أهلاً بك! لطلب **{name}**، كم قطعة تريد؟")
    else:
        main_admin_menu(message)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'QTY')
def calc_total(message):
    try:
        qty = int(message.text)
        # نفترض السعر 100 ج.م للتجربة (يجب جلبه من الداتابيز لاحقاً)
        unit_price = 100 
        total = qty * unit_price
        
        # تطبيق الخصم الآلي
        discount = 0
        if total >= DISCOUNT_LIMIT:
            discount = total * 0.10
            total -= discount
            bot.send_message(message.chat.id, f"🎊 مبروك! حصلت على خصم آلي {discount} ج.م لتجاوزك مبلغ {DISCOUNT_LIMIT} ج.م")

        user_states[message.chat.id].update({'qty': qty, 'total': total, 'discount': discount, 'step': 'PROMO'})
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("لا يوجد كود")
        bot.send_message(message.chat.id, "🎁 هل لديك كود خصم يدوي؟ (أرسله الآن أو اضغط الزر):", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ يرجى إرسال رقم صحيح.")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'PROMO')
def apply_promo(message):
    code = message.text.upper()
    data = user_states[message.chat.id]
    
    if code in PROMO_CODES:
        promo_val = PROMO_CODES[code]
        deduction = data['total'] * promo_val if isinstance(promo_val, float) else promo_val
        data['total'] -= deduction
        data['discount'] += deduction
        bot.send_message(message.chat.id, f"✅ تم تطبيق الكود! الإجمالي النهائي: {data['total']} ج.م")
    
    user_states[message.chat.id]['step'] = 'FINAL'
    bot.send_message(message.chat.id, "👤 الآن أرسل اسمك الثلاثي وعنوانك للتوصيل:")

# --- 3. لوحة تحكم المدير ---
def main_admin_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج", "📊 التقارير")
    bot.send_message(message.chat.id, "💎 لوحة تحكم منصة my-store المحدثة:", reply_markup=markup)

if __name__ == "__main__":
    # تشغيل Flask لتجنب خطأ Unhealthy في Koyeb
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    bot.infinity_polling()
  # تشغيل البوت في الخلفية عند تشغيل Flask بواسطة gunicorn
def start_bot():
    print("🚀 Bot is starting...")
    bot.infinity_polling()
if __name__ == "__main__":
    # هذا الجزء للموقع المحلي فقط
    Thread(target=start_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
else:
    # هذا الجزء هو ما سيستخدمه Koyeb عبر gunicorn
    Thread(target=start_bot).start()
        
