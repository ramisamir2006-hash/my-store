const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// حل مشكلة السيرفر (Koyeb) لكي يصبح Healthy
const app = express();
app.get('/', (req, res) => res.send('سيرفر متجر رامي يعمل!'));
app.listen(process.env.PORT || 8000);

// ربط البيانات بالخانات التي أدخلتها
const base = new Airtable({apiKey: process.env.AIRTABLE_API_KEY}).base(process.env.BASE_ID);
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

// الأزرار العربية لمتجر رامي
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "✨ أهلاً بك في متجر رامي للذهب الصيني ✨", {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة للسلة', callback_data: 'add' }],
                [{ text: '🏪 فتح المتجر (المعرض)', url: 'https://t.me/ramisami' }], // ضع رابط قناتك هنا
                [{ text: '💬 استفسار / مساعدة', callback_data: 'help' }]
            ]
        }
    });
});

// حفظ البيانات في جدول "مبيعات رامي"
bot.on('message', async (msg) => {
    if (msg.text && msg.text.includes('-')) {
        const [name, phone, type] = msg.text.split('-');
        try {
            await base('مبيعات رامي').create([{
                "fields": {
                    "العميل": name.trim(),
                    "الهاتف": phone.trim(),
                    "النوع": type ? type.trim() : "قطاعي"
                }
            }]);
            bot.sendMessage(msg.chat.id, "✅ تم تسجيل طلبك في مبيعات رامي بنجاح.");
        } catch (e) {
            bot.sendMessage(msg.chat.id, "❌ خطأ في الاتصال بجدول Airtable.");
        }
    }
});
