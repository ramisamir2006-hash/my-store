import flask
from datetime import datetime
import requests
import time
import logging
from flask_session import Session
import telebot
from flask import Flask, request, jsonify
from telebot import types
import random
import os
import os.path
import re
from InDMDevDB import *
from purchase import *
from InDMCategories import *
from telebot.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment, ShippingOption
import json

# ====================================================
# --- بيانات الربط النهائية (RAMY SAMIR) ---
# ====================================================
TELEGRAM_BOT_TOKEN = '8395659007:AAHaIQBJD_dTd6Np46fNeNS-WHoAbLNK0rk'
ADMIN_ID = 7020070481              # رقم هويتك كمدير
ADMIN_USERNAME = "@RamiSamir2024"  # حسابك للتواصل
CHANNEL_ID = '@RamySamir2026Gold'  # القناة لعرض الموديلات
STORE_CURRENCY = 'EGP'             # العملة
# ====================================================

# إعداد البوت
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# إعداد Flask
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'Ramy_Secret_Key_2026'

# إعداد السجلات (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دالة إنشاء الكيبورد الرئيسي للعرب
def create_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    key1 = types.KeyboardButton(text="Shop Items 🛒")
    key2 = types.KeyboardButton(text="My Orders 🛍")
    key3 = types.KeyboardButton(text="Support 📞")
    keyboard.add(key1)
    keyboard.add(key2, key3)
    return keyboard

# معالج أمر البداية (Start) المطور لرامي سمير
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.chat.username
    
    # التحقق من صلاحيات الأدمن
    if user_id == ADMIN_ID:
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        
        # أزرار لوحة التحكم الكاملة
        key0 = types.KeyboardButton(text="Manage Products 💼")
        key1 = types.KeyboardButton(text="Manage Categories 💼")
        key2 = types.KeyboardButton(text="Manage Orders 🛍")
        key3 = types.KeyboardButton(text="Payment Methods 💳")
        key4 = types.KeyboardButton(text="News To Users 📣")
        key5 = types.KeyboardButton(text="Switch To User 🙍‍♂️")
        keyboardadmin.add(key0)
        keyboardadmin.add(key1, key2)
        keyboardadmin.add(key3, key4)
        keyboardadmin.add(key5)

        welcome_admin = f"أهلاً بك يا سيد رامي! 🤴\nأنت الآن المتحكم في متجر: {CHANNEL_ID}\n\nيمكنك إضافة منتجات جديدة أو متابعة الطلبات من الأزرار أدناه."
        bot.send_message(user_id, welcome_admin, reply_markup=keyboardadmin)
    else:
        # واجهة العملاء
        welcome_user = "مرحباً بك في متجرنا الإلكتروني! 🛍\nتصفح أرقى الموديلات والمنتجات الآن."
        bot.send_message(user_id, welcome_user, reply_markup=create_main_keyboard())

# استكمال باقي الدوال (Handlers) الخاصة بالمنتجات والأقسام...
