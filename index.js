const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
// المنصات السحابية تفرض استخدام المنفذ من متغيرات البيئة
const port = process.env.PORT || 8080; 

// --- تصحيح الأخطاء الكبيرة في الربط ---
// 1. تفعيل الوصول لملفات مجلد public (مثل index.html)
app.use(express.static(path.join(__dirname, 'public')));

// 2. نقطة فحص الحالة (Health Check) لمنع تعليق السيرفر
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
    console.log(`Server is live on port ${port}`);
});

// --- إعداد البوت ---
// تأكد من إضافة TELEGRAM_TOKEN في إعدادات السيرفر (Environment Variables)
const token = process.env.TELEGRAM_TOKEN;
if (!token) {
    console.error("خطأ: لم يتم ضبط توكن البوت في متغيرات البيئة!");
} else {
    const bot = new TelegramBot(token, {polling: true});
    
    bot.on('message', (msg) => {
        bot.sendMessage(msg.chat.id, "أهلاً بك في متجري! البوت يعمل الآن بنجاح.");
    });
}
