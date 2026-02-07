const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const cron = require('node-cron'); // مكتبة الجدولة الزمنية

const TOKEN = "8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk";
const CHANNEL_ID = "-1003223634521";
const bot = new TelegramBot(TOKEN, { polling: true });
const app = express();
app.use(express.json());

// مخزن مؤقت للمنتجات المجدولة للحملات الإعلانية
let adQueue = [];

// دالة توليد الوصف التسويقي التلقائي (الاحترافي)
function generateAutoDescription(category, name) {
    const ads = {
        "شويكار": `✨ موديل شويكار الراقي.. قطعة فنية تمنحك إطلالة الأميرات. ${name} بجودة استيراد لا تضاهى.`,
        "برسن": `💎 تألقي بلمسة البرسن الفريدة.. ${name} مصمم خصيصاً لمن تعشق التميز والاختلاف.`,
        "خلخال": `👣 رقة وأنوثة في كل خطوة مع خلخال ${name}. الجمال يبدأ من التفاصيل البسيطة.`,
        "انسيال": `💫 معصمك يستحق هذا الدلال! انسيال ${name} بلمعته الخاصة التي تزيدك جاذبية.`,
        "طقم": `👑 الفخامة الكاملة في طقم ${name}. المجموعة المثالية للمناسبات السعيدة والهدايا الراقية.`
    };
    return ads[category] || `قطعة ${name} المميزة.. جودة عالية وتصميم عصري يناسب ذوقك الرفيع. ✨`;
}

// نظام الجدولة: نشر منتج من الطابور كل ساعتين تلقائياً
cron.schedule('0 */2 * * *', async () => {
    if (adQueue.length > 0) {
        const product = adQueue.shift(); // سحب أول منتج في القائمة
        await publishToTelegram(product);
        console.log("تم نشر حملة إعلانية مجدولة بنجاح");
    }
});

async function publishToTelegram(p) {
    const finalPrice = p.discount ? p.price - (p.price * (p.discount/100)) : p.price;
    const desc = generateAutoDescription(p.cat, p.name);
    
    const caption = `💍 **إصدار جديد من متجر كاراس وأبو سيفين** ✨\n\n` +
                  `📦 **الموديل:** ${p.name}\n` +
                  `📂 **القسم:** ${p.cat}\n` +
                  `📏 **المقاس:** ${p.size || 'متوفر جميع المقاسات'}\n` +
                  `📝 **الوصف:** ${desc}\n\n` +
                  `💰 **السعر:** ${finalPrice} ج.م ${p.discount ? `(خصم ${p.discount}%)` : ''}\n` +
                  `🏬 **جملة:** ${p.wholesale} ج.م\n\n` +
                  `🛒 للطلب والاستفسار: @RamiSamir\n` +
                  `🚚 شحن سريع لكافة المحافظات!`;

    if (p.images.length > 1) {
        const media = p.images.map((img, i) => ({ type: 'photo', media: img, caption: i === 0 ? caption : '', parse_mode: 'Markdown' }));
        await bot.sendMediaGroup(CHANNEL_ID, media);
    } else {
        await bot.sendPhoto(CHANNEL_ID, p.images[0], { caption, parse_mode: 'Markdown' });
    }
}

// أزرار التحكم: نشر فوري أو إضافة للجدولة
app.post('/publish-now', async (req, res) => {
    await publishToTelegram(req.body);
    res.send({ success: true });
});

app.post('/add-to-ads', (req, res) => {
    adQueue.push(req.body);
    res.send({ success: true, queueLength: adQueue.length });
});

app.listen(8000, () => console.log("السيرفر يعمل..."));
