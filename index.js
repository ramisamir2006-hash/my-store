const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
const path = require('path');

const token = '8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I';
const bot = new TelegramBot(token, {polling: true});

// تشغيل سيرفر ويب بسيط لـ Koyeb
app.use(express.static('public'));
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

// أوامر البوت الأساسية
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "مرحباً بك في متجري! استخدم القائمة الجانبية للتصفح.");
});
