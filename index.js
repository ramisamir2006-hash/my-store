const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
app.use(express.json()); // ضروري لاستقبال بيانات المنتجات من لوحة التحكم

// استخدام المنفذ 8000 كما برمجنا سابقاً في Koyeb
const PORT = process.env.PORT || 8000;

// إعداد ملفات الواجهة (مجلد public)
app.use(express.static(path.join(__dirname, 'public')));

// تشغيل البوت باستخدام التوكن
const token = '8395659007:AAHPrAQh6S50axorF_xrtI8XAFSRUyrXe3I'; 
const bot = new TelegramBot(token, { polling: true });

// --- الجزء الخاص باستقبال البيانات من لوحة التحكم ونشرها ---
app.post('/publish', (req, res) => {
    const { name, price, discRetail, discWholesale, image, cat, size } = req.body;
    
    // حساب الأسعار بعد الخصم
    const retailFinal = price - (price * (discRetail / 100));
    const wholesaleFinal = price - (price * (discWholesale / 100));

    // تنسيق رسالة الإكسسوارات
    const caption = `✨ **قطعة فريدة جديدة من my-store** ✨\n\n` +
                  `💍 **النوع:** ${name}\n` +
                  `🎨 **المادة/اللون:** ${size}\n` +
                  `📂 **القسم:** ${cat}\n\n` +
                  `💰 **السعر:** ${retailFinal} ج.م\n` +
                  `🎁 **سعر الجملة:** ${wholesaleFinal} ج.م\n\n` +
                  `🛍️ للطلب أو الاستفسار تواصل معنا الآن!`;

    // إرسال الصورة مع التفاصيل للقناة (استبدل @YOUR_CHANNEL_ID بمعرف قناتك)
    bot.sendPhoto('@YOUR_CHANNEL_ID', image, {
        caption: caption,
        parse_mode: 'Markdown',
        reply_markup: {
            inline_keyboard: [
                [{ text: "🛒 اطلب عبر واتساب", url: "https://wa.me/20123456789" }],
                [{ text: "💬 استفسار", callback_data: "inquiry" }]
            ]
        }
    });

    res.sendStatus(200);
});

// --- أوامر البوت الأساسية ---
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, '✨ أهلاً بك في متجر الإكسسوارات الحريمي! \nاستخدم القائمة بالأسفل لتصفح الخدمات.', {
        reply_markup: {
            keyboard: [['📦 حالة المخزون', '📊 التقرير اليومي']],
            resize_keyboard: true
        }
    });
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Accessories Store Server is running on port ${PORT}`);
});
