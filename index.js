const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

// تشغيل السيرفر لضمان استقرار Koyeb
app.use(express.static(path.join(__dirname, 'public')));
app.get('/', (req, res) => res.send('لوحة تحكم my-store نشطة'));
app.listen(PORT, () => console.log(`Server running on ${PORT}`));

// إعداد البوت (تأكد من وضع التوكن في إعدادات Koyeb)
const token = process.env.TELEGRAM_TOKEN;
const bot = new TelegramBot(token, { polling: true });

// --- لوحة تحكم المدير ---
bot.onText(/\/start/, (msg) => {
    const opts = {
        reply_markup: {
            keyboard: [
                ['➕ إضافة قسم جديد', '📦 عرض المخزون'],
                ['➕ إضافة منتج جديد', '🖼️ عرض المنتجات'],
                ['📊 التقارير', '🎟️ نظام الخصومات'],
                ['👥 العملاء', '📢 حملة إعلانية']
            ],
            resize_keyboard: true
        }
    };
    bot.sendMessage(msg.chat.id, "أهلاً بك يا مدير! اختر المهمة المطلوبة:", opts);
});

// --- معالجة الأوامر والأزرار ---
bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    switch (text) {
        case '📊 التقارير':
            // محاكاة تقرير (يمكن ربطه بقاعدة بيانات لاحقاً)
            const report = `📈 التقرير اليومي:\n- عدد الطلبات: 15\n- عدد الزوار: 120\n- أوقات الذروة: 8:00 مساءً`;
            bot.sendMessage(chatId, report);
            break;

        case '📦 عرض المخزون':
            bot.sendMessage(chatId, "جاري جلب البيانات من المخزون...");
            break;

        case '👥 العملاء':
            const clientOpts = {
                reply_markup: {
                    inline_keyboard: [
                        [{ text: "ارسال للكل", callback_data: 'send_all' }],
                        [{ text: "تحديد عميل معين", callback_data: 'select_user' }]
                    ]
                }
            };
            bot.sendMessage(chatId, "قائمة العملاء:", clientOpts);
            break;

        case '➕ إضافة قسم جديد':
            bot.sendMessage(chatId, "يرجى إرسال اسم القسم الجديد:");
            break;
            
        // يمكنك إضافة باقي الحالات (إضافة منتج، تحديث حالة طلب) هنا بنفس الطريقة
    }
});

// --- أزرار العميل وحالة الطلب ---
bot.on('callback_query', (query) => {
    const chatId = query.message.chat.id;
    
    if (query.data === 'track_order') {
        bot.sendMessage(chatId, "حالة طلبك الحالية: (تم التجهيز 📦)");
    }
});
