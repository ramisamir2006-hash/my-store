const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const path = require('path');

const app = express();
// تصحيح: يجب قراءة المنفذ من Koyeb لكي تصبح الخدمة Healthy
const PORT = process.env.PORT || 8080;

app.use(express.static(path.join(__dirname, 'public')));
app.get('/', (req, res) => res.send('لوحة تحكم my-store نشطة وتعمل!'));

app.listen(PORT, () => console.log(`سيرفر الويب يعمل على المنفذ ${PORT}`));

// التأكد من وجود التوكن
const token = process.env.TELEGRAM_TOKEN;
if (!token) {
    console.error("خطأ قاتل: TELEGRAM_TOKEN غير موجود في إعدادات Koyeb!");
} else {
    const bot = new TelegramBot(token, { polling: true });

    // --- لوحة تحكم المدير ---
    const adminKeyboard = {
        reply_markup: {
            keyboard: [
                ['➕ إضافة قسم جديد', '📦 عرض المخزون'],
                ['➕ إضافة منتج جديد', '🖼️ عرض المنتجات'],
                ['📊 التقارير', '🎟️ نظام الخصومات'],
                ['👥 العملاء', '📢 حملة إعلانية']
            ],
            resize_keyboard: true
        }
    };

    bot.onText(/\/start/, (msg) => {
        bot.sendMessage(msg.chat.id, "أهلاً بك يا مدير! تم تفعيل نظام الإدارة الشامل:", adminKeyboard);
    });

    bot.on('message', (msg) => {
        const chatId = msg.chat.id;
        const text = msg.text;

        switch (text) {
            case '📊 التقارير':
                bot.sendMessage(chatId, `📈 التقرير اليومي:\n- طلبات جديدة: 5\n- زوار: 42\n- وقت الذروة: 10 مساءً`);
                break;
            case '👥 العملاء':
                bot.sendMessage(chatId, "اختر طريقة التواصل مع العملاء:", {
                    reply_markup: {
                        inline_keyboard: [
                            [{ text: "رسالة جماعية (الكل)", callback_data: 'msg_all' }],
                            [{ text: "رسالة لعميل محدد", callback_data: 'msg_one' }]
                        ]
                    }
                });
                break;
            case '🎟️ نظام الخصومات':
                bot.sendMessage(chatId, "أرسل كود الخصم ونسبة الخصم (مثال: SAVE20 - 20%)");
                break;
            case '📢 حملة إعلانية':
                bot.sendMessage(chatId, "اختر المنتج الذي تود عمل حملة إعلانية له:");
                break;
            // زر تحديث حالة الطلب للمدير
            case '📦 عرض المخزون':
                bot.sendMessage(chatId, "إليك حالة الطلبات الحالية للتحديث:", {
                    reply_markup: {
                        inline_keyboard: [
                            [{ text: "تحديث حالة طلب #101", callback_data: 'update_101' }]
                        ]
                    }
                });
                break;
        }
    });

    // معالجة الأوامر التفاعلية
    bot.on('callback_query', (query) => {
        const chatId = query.message.chat.id;
        if (query.data === 'update_101') {
            bot.sendMessage(chatId, "اختر الحالة الجديدة:", {
                reply_markup: {
                    inline_keyboard: [
                        [{ text: "تم التجهيز ✅", callback_data: 'status_ready' }],
                        [{ text: "مع الطيار 🚚", callback_data: 'status_shipped' }],
                        [{ text: "تم الاستلام 🏁", callback_data: 'status_done' }]
                    ]
                }
            });
        }
    });
            }
