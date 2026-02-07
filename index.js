const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// إعدادات السيرفر لـ Render
const app = express();
const port = process.env.PORT || 8000;
app.get('/', (req, res) => res.send('بوت متجر رامي يعمل بنجاح!'));
app.listen(port, () => console.log(`السيرفر يعمل على منفذ ${port}`));

// ربط Airtable
const base = new Airtable({apiKey: process.env.AIRTABLE_API_KEY}).base(process.env.BASE_ID);
const TABLE_NAME = "مبيعات رامي"; // نفس الاسم في صورتك

// ربط البوت
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

// 1. القائمة الرئيسية (أزرار التحكم في البوت)
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛍️ فتح المتجر (المعرض)', url: 'https://t.me/your_channel_link' }],
                [{ text: '🛒 إضافة طلب جديد', callback_data: 'add_order' }],
                [{ text: '📢 التحكم بالقناة', callback_data: 'channel_control' }],
                [{ text: '❓ استفسار / مساعدة', callback_data: 'help' }]
            ]
        }
    };
    bot.sendMessage(chatId, `أهلاً بك يا ${msg.from.first_name} في لوحة تحكم متجر رامي.`, opts);
});

// 2. معالجة ضغطات الأزرار
bot.on('callback_query', async (callbackQuery) => {
    const msg = callbackQuery.message;
    const data = callbackQuery.data;

    if (data === 'add_order') {
        bot.sendMessage(msg.chat.id, "من فضلك أرسل اسم العميل ورقم الهاتف بهذا الشكل:\nالاسم - الرقم - النوع(جملة/قطاعي)");
    }

    if (data === 'channel_control') {
        bot.sendMessage(msg.chat.id, "إعدادات القناة:\n1. نشر منتج جديد\n2. إرسال عرض خاص\n(يمكنك ربط هذه الأزرار بوظائف النشر التلقائي)");
    }
});

// 3. استقبال البيانات وحفظها في جدول "مبيعات رامي"
bot.on('message', async (msg) => {
    const text = msg.text;
    if (text && text.includes('-')) {
        const details = text.split('-');
        const name = details[0].trim();
        const phone = details[1].trim();
        const type = details[2] ? details[2].trim() : "قطاعي";

        try {
            await base(TABLE_NAME).create([
                {
                    "fields": {
                        "العميل": name,
                        "الهاتف": phone,
                        "النوع": type
                    }
                }
            ]);
            bot.sendMessage(msg.chat.id, `✅ تم تسجيل البيانات بنجاح في جدول "مبيعات رامي":\n👤 العميل: ${name}\n📞 الهاتف: ${phone}\n🏷️ النوع: ${type}`);
        } catch (error) {
            console.error(error);
            bot.sendMessage(msg.chat.id, "❌ حدث خطأ أثناء الحفظ. تأكد من إعدادات الـ API و Base ID.");
        }
    }
});
