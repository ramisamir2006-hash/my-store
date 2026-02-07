const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

// إعدادات السيرفر لمنصة Render
const app = express();
const port = process.env.PORT || 8000;
app.get('/', (req, res) => res.send('لوحة تحكم متجر رامي نشطة!'));
app.listen(port, () => console.log(`السيرفر يعمل على منفذ ${port}`));

// ربط Airtable (تأكد من إضافة المتغيرات في Settings)
const base = new Airtable({apiKey: process.env.AIRTABLE_API_KEY}).base(process.env.BASE_ID);
const TABLE_NAME = "مبيعات رامي";

// ربط البوت (استخدام التوكن من الصورة 8395659007)
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

// --- 1. قائمة التحكم الرئيسية (لصاحب البوت) ---
bot.onText(/\/admin/, (msg) => {
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🚀 نشر منتج فوري للقناة', callback_data: 'publish_post' }],
                [{ text: '📊 عرض مبيعات رامي', url: `https://airtable.com/${process.env.BASE_ID}` }],
                [{ text: '🔧 إعدادات البوت', callback_data: 'settings' }]
            ]
        }
    };
    bot.sendMessage(msg.chat.id, "🛠️ أهلاً بك يا رامي في لوحة الإدارة:", opts);
});

// --- 2. أزرار المتجر للمستخدمين (كما في صورتك) ---
bot.onText(/\/start/, (msg) => {
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة للسلة', callback_data: 'add_to_cart' }],
                [{ text: '🏪 فتح المتجر (المعرض)', url: 'https://t.me/your_channel_name' }], // استبدل برابط قناتك
                [{ text: '💬 استفسار / مساعدة', callback_data: 'help' }],
                [{ text: '📜 عرض السلة', callback_data: 'view_cart' }]
            ]
        }
    };
    bot.sendMessage(msg.chat.id, "✨ مرحباً بك في متجرنا! استخدم الأزرار أدناه للتسوق:", opts);
});

// --- 3. معالجة الأوامر والأزرار ---
bot.on('callback_query', async (callbackQuery) => {
    const chatId = callbackQuery.message.chat.id;
    const data = callbackQuery.data;

    if (data === 'add_to_cart') {
        bot.sendMessage(chatId, "📝 لإتمام الطلب، أرسل بياناتك كالتالي:\nالأسم - الهاتف - النوع (جملة/قطاعي)");
    }

    if (data === 'publish_post') {
        bot.sendMessage(chatId, "📤 أرسل صورة المنتج مع الوصف والسعر ليتم نشرها فوراً في القناة.");
    }
    
    if (data === 'help') {
        bot.sendMessage(chatId, "🤝 للدعم الفني تواصل مع: @YourUsername");
    }
});

// --- 4. وظيفة الحفظ التلقائي في Airtable ونشر القناة ---
bot.on('message', async (msg) => {
    const text = msg.text;
    const chatId = msg.chat.id;

    // حفظ البيانات في Airtable إذا كانت تحتوي على شرطة "-"
    if (text && text.includes('-')) {
        const parts = text.split('-');
        if (parts.length >= 2) {
            const name = parts[0].trim();
            const phone = parts[1].trim();
            const type = parts[2] ? parts[2].trim() : "قطاعي";

            try {
                await base(TABLE_NAME).create([{
                    "fields": {
                        "العميل": name,
                        "الهاتف": phone,
                        "النوع": type
                    }
                }]);
                bot.sendMessage(chatId, `✅ تم تسجيل طلبك بنجاح في جدول "مبيعات رامي".`);
            } catch (e) {
                bot.sendMessage(chatId, "❌ خطأ في الاتصال بـ Airtable.");
            }
        }
    }
    
    // وظيفة النشر التلقائي للقناة (إذا أرسل المسؤول صورة)
    if (msg.photo && msg.caption) {
        const channelId = "@your_channel_id"; // ضع معرف قناتك هنا يبدأ بـ @
        bot.sendPhoto(channelId, msg.photo[msg.photo.length - 1].file_id, {
            caption: msg.caption,
            reply_markup: {
                inline_keyboard: [
                    [{ text: '🛒 إضافة للسلة', callback_data: 'add_to_cart' }],
                    [{ text: '🏪 فتح المتجر (المعرض)', url: 'https://t.me/your_channel_name' }]
                ]
            }
        });
        bot.sendMessage(chatId, "🚀 تم نشر المنتج في القناة بنجاح مع أزرار الشراء!");
    }
});
            
