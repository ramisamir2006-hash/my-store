const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080; // ضروري لمنصة Koyeb

// تفعيل الملفات العامة (واجهة المتجر)
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.send('My-Store Bot is Running!');
});

app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});

// تفعيل البوت باستخدام المتغير الذي سنضعه في Koyeb
const token = process.env.TELEGRAM_TOKEN;

if (!token) {
    console.error("خطأ: لم يتم العثور على TELEGRAM_TOKEN في إعدادات السيرفر!");
} else {
    const bot = new TelegramBot(token, { polling: true });
    
    bot.on('message', (msg) => {
        bot.sendMessage(msg.chat.id, "مرحباً بك في متجر my-store! تم التفعيل بنجاح 🚀");
    });
}
