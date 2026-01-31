const express = require('express');
const TelegramBot = require('node-telegram-bot-api');

const app = express();
const port = process.env.PORT || 3000;

// هذا السطر ضروري جداً لإبقاء السيرفر حياً على المنصة
app.get('/', (req, res) => res.send('Bot is running...'));
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});

// إعداد البوت (تأكد من وضع التوكن في متغيرات البيئة)
const token = process.env.TELEGRAM_TOKEN;
const bot = new TelegramBot(token, {polling: true});

// ... باقي كود المتجر الخاص بك
