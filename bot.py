import os, telebot, types
from supabase import create_client
from flask import Flask
from threading import Thread
from datetime import datetime

# إعدادات الهوية والاتصال
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = "https://xounbdcfmjuzgtpeefyj.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHANNEL_ID = "@RamySamir2026Gold"

bot = telebot.TeleBot(TOKEN)
db = create_client(SUPABASE_URL, SUPABASE_KEY)
user_states = {}

@app.route('/')
def home(): return "OCTO-STYLE Platform is Live!"

# --- 1. نظام النشر المتطور (أزرار العملاء) ---
def get_client_markup(product_name, price):
    markup = types.InlineKeyboardMarkup(row_width=2)
    # ربط مباشر بالبوت لبدء طلب القطعة
    order_url = f"https://t.me/Stormmarketing_bot?start=buy_{product_name.replace(' ', '_')}"
    
    markup.add(types.InlineKeyboardButton("🛒 إضافة للسلة والشراء", url=order_url))
    markup.add(
        types.InlineKeyboardButton("🏪 المعرض", url="https://ramisamir2006-hash.github.io"),
        types.InlineKeyboardButton("💬 دعم فني", url="https://t.me/RamySamir2026")
    )
    markup.add(types.InlineKeyboardButton("📜 عرض سلة مشترياتي", url="https://t.me/Stormmarketing_bot?start=cart"))
    return markup

# --- 2. معالجة طلبات العملاء (تسجيل البيانات) ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    text = message.text
    if "buy_" in text:
        prod_name = text.split("buy_")[1].replace("_", " ")
        user_states[message.chat.id] = {'prod': prod_name, 'step': 'QTY'}
        bot.send_message(message.chat.id, f"🛍️ اختيار رائع! لطلب **{prod_name}**، كم قطعة تحتاج؟")
    else:
        # لوحة تحكم الإدارة
        main_menu(message)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'QTY')
def set_qty(message):
    user_states[message.chat.id].update({'qty': message.text, 'step': 'DELIVERY'})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚚 دليفري (عنواني)", "🏪 استلام من مقر المتجر")
    bot.send_message(message.chat.id, "📦 اختر طريقة الاستلام:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'DELIVERY')
def set_delivery(message):
    user_states[message.chat.id].update({'delivery': message.text, 'step': 'INFO'})
    bot.send_message(message.chat.id, "📝 سجل بياناتك (الاسم الثلاثي + رقم الهاتف + العنوان بالتفصيل):")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'INFO')
def save_order(message):
    data = user_states[message.chat.id]
    order_info = message.text
    
    # حفظ في قاعدة البيانات (المنصة)
    db.table("orders").insert({
        "client_info": order_info,
        "product": data['prod'],
        "quantity": data['qty'],
        "method": data['delivery'],
        "status": "قيد المراجعة"
    }).execute()
    
    bot.send_message(message.chat.id, "✅ تم تسجيل طلبك بنجاح! فريق OCTO TECH سيقوم بتأكيد الطلب معك.")
    # إشعار للمدير
    bot.send_message(os.getenv("ADMIN_ID"), f"🔔 طلب جديد:\n{order_info}\nالمنتج: {data['prod']}")
    del user_states[message.chat.id]

# --- 3. لوحة تحكم المدير (إضافة منتج) ---
@bot.message_handler(func=lambda m: m.text == "➕ إضافة منتج")
def add_product_start(message):
    user_states[message.chat.id] = {'step': 'ADMIN_PHOTO'}
    bot.send_message(message.chat.id, "📸 أرسل صورة المنتج الجديد:")

@bot.message_handler(content_types=['photo'], func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ADMIN_PHOTO')
def admin_get_photo(message):
    user_states[message.chat.id].update({'photo': message.photo[-1].file_id, 'step': 'ADMIN_DATA'})
    bot.send_message(message.chat.id, "🏷️ أرسل (الاسم - السعر - الوصف) في رسالة واحدة:")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'ADMIN_DATA')
def admin_publish(message):
    info = message.text.split("-")
    data = user_states[message.chat.id]
    
    # النشر الاحترافي في القناة
    markup = get_client_markup(info[0], info[1])
    caption = f"💎 **{info[0]}**\n💰 السعر: {info[1]} ج.م\n\n{info[2]}\n\n✅ برمجة متطورة بواسطة OCTO TECH"
    
    bot.send_photo(CHANNEL_ID, data['photo'], caption=caption, reply_markup=markup, parse_mode="Markdown")
    bot.send_message(message.chat.id, "🚀 تم النشر بنجاح على القناة!")
    del user_states[message.chat.id]

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("➕ إضافة منتج", "📊 تقارير الأعمال", "👥 إدارة العملاء")
    bot.send_message(message.chat.id, "🏢 منصة my-store الإدارية\nبإدارة OCTO TECH", reply_markup=markup)

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    bot.infinity_polling()
    # إعداد قيمة الخصم والحد الأدنى
