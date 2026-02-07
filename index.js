const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());
app.use(express.static('public'));

const token = '8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk';
const channelId = '-1003223634521';
const bot = new TelegramBot(token, { polling: true });

app.get('/', (req, res) => {
    res.send('نظام رامي سمير يعمل بنجاح! السيرفر نشط.');
});

app.post('/publish', async (req, res) => {
    const { name, price, images } = req.body;
    const caption = `💍 *منتج جديد من متجر رامي*\n📝 الاسم: ${name}\n💰 السعر: ${price} ج.م`;
    
    try {
        if (images && images.length > 0) {
            await bot.sendPhoto(channelId, images[0], { caption, parse_mode: 'Markdown' });
            res.json({ success: true });
        }
    } catch (e) {
        res.status(500).json({ success: false, error: e.message });
    }
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
