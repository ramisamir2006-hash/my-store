const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// 1. إعداد السيرفر ليعمل على Koyeb أو Render
const app = express();
const port = process.env.PORT || 8000;
app.get('/', (req, res) => res.send('سيرفر متجر رامي يعمل بنجاح!'));
app.listen(port, () => console.log(`السيرفر يعمل على منفذ ${port}`));

// 2. ربط Airtable بالبيانات التي ستضعها في الإعدادات
const base = new Airtable({
    apiKey: process.env.AIRTABLE_API_KEY 
}).base(process.env.BASE_ID);

// 3. ربط البوت بالتوكن الخاص بك (8395659007)
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

// 4. القائمة الرئيسية باللغة العربية (كما في طلبك)
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة للسلة', callback_data: 'add_to_cart' }],
                [{ text: '🏪 فتح المتجر (المعرض)', url: 'https://t.me/your_channel_link' }],
                [{ text: '💬 استفسار / مساعدة', callback_data: 'help' }],
                [{ text: '📋 عرض السلة', callback_data: 'view_cart' }]
            ]
        }
    };
    bot.sendMessage(chatId, `مرحباً بك يا ${msg.from.first_name} في متجر ماريا للذهب الصيني ✨\n\nكيف يمكننا مساعدتك اليوم؟`, opts);
});

// 5. معالجة الضغط على الأزرار
bot.on('callback_query', async (callbackQuery) => {
    const msg = callbackQuery.message;
    const data = callbackQuery.data;

    if (data === 'add_to_cart') {
        bot.sendMessage(msg.chat.id, "لطفاً، أرسل بياناتك لحفظ الطلب بالتنسيق التالي:\nالاسم - رقم الهاتف - النوع (جملة/قطاعي)");
    }

    if (data === 'help') {
        bot.sendMessage(msg.chat.id, "يمكنك التواصل مع الدعم الفني للمتجر من هنا: @YourUsername");
    }
});

// 6. استقبال الرسائل وحفظها في جدول "مبيعات رامي"
bot.on('message', async (msg) => {
    const text = msg.text;
    
    // التحقق إذا كان المستخدم يرسل بيانات الطلب (يحتوي على شرطة)
    if (text && text.includes('-')) {
        const details = text.split('-');
        const name = details[0].trim();
        const phone = details[1].trim();
        const type = details[2] ? details[2].trim() : "قطاعي";

        try {
            await base('مبيعات رامي').create([{
                "fields": {
                    "العميل": name,
                    "الهاتف": phone,
                    "النوع": type
                }
            }]);
            bot.sendMessage(msg.chat.id, `✅ تم استلام طلبك يا ${name} وحفظه في جدول المبيعات بنجاح!`);
        } catch (error) {
            console.error("خطأ في Airtable:", error);
            bot.sendMessage(msg.chat.id, "❌ عذراً، حدث خطأ أثناء الاتصال بجدول البيانات.");
        }
    }
});
                    
