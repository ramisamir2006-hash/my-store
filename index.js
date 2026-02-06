const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());

// --- الإعدادات النهائية لقناتك ---
const TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE";
const ADMIN_ID = 7020070481; // رامي سمير
const CHANNEL_USERNAME = "@RamySamir2026Gold"; // معرف قناتك الجديد

const bot = new TelegramBot(TOKEN, { polling: true });

// استقبال بيانات النشر من لوحة التحكم HTML
app.post('/publish', (req, res) => {
    const { name, price, wholesale, image, cat, size } = req.body;
    
    // تنسيق الرسالة لتناسب "مجوهرات رامي سمير Gold"
    const caption = `✨ **موديل جديد وصل الآن في رامي سمير Gold** ✨\n\n` +
                  `💍 **القطعة:** ${name}\n` +
                  `🏷️ **الخامة:** ${size}\n` +
                  `📂 **القسم:** ${cat}\n\n` +
                  `💰 **سعر القطاعي:** ${price} ج.م\n` +
                  `📦 **سعر الجملة:** ${wholesale} ج.م\n\n` +
                  `🛍️ للطلب والاستفسار تواصل معنا مباشرة!`;

    // النشر التلقائي في القناة
    bot.sendPhoto(CHANNEL_USERNAME, image, {
        caption: caption,
        parse_mode: 'Markdown',
        reply_markup: {
            inline_keyboard: [
                [{ text: "🛒 اطلب عبر واتساب", url: "https://wa.me/20123456789" }],
                [{ text: "💬 مراسلة رامي سمير", url: "https://t.me/RamiSamir" }]
            ]
        }
    });

    res.status(200).send({ success: true });
});

// استقبال طلبات السلة من العملاء
app.post('/submit-order', (req, res) => {
    const { name, phone, items, total } = req.body;
    let orderMsg = `🚨 **طلب شراء جديد من المتجر**\n\n👤 العميل: ${name}\n📞 هاتف: ${phone}\n\nالمنتجات:\n`;
    items.forEach(i => orderMsg += `- ${i.title} (${i.price} ج.م)\n`);
    orderMsg += `\n💰 الإجمالي: ${total}`;

    bot.sendMessage(ADMIN_ID, orderMsg);
    res.sendStatus(200);
});

app.use(express.static(path.join(__dirname, 'public')));
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
