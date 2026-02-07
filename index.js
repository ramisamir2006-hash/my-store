const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// إعداد السيرفر لـ Render أو Koyeb
const app = express();
const port = process.env.PORT || 8000;
app.get('/', (req, res) => res.send('لوحة تحكم رامي تعمل!'));
app.listen(port, () => console.log(`Server started on port ${port}`));

// ربط الجداول
const base = new Airtable({apiKey: process.env.AIRTABLE_API_KEY}).base(process.env.BASE_ID);

// ربط البوت بالتوكن الذي أرسلته (8395659007)
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

// الأزرار العربية الجديدة
bot.onText(/\/start/, (msg) => {
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة للسلة', callback_data: 'add_to_cart' }],
                [{ text: '🏪 فتح المتجر (المعرض)', url: 'https://t.me/maria_jewelry' }],
                [{ text: '💬 استفسار / مساعدة', callback_data: 'help' }]
            ]
        }
    };
    bot.sendMessage(msg.chat.id, `أهلاً بك يا ${msg.from.first_name} في متجر ماريا للذهب الصيني ✨`, opts);
});
