const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

// --- إعداد السيرفر ---
const app = express();
app.use(bodyParser.json());
app.use(express.static('public')); // تأكد من وضع ملف HTML داخل مجلد اسمه public

// --- بيانات الربط الخاصة بك ---
const token = '8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk';
const channelId = '-1003223634521';
const channelUrl = 'https://t.me/RamySamir2026Gold';

const bot = new TelegramBot(token, { polling: true });

// ربط Airtable (تأكد من إضافة المتغيرات في إعدادات Koyeb)
const base = new Airtable({ 
    apiKey: process.env.AIRTABLE_API_KEY 
}).base(process.env.BASE_ID);

// --- تشغيل السيرفر لإصلاح مشكلة Unhealthy ---
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(process.env.PORT || 8000, () => {
    console.log('سيرفر متجر رامي يعمل على المنفذ 8000');
});

// --- استقبال طلبات النشر من لوحة التحكم ---
app.post('/publish', async (req, res) => {
    const data = req.body;
    
    const caption = `💍 *موديل جديد من متجر رامي* 💍\n\n` +
                    `📝 *اسم المنتج:* ${data.name}\n` +
                    `🏷️ *القسم:* ${data.category}\n` +
                    `📏 *المقاسات:* ${data.size}\n\n` +
                    `💰 *السعر قطاعي:* ${data.price} ج.م\n` +
                    `🏬 *السعر جملة:* ${data.wholesale} ج.م\n` +
                    `🎁 *الخصم:* ${data.discount}%\n\n` +
                    `✅ [اضغط هنا للدخول للمعرض](${channelUrl})\n` +
                    `📞 للطلب تواصل مع المدير: @RamySamir2026`;

    try {
        if (data.images.length > 1) {
            const mediaGroup = data.images.map((url, index) => ({
                type: 'photo',
                media: url,
                caption: index === 0 ? caption : '',
                parse_mode: 'Markdown'
            }));
            await bot.sendMediaGroup(channelId, mediaGroup);
        } else {
            await bot.sendPhoto(channelId, data.images[0], { caption, parse_mode: 'Markdown' });
        }
        res.json({ success: true });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

// --- أوامر البوت الأساسية ---
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, `مرحباً بك في نظام رامي سمير الذكي ✨\nيمكنك استخدام لوحة التحكم لإضافة المنتجات.`);
});