DISCOUNT_THRESHOLD = 1500  # الحد الأدنى لتفعيل الخصم
DISCOUNT_PERCENT = 0.10     # نسبة الخصم 10%

# --- دالة حساب السعر النهائي ---
def calculate_final_price(total_price):
    if total_price >= DISCOUNT_THRESHOLD:
        discount_amount = total_price * DISCOUNT_PERCENT
        final_price = total_price - discount_amount
        return final_price, discount_amount
    return total_price, 0

# --- تعديل معالجة الطلب لتشمل الخصم الآلي ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'QTY')
def set_qty(message):
    try:
        qty = int(message.text)
        data = user_states[message.chat.id]
        
        # جلب سعر المنتج من البيانات المخزنة (بفرض أن السعر مخزن عند الضغط على الزر)
        price_per_unit = float(data.get('unit_price', 0))
        total_before_discount = qty * price_per_unit
        
        final_price, discount_val = calculate_final_price(total_before_discount)
        
        user_states[message.chat.id].update({
            'qty': qty, 
            'total_price': final_price,
            'discount': discount_val,
            'step': 'DELIVERY'
        })

        if discount_val > 0:
            msg = (f"🎊 تهانينا! لقد حصلت على خصم بقيمة {discount_val} ج.م\n"
                   f"💰 الإجمالي بعد الخصم: {final_price} ج.م\n\n"
                   f"📦 اختر طريقة الاستلام:")
        else:
            msg = f"💰 الإجمالي: {final_price} ج.م\n\n📦 اختر طريقة الاستلام:"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🚚 دليفري (عنواني)", "🏪 استلام من مقر المتجر")
        bot.send_message(message.chat.id, msg, reply_markup=markup)
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ من فضلك أرسل رقماً صحيحاً للكمية.")
# --- حفظ الطلب في الداتابيز مع تفاصيل الخصم ---
def finalize_order_to_db(chat_id, data, client_info):
    db.table("orders").insert({
        "client_info": client_info,
        "product": data['prod'],
        "quantity": data['qty'],
        "total_amount": data['total_price'],
        "discount_applied": data['discount'],
        "method": data['delivery'],
        "status": "قيد المراجعة",
        "created_at": "now()"
    }).execute()
# قائمة أكواد الخصم (يمكنك لاحقاً وضعها في الداتابيز)
PROMO_CODES = {
    "RAMY2026": 0.15,  # خصم 15%
    "OCTO": 0.20,      # خصم 20% لعملاء القناة المميزين
    "GOLD": 50         # خصم ثابت 50 جنيه
}

# --- تعديل خطوة ما بعد اختيار طريقة الاستلام ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'DELIVERY')
def ask_for_promo(message):
    user_states[message.chat.id].update({'delivery': message.text, 'step': 'PROMO_CHECK'})
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("لا يوجد لدي كود")
    bot.send_message(message.chat.id, "🎁 هل لديك كود خصم مخصص لعملاء القناة؟ أرسله الآن أو اضغط على الزر أدناه:", reply_markup=markup)

# --- معالجة كود الخصم المكتوب ---
@bot.message_handler(func=lambda m: user_states.get(m.chat.id, {}).get('step') == 'PROMO_CHECK')
def apply_promo(message):
    code = message.text.upper()
    data = user_states[message.chat.id]
    total = data['total_price']
    discount_val = data['discount'] # الخصم الآلي السابق (الـ 1500 جنيه)

    if code in PROMO_CODES:
        promo_benefit = PROMO_CODES[code]
        
        # إذا كان الخصم نسبة (مثلاً 0.15)
        if isinstance(promo_benefit, float):
            promo_discount = total * promo_benefit
        # إذا كان الخصم مبلغ ثابت (مثلاً 50)
        else:
            promo_discount = promo_benefit
            
        total -= promo_discount
        discount_val += promo_discount
        
        bot.send_message(message.chat.id, f"✅ تم تطبيق الكود بنجاح! خصم إضافي: {promo_discount} ج.م")
    elif code != "لا يوجد لدي كود":
        bot.send_message(message.chat.id, "❌ عذراً، هذا الكود غير صحيح أو انتهت صلاحيته.")

    # التحديث النهائي للبيانات قبل طلب المعلومات الشخصية
    user_states[message.chat.id].update({
        'total_price': total,
        'discount': discount_val,
        'promo_used': code if code in PROMO_CODES else "None",
        'step': 'INFO'
    })
    
    bot.send_message(message.chat.id, f"💰 الإجمالي النهائي المعتمد: {total} ج.م\n\n📝 من فضلك سجل بياناتك (الاسم + الهاتف + العنوان):")
    
