const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
// ملاحظة: المنصات السحابية تستخدم المنفذ 8080 أو الممرر عبر process.env.PORT
const PORT = process.env.PORT || 8080;

// إعداد ملفات الواجهة (مجلد public)
app.use(express.static(path.join(__dirname, 'public')));

// نقطة فحص الحالة لضمان عدم توقف السيرفر
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// تشغيل السيرفر أولاً
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

// تشغيل البوت باستخدام التوكن من متغيرات البيئة
const token = process.env.TELEGRAM_TOKEN;

if (!token) {
    console.error("خطأ: TELEGRAM_TOKEN غير موجود في إعدادات السيرفر!");
} else {
    // استخدم polling: true للبساطة في البداية
    const bot = new TelegramBot(token, { polling: true });

    bot.on('message', (msg) => {
        const chatId = msg.chat.id;
        bot.sendMessage(chatId, 'أهلاً بك! المتجر يعمل الآن بنجاح 🚀');
    });

    console.log("Bot is polling...");
}
