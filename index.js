const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
// المنصات السحابية تفرض استخدام المنفذ من المتغيرات البيئية
const port = process.env.PORT || 8080; 

// ربط مجلد الواجهة
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.send('Bot is running properly...');
});

app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});

// قراءة التوكن بأمان
const token = process.env.TELEGRAM_TOKEN;

if (!token) {
    console.error("ERROR: TELEGRAM_TOKEN is missing!");
} else {
    const bot = new TelegramBot(token, { polling: true });
    
    bot.on('message', (msg) => {
        bot.sendMessage(msg.chat.id, "أهلاً بك! البوت يعمل الآن من السيرفر بنجاح.");
    });
}
