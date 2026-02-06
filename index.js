const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const path = require('path');
const axios = require('axios');

const app = express();
app.use(express.json());

// --- إعداداتك الخاصة (تأكد من صحتها) ---
const TOKEN = "8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk";
const ADMIN_ID = 7020070481;
const CHANNEL_ID = "-1003223634521"; // معرف قناتك

// إعدادات Airtable (الموقع الخارجي للتقارير)
const AIRTABLE_API_KEY = 'YOUR_AIRTABLE_TOKEN'; 
const AIRTABLE_BASE_ID = 'YOUR_BASE_ID';

const bot = new TelegramBot(TOKEN, { polling: true });
app.use(express.static(path.join(__dirname, 'public')));

// --- أزرار التحكم والعمليات ---

// 1. نشر منتج جديد من لوحة التحكم للقناة مباشرة
app.post('/publish', async (req, res) => {
    const { name, price, wholesale, image, cat } = req.body;
    const caption = `💍 **موديل جديد من كاراس وأبو سيفين** ✨\n\n` +
                  `📦 **القطعة:** ${name}\n` +
                  `📂 **القسم:** ${cat}\n` +
                  `💰 **قطاعي:** ${price} ج.م\n` +
                  `🏬 **جملة:** ${wholesale} ج.م\n\n` +
                  `🛒 اطلب الآن عبر السلة في المتجر!`;

    try {
        await bot.sendPhoto(CHANNEL_ID, image, {
            caption: caption,
            parse_mode: 'Markdown',
            reply_markup: {
                inline_keyboard: [[{ text: "💬 مراسلة رامي سمير", url: "https://t.me/RamiSamir" }]]
            }
        });
        res.status(200).send({ success: true });
    } catch (e) { res.status(500).send({ error: e.message }); }
});

// 2. استقبال الطلبات وتسجيلها خارجياً (Airtable) وإرسال تقرير لرامي
app.post('/submit-order', async (req, res) => {
    const { name, phone, items, total, customerType } = req.body;
    
    // تطبيق خصم الجملة (مثلاً 10% تلقائياً)
    let finalTotal = customerType === 'wholesale' ? total * 0.90 : total;

    // تسجيل في Airtable للتقارير اليومية
    try {
        await axios.post(`https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/Orders`, {
            fields: {
                "العميل": name,
                "الهاتف": phone,
                "النوع": customerType,
                "إجمالي الطلب": finalTotal,
                "التاريخ": new Date().toISOString()
            }
        }, { headers: { Authorization: `Bearer ${AIRTABLE_API_KEY}` } });
    } catch (e) { console.log("خطأ في تسجيل التقرير الخارجي"); }

    // إرسال رسالة خاصة لرامي بالطلب
    let orderList = items.map(i => `- ${i.name}`).join('\n');
    let adminMsg = `🚨 **طلب جديد وصل!**\n\n👤 العميل: ${name}\n📞 هاتف: ${phone}\n🏷️ الفئة: ${customerType}\n🛍️ المنتجات:\n${orderList}\n\n💰 الإجمالي النهائي: ${finalTotal} ج.م`;

    bot.sendMessage(ADMIN_ID, adminMsg, {
        reply_markup: { inline_keyboard: [[{ text: "📞 اتصل بالعميل", url: `tel:${phone}` }]] }
    });

    res.json({ success: true, finalTotal });
});

// --- أوامر البوت داخل تليجرام ---
bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "أهلاً بك في بوت إدارة متجر كاراس وأبو سيفين 💍", {
        reply_markup: {
            keyboard: [
                [{ text: "📊 تقرير المبيعات" }, { text: "🛍️ فتح المتجر" }],
                [{ text: "⚙️ الإعدادات" }]
            ], resize_keyboard: true
        }
    });
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`السيرفر يعمل بنجاح على منفذ ${PORT}`));
            
