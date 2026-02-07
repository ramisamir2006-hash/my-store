const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// إعداد خادم ويب بسيط لإصلاح مشكلة Service unhealthy في Koyeb
const app = express();
app.get('/', (req, res) => res.send('سيرفر متجر رامي يعمل!'));
app.listen(process.env.PORT || 8000);

// إعدادات الربط - تستخدم المتغيرات لضمان الأمان
const base = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY }).base(process.env.BASE_ID);
const bot = new TelegramBot('8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk', { polling: true });

// بيانات المتجر الخاصة بك
const CHANNEL_ID = '-1003223634521';
const CHANNEL_URL = 'https://t.me/RamySamir2026Gold';

// القائمة الرئيسية للبوت
bot.onText(/\/start/, (msg) => {
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة طلب جديد', callback_data: 'start_order' }],
                [{ text: '🏪 دخول معرض الذهب (القناة)', url: CHANNEL_URL }],
                [{ text: '📞 الدعم الفني', callback_data: 'help' }]
            ]
        }
    };
    bot.sendMessage(msg.chat.id, `✨ مرحباً بك في بوت متجر رامي للذهب الصيني ✨\nيمكنك تصفح المعرض أو البدء بالطلب أدناه:`, opts);
});

// نظام إدارة الطلبات (قطاعي وجملة)
bot.on('callback_query', async (query) => {
    const chatId = query.message.chat.id;
    if (query.data === 'start_order') {
        bot.sendMessage(chatId, "يرجى تحديد نوع البيع:\n1️⃣ للقطاعي أرسل بياناتك: (اسمك - رقمك - اسم المنتج)\n2️⃣ للجملة أرسل: (جملة - اسمك - رقمك)");
    }
    if (query.data === 'help') {
        bot.sendMessage(chatId, "للتواصل مع المدير التنفيذي مباشرة: @RamySamir2026");
    }
});

// حفظ الطلبات في Airtable وإرسال إشعار للمدير
bot.on('message', async (msg) => {
    if (msg.text && msg.text.includes('-')) {
        const details = msg.text.split('-');
        try {
            await base('مبيعات رامي').create([{
                "fields": {
                    "العميل": details[0].trim(),
                    "الهاتف": details[1].trim(),
                    "التفاصيل": details[2] ? details[2].trim() : "طلب عام"
                }
            }]);
            bot.sendMessage(msg.chat.id, "✅ تم تسجيل طلبك بنجاح! سيتم التواصل معك من قبل الإدارة.");
            
            // إشعار للقناة أو المدير (اختياري)
            bot.sendMessage(CHANNEL_ID, `🔔 طلب جديد من: ${details[0].trim()}\n📱 هاتف: ${details[1].trim()}`);
        } catch (e) {
            bot.sendMessage(msg.chat.id, "❌ خطأ في حفظ البيانات، تأكد من إعدادات Airtable.");
        }
    }
});
