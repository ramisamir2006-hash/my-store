const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// إصلاح مشكلة السيرفر (Koyeb)
const app = express();
app.get('/', (req, res) => res.send('سيرفر متجر رامي يعمل بنجاح!'));
app.listen(process.env.PORT || 8000);

// ربط الجداول (Airtable)
const base = new Airtable({apiKey: process.env.AIRTABLE_API_KEY}).base(process.env.BASE_ID);

// ربط البوت
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

// الأزرار العربية للمتجر
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "✨ مرحباً بك في متجر رامي ✨", {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة للسلة', callback_data: 'add' }],
                [{ text: '🏪 المعرض', url: 'https://t.me/ramisami' }]
            ]
        }
    });
});

// استقبال الطلبات وحفظها
bot.on('message', async (msg) => {
    if (msg.text && msg.text.includes('-')) {
        const [name, phone] = msg.text.split('-');
        try {
            await base('مبيعات رامي').create([{
                "fields": { "العميل": name.trim(), "الهاتف": phone.trim() }
            }]);
            bot.sendMessage(msg.chat.id, "✅ تم تسجيل طلبك بنجاح!");
        } catch (e) {
            bot.sendMessage(msg.chat.id, "❌ خطأ في الربط بالجداول.");
        }
    }
});
