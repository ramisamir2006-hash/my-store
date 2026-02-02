const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080; // ضروري جداً لـ Koyeb

// تشغيل واجهة الويب (إذا كان لديك ملفات في public)
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => res.send('مدير المتجر يعمل بنجاح!'));

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

// إعداد البوت المدير
const token = process.env.TELEGRAM_TOKEN; // اجلبه من إعدادات Koyeb وليس الكود
const bot = new TelegramBot(token, { polling: true });

// الأوامر التي ظهرت في صورتك
bot.onText(/\/start/, (msg) => {
    const opts = {
        reply_markup: {
            keyboard: [
                ['📊 تقارير', '➕ إضافة منتج'],
                ['📂 أقسام', '💡 تسويق']
            ],
            resize_keyboard: true
        }
    };
    bot.sendMessage(msg.chat.id, "أهلاً بك في لوحة تحكم my-store 💎\nاختر من الأزرار بالأسفل:", opts);
});

// التعامل مع الأزرار
bot.on('message', (msg) => {
    if (msg.text === '📊 تقارير') {
        bot.sendMessage(msg.chat.id, "جاري تحضير التقارير...");
    }
    // يمكنك إضافة باقي المهام هنا
});
