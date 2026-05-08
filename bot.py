import telebot
from telebot import types
import json
import os
import time
from datetime import datetime

# --- الإعدادات الأساسية ---
# التوكن الصحيح والوحيد
API_TOKEN = '8260522692:AAFQjw5-3-Qo7Oie2vb_WsTdNIRgaoAFK_E'
ADMIN_ID = 96799666 

bot = telebot.TeleBot(API_TOKEN)

# ملف تخزين البيانات لضمان استقرار النظام
DB_FILE = "global_subs.json"

# --- نظام إدارة البيانات (لضمان الاستقرار) ---
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    try:
        with open(DB_FILE, "r", encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving: {e}")

# --- لوحة الأزرار الرئيسية ---
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('🚀 بدء شد جديد'),
        types.KeyboardButton('📂 إدارة بياناتي'),
        types.KeyboardButton('📊 عدد المشتركين')
    )
    return markup

# --- الأوامر ومعالجة الرسائل ---

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    data = load_data()
    
    # تسجيل المستخدم إذا كان جديداً
    if user_id not in data:
        data[user_id] = {
            "name": message.from_user.first_name,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_data(data)
    
    bot.send_message(
        message.chat.id, 
        "تم الدخول بنجاح. اختر من القائمة:", 
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    user_id = str(message.from_user.id)
    text = message.text

    if text == '🚀 بدء شد جديد':
        bot.send_message(message.chat.id, "تم الدخول بنجاح. اختر من القائمة:", reply_markup=main_keyboard())
        
    elif text == '📂 إدارة بياناتي':
        bot.send_message(message.chat.id, "تم الدخول بنجاح. اختر من القائمة:", reply_markup=main_keyboard())

    elif text == '📊 عدد المشتركين':
        data = load_data()
        bot.send_message(message.chat.id, f"تم الدخول بنجاح. اختر من القائمة:\n\nعدد المشتركين: {len(data)}", reply_markup=main_keyboard())

    else:
        bot.send_message(message.chat.id, "اختر من القائمة المتاحة أدناه 👇", reply_markup=main_keyboard())

# --- تشغيل البوت بنظام حماية من التوقف ---
def run_bot():
    print("Bot is Live now...")
    while True:
        try:
            bot.infinity_polling(timeout=15, long_polling_timeout=10)
        except Exception as e:
            print(f"Error: {e}. Restarting in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
