const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
app.use(express.json());

const TOKEN = "8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk";
const ADMIN_ID = 7020070481;
const CHANNEL_ID = "-1003223634521";

// مفاتيح Airtable التي جهزتها أنت في الصور
const AIRTABLE_API_KEY = 'YOUR_AIRTABLE_TOKEN'; 
const AIRTABLE_BASE_ID = 'YOUR_BASE_ID';

const bot = new TelegramBot(TOKEN, { polling: true });
app.use(express.static(path.join(__dirname, 'public')));

// دالة توليد الوصف التسويقي التلقائي لكل قسم
function generateDescription(category, name) {
    const templates = {
        "خواتم": `✨ تألقي بسحر الأناقة مع خاتم ${name}. تصميم يجمع بين الفخامة والرقي ليناسب كل لحظاتك السعيدة. 💍`,
        "سلاسل": `📿 لمسة جمالية تلتف حول عنقك.. سلسلة ${name} المستوردة، بريق لا ينطفئ وتصميم يخطف الأنظار.`,
        "انسيال": `💫 معصمك يستحق هذا الدلال! انسيال ${name} بلمعته الخاصة التي تزيدك جاذبية في كل حركة.`,
        "أساور": `🌟 أساور ${name}.. عنوان الفخامة والجمال. قطعة فريدة تعكس ذوقك الرفيع وتكمل إطلالتك.`,
        "حلق": `👂 ابهري الجميع مع حلق ${name}. بريق استثنائي يضيف لمسة من السحر على وجهك الجميل.`,
        "غوايش": `👑 غوايش ${name} الأصلية.. متانة وفخامة تدوم طويلاً. زينة المرأة العربية الأصيلة.`,
        "طقم": `💎 طقم ${name} المتكامل.. لأناقة ملكية لا مثيل لها. المجموعة التي تحلم بها كل امرأة.`,
        "خلخال": `👣 خلخال ${name}.. رقة وأنوثة في كل خطوة. تصميم عصري يناسب إطلالات الصيف المبهجة.`
    };
    return templates[category] || `قطعة ${name} الفريدة من متجرنا، جودة استيراد وسعر لا يقاوم. ✨`;
}

// 🚀 زر التحكم: نشر المنتج للقناة مع كافة التفاصيل
app.post('/publish', async (req, res) => {
    const { name, price, wholesale, images, cat, size, discount } = req.body;
    
    const finalPrice = discount ? price - (price * (discount/100)) : price;
    const autoDesc = generateDescription(cat, name);

    const caption = `💍 **موديل جديد من كاراس وأبو سيفين** ✨\n\n` +
                  `📦 **الصنف:** ${name}\n` +
                  `📂 **القسم:** ${cat}\n` +
                  `📏 **المقاسات:** ${size || 'متوفر كافة المقاسات'}\n` +
                  `📝 **الوصف:** ${autoDesc}\n\n` +
                  `💰 **السعر القطاعي:** ${finalPrice} ج.م ${discount ? `(خصم ${discount}%)` : ''}\n` +
                  `🏬 **سعر الجملة:** ${wholesale} ج.م\n\n` +
                  `📣 **حملة خاصة:** شحن مجاني لأول 5 طلبات! 🚚\n\n` +
                  `🛒 اطلب الآن عبر الخاص: @RamiSamir`;

    try {
        // إرسال أكثر من صورة كمجموعة (Album)
        const mediaGroup = images.map((img, index) => ({
            type: 'photo',
            media: img,
            caption: index === 0 ? caption : '',
            parse_mode: 'Markdown'
        }));

        await bot.sendMediaGroup(CHANNEL_ID, mediaGroup);
        res.status(200).send({ success: true });
    } catch (e) { res.status(500).send({ error: e.message }); }
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`السيرفر يعمل بنجاح` ));
