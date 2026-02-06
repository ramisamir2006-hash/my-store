const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const path = require('path');

const app = express();
app.use(express.json());

// --- الإعدادات الثابتة ---
const TOKEN = "8234943697:AAEKiDTuNJMgBF7XySjvimPzHcPRrIo_DuE";
const ADMIN_ID = 7020070481; // معرف رامي سمير
const CHANNEL_ID = "-1003223634521"; // معرف القناة

const bot = new TelegramBot(TOKEN, { polling: true });

// --- 1. لوحات التحكم (Keyboards) ---

const adminKeyboard = {
    reply_markup: {
        keyboard: [
            [{ text: "📊 التقارير اليومية" }, { text: "📦 إدارة الطلبات" }],
            [{ text: "👥 الموظفين" }, { text: "➕ إضافة منتج جديد" }],
            [{ text: "💰 ضبط الخصومات" }, { text: "🛍️ فتح المتجر" }]
        ],
        resize_keyboard: true
    }
};

const userKeyboard = {
    reply_markup: {
        keyboard: [
            [{ text: "🛍️ دخول المتجر" }],
            [{ text: "📞 الدعم الفني" }]
        ],
        resize_keyboard: true
    }
};

// --- 2. معالجة الأوامر ---

bot.onText(/\/start/, (msg) => {
    const userId = msg.from_user.id;
    if (userId === ADMIN_ID) {
        bot.sendMessage(msg.chat.id, "أهلاً يا رامي! لوحة الإدارة العامة جاهزة للعمل.", adminKeyboard);
    } else {
        bot.sendMessage(msg.chat.id, "مرحباً بك في مجوهرات رامي سمير ✨\nتفضل بتصفح أحدث الموديلات عبر المتجر.", userKeyboard);
    }
});

// معالجة الضغط على الأزرار
bot.on('message', (msg) => {
    const text = msg.text;
    const chatId = msg.chat.id;

    if (text === "📊 التقارير اليومية" && msg.from_user.id === ADMIN_ID) {
        bot.sendMessage(chatId, "📈 تقرير اليوم:\n- المبيعات: 0\n- الطلبات الجديدة: 0");
    }
    
    if (text === "🛍️ دخول المتجر") {
        bot.sendMessage(chatId, "يمكنك تصفح المنتجات عبر قناتنا الرسمية مباشرة، أو انتظر إطلاق الكتالوج التفاعلي هنا قريباً.");
    }
});

// --- 3. استقبال البيانات من لوحة التحكم (HTML) ---
app.post('/publish', (req, res) => {
    const { name, price, discRetail, discWholesale, image, cat, size } = req.body;
    
    const retailFinal = price - (price * (discRetail / 100));

    const caption = `✨ **قطعة مجوهرات جديدة من رامي سمير** ✨\n\n` +
                  `💍 **النوع:** ${name}\n` +
                  `🎨 **المادة:** ${size}\n` +
                  `📂 **القسم:** ${cat}\n\n` +
                  `💰 **السعر:** ${retailFinal} ج.م\n\n` +
                  `🛍️ اطلب الآن عبر الخاص!`;

    bot.sendPhoto(CHANNEL_ID, image, {
        caption: caption,
        parse_mode: 'Markdown',
        reply_markup: {
            inline_keyboard: [[{ text: "🛒 اطلب الآن", url: "https://t.me/RamiSamir" }]]
        }
    });

    res.sendStatus(200);
});

// --- تشغيل السيرفر لـ Koyeb ---
app.use(express.static(path.join(__dirname, 'public')));
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Server started on port ${PORT}`));
