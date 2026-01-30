const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const app = express();
const path = require('path');

const token = '8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I';
const bot = new TelegramBot(token, {polling: true});

app.use(express.json());
app.use(express.static('public'));

// إعداد أوامر القائمة الجانبية
bot.setMyCommands([
  {command: 'start', description: 'تشغيل المتجر'},
  {command: 'panel', description: 'لوحة التحكم'},
  {command: 'report', description: 'التقرير اليومي/الشهري'},
  {command: 'cancel', description: 'إلغاء العملية'}
]);

// أمر التقرير اليومي والمخزون
bot.onText(/\/report/, (msg) => {
  const report = `📊 **تقرير متجر my-store**\n\n` +
                 `📅 التاريخ: ${new Date().toLocaleDateString('ar-EG')}\n` +
                 `📦 المخزون: متوفر\n` +
                 `💰 مبيعات اليوم: 0.00\n` +
                 `💬 استفسارات: لا يوجد`;
  bot.sendMessage(msg.chat.id, report, {parse_mode: 'Markdown'});
});

// استقبال البيانات من لوحة التحكم (HTML) ونشرها
app.post('/publish', (req, res) => {
  const { name, price, discRetail, discWholesale, image, cat, size } = req.body;
  
  const retailFinal = price - (price * (discRetail / 100));
  const wholesaleFinal = price - (price * (discWholesale / 100));

  const caption = `🆕 **منتج جديد في قسم: ${cat}**\n\n` +
                  `🏷 الاسم: ${name}\n` +
                  `📏 المقاسات: ${size}\n\n` +
                  `💰 سعر التجزئة: ${retailFinal} ج.م\n` +
                  `📦 سعر الجملة: ${wholesaleFinal} ج.م\n\n` +
                  `🚚 التوصيل لجميع المحافظات!`;

  bot.sendPhoto('@YOUR_CHANNEL_ID', image, {
    caption: caption,
    parse_mode: 'Markdown',
    reply_markup: {
      inline_keyboard: [[{ text: "🛒 إضافة للسلة", callback_data: "add_to_cart" }]]
    }
  });
  res.sendStatus(200);
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Server is running on port ${PORT}`));
