const TelegramBot = require('node-telegram-bot-api');
const Airtable = require('airtable');
const express = require('express');

const app = express();
app.listen(process.env.PORT || 8000); // المنفذ الذي اخترته في Koyeb

const base = new Airtable({apiKey: process.env.AIRTABLE_API_KEY}).base(process.env.BASE_ID);
const bot = new TelegramBot(process.env.BOT_TOKEN, {polling: true});

bot.onText(/\/start/, (msg) => {
    const opts = {
        reply_markup: {
            inline_keyboard: [
                [{ text: '🛒 إضافة للسلة', callback_data: 'add' }],
                [{ text: '🏪 فتح المتجر', url: 'https://t.me/maria_jewelry' }]
            ]
        }
    };
    bot.sendMessage(msg.chat.id, "مرحباً بك في متجر ماريا للذهب الصيني ✨", opts);
});
