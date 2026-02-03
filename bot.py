@bot.callback_query_handler(func=lambda call: call.data == "publish_now")
def final_publish(call):
    data = user_states.get(call.message.chat.id)
    if data:
        # 1. إنشاء الأزرار التي تظهر للعملاء أسفل المنشور في القناة
        client_markup = types.InlineKeyboardMarkup(row_width=2)
        
        # زر فتح المتجر (يفتح رابط موقعك)
        btn_store = types.InlineKeyboardButton("🏪 فتح المتجر (المعرض)", url="https://ramisamir2006-hash.github.io")
        # زر إضافة للسلة (يربط العميل بالبوت الخاص بك لإتمام الطلب)
        btn_add_cart = types.InlineKeyboardButton("🛒 إضافة للسلة", url=f"https://t.me/{bot.get_me().username}?start=add_{data.get('name')}")
        # زر استفسار / مساعدة
        btn_help = types.InlineKeyboardButton("💬 استفسار / مساعدة", url="https://t.me/RamySamir2026")
        # زر عرض السلة
        btn_view_cart = types.InlineKeyboardButton("📜 عرض السلة", url=f"https://t.me/{bot.get_me().username}?start=cart")

        client_markup.add(btn_add_cart) # السطر الأول
        client_markup.add(btn_help, btn_store) # السطر الثاني
        client_markup.add(btn_view_cart) # السطر الثالث

        # 2. نص المنشور الموجه للعملاء
        caption = (
            f"✨ **{data['name']}** ✨\n\n"
            f"الرقة والذوق كله في القطعة دي. تفصيلة صغيرة لكن بتفرق في اللوك، بتدي لمسة شياكة.\n"
            f"مصنوع من الـ **ستانلس** المقاوم للصدأ. 🛡️\n\n"
            f"💰 **السعر: {data['retail']} ج.م**\n\n"
            f"اطلبيها قبل نفاذ الكمية 🛒"
        )

        # 3. النشر الفعلي في القناة مع الأزرار
        bot.send_photo(
            CHANNEL_ID, 
            data['photo'], 
            caption=caption, 
            reply_markup=client_markup, 
            parse_mode="Markdown"
        )

        bot.answer_callback_query(call.id, "✅ تم النشر بالأزرار بنجاح!")
        bot.send_message(call.message.chat.id, "🎉 المنشور الآن في القناة ومزود بأزرار التحكم للعملاء.")
        del user_states[call.message.chat.id]
        
