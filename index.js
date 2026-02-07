const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());
app.use(express.static('public')); // لتشغيل ملفات HTML من مجلد public

// بياناتك الأساسية
const token = '8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk';
const channelId = '-1003223634521';
const bot = new TelegramBot(token, { polling: true });

// تشغيل السيرفر
app.listen(process.env.PORT || 8000);

// استقبال طلب النشر من لوحة التحكم
app.post('/publish', async (req, res) => {
    const data = req.body;
    
    // تنسيق الرسالة التسويقية
    const message = `✨ *موديل جديد في متجر رامي* ✨\n\n` +
                    `📦 *المنتج:* ${data.name}\n` +
                    `🗂️ *القسم:* ${data.category}\n` +
                    `📏 *المقاسات:* ${data.size}\n\n` +
                    `💰 *السعر:* ${data.price} ج.م\n` +
                    `🏬 *سعر الجملة:* ${data.wholesale} ج.م\n` +
                    `🎁 *خصم:* ${data.discount}%\n\n` +
                    `🔗 [لطلب المنتج أو الاستفسار](https://t.me/RamySamir2026Gold)`;

    try {
        if (data.images.length > 1) {
            // نشر مجموعة صور
            const mediaGroup = data.images.map((url, index) => ({
                type: 'photo',
                media: url,
                caption: index === 0 ? message : '',
                parse_mode: 'Markdown'
            }));
            await bot.sendMediaGroup(channelId, mediaGroup);
        } else if (data.images.length === 1) {
            // نشر صورة واحدة
            await bot.sendPhoto(channelId, data.images[0], { caption: message, parse_mode: 'Markdown' });
        }
        res.json({ success: true });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});
