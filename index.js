const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
const path = require('path');

// التوكن الخاص بك
const token = '8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I';
const bot = new TelegramBot(token, {polling: true});

// إعداد سيرفر ويب بسيط (مهم جداً لتجاوز خطأ Unhealthy في Koyeb)
app.use(express.static('public'));
const PORT = process.env.PORT || 8000;

app.get('/', (req, res) => {
  res.send('البوت يعمل بنجاح!');
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});

// أوامر البوت
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, "🛍️ مرحباً بك في متجرنا!\nاستخدم الأوامر بالأسفل لتصفح المنتجات.");
});

// رسالة خطأ عامة للتشخيص
bot.on('polling_error', (error) => {
  console.log(error);
});
