const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());

// --- إعدادات الربط النهائية والمؤكدة ---
const TOKEN = "8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk"; // توكن البوت الخاص بك
const ADMIN_ID = 7020070481; // معرف رامي سمير (المدير العام)
const CHANNEL_ID = "-1003223634521"; // معرف القناة الصحيح

const bot = new TelegramBot(TOKEN, { polling: true });

// خدمة ملفات الواجهة من مجلد public
app.use(express.static(path.join(__dirname, 'public')));

// 1. استقبال بيانات النشر من لوحة التحكم (HTML) إلى القناة
app.post('/publish', (req, res) => {
    const { name, price, wholesale, image, cat, size } = req.body;
    
    const caption = `✨ **موديل جديد وصل في رامي سمير Gold** ✨\n\n` +
                  `💍 **القطعة:** ${name}\n` +
                  `🏷️ **الخامة:** ${size || 'استانلس ستيل'}\n` +
                  `📂 **القسم:** ${cat}\n\n` +
                  `💰 **سعر القطاعي:** ${price} ج.م\n` +
                  `📦 **سعر الجملة:** ${wholesale} ج.م\n\n` +
                  `🛍️ كاراس وأبو سيفين للاستيراد`;

    bot.sendPhoto(CHANNEL_ID, image, {
        caption: caption,
        parse_mode: 'Markdown',
        reply_markup: {
            inline_keyboard: [
                [{ text: "🛒 اطلب عبر واتساب", url: "https://wa.me/20123456789" }],
                [{ text: "💬 مراسلة رامي سمير", url: "https://t.me/RamiSamir" }]
            ]
        }
    }).then(() => {
        res.status(200).send({ success: true });
    }).catch((err) => {
        console.error("خطأ في النشر:", err);
        res.status(500).send({ error: "فشل النشر في القناة" });
    });
});

// 2. استقبال طلبات السلة من العملاء وإرسالها لرامي (خاص)
app.post('/submit-order', (req, res) => {
    const { name, phone, items, total } = req.body;
    
    let orderMsg = `🚨 **طلب شراء جديد (كاراس وأبو سيفين)**\n\n👤 العميل: ${name}\n📞 هاتف: ${phone}\n\nالمنتجات:\n`;
    items.forEach((i, index) => orderMsg += `${index + 1}- ${i.title} (${i.price} ج.م)\n`);
    orderMsg += `\n💰 الإجمالي: ${total}`;

    bot.sendMessage(ADMIN_ID, orderMsg, {
        reply_markup: {
            inline_keyboard: [[{ text: "📞 اتصال بالعميل", url: `tel:${phone}` }]]
        }
    });
    res.sendStatus(200);
});

// 3. أوامر البوت الأساسية
bot.onText(/\/start/, (msg) => {
    const welcomeMsg = msg.from.id === ADMIN_ID ? 
        "أهلاً يا رامي! يمكنك التحكم في المتجر ونشر المنتجات عبر لوحة الويب." :
        "مرحباً بك في متجر رامي سمير Gold ✨\nتصفح المنتجات واطلب عبر السلة الملحقة.";
    
    bot.sendMessage(msg.chat.id, welcomeMsg);
});

// تشغيل السيرفر على المنفذ 8000 ليتوافق مع Koyeb
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
