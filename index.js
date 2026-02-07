const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

// --- إعداد السيرفر لضمان عمل الخدمة (إصلاح Build Error) ---
const app = express();
app.use(bodyParser.json());
app.use(express.static('public'));

// --- بياناتك الشخصية المدمجة ---
const token = '8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk'; // توكن المدير التنفيذي
const channelId = '-1003223634521'; // معرف القناة الخاص بك
const channelUrl = 'https://t.me/RamySamir2026Gold';

const bot = new TelegramBot(token, { polling: true });

// ربط Airtable (تأكد من وجود المتغيرات AIRTABLE_API_KEY و BASE_ID في Koyeb)
const base = new Airtable({ 
    apiKey: process.env.AIRTABLE_API_KEY 
}).base(process.env.BASE_ID);

// فتح لوحة التحكم عند زيارة رابط السيرفر
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// استقبال طلبات النشر من لوحة التحكم (HTML)
app.post('/publish', async (req, res) => {
    const data = req.body;
    
    const caption = `💍 *موديل جديد: متجر رامي سمير* 💍\n\n` +
                    `📝 *الصنف:* ${data.name}\n` +
                    `🏷️ *القسم:* ${data.category}\n` +
                    `📏 *المقاسات:* ${data.size}\n\n` +
                    `💰 *قطاعي:* ${data.price} ج.م\n` +
                    `🏬 *جملة:* ${data.wholesale} ج.م\n` +
                    `🎁 *الخصم:* ${data.discount}%\n\n` +
                    `✅ [تصفح المعرض الكامل من هنا](${channelUrl})\n` +
                    `📞 للطلب والاستفسار: @RamySamir2026`;

    try {
        if (data.images && data.images.length > 1) {
            const mediaGroup = data.images.map((url, index) => ({
                type: 'photo',
                media: url,
                caption: index === 0 ? caption : '',
                parse_mode: 'Markdown'
            }));
            await bot.sendMediaGroup(channelId, mediaGroup);
        } else if (data.images && data.images.length === 1) {
            await bot.sendPhoto(channelId, data.images[0], { caption, parse_mode: 'Markdown' });
        }
        res.json({ success: true });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

app.listen(process.env.PORT || 8000, () => {
    console.log('نظام رامي سمير يعمل بنجاح');
});
