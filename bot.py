import telebot
import time
from datetime import datetime, timedelta

# ضع التوكن الخاص بك هنا مباشرة بين علامتي التنصيص
API_TOKEN = '8260522692:AAFQjw5-3-Qo7Oie2vb_WsTdNIRgaoAFK_E'

bot = telebot.TeleBot(API_TOKEN)

# كمل باقي كودك هنا...


# اسم ملف البيانات
DB_FILE = "global_subs.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    subs = load_data()
    
    # رسالة ترحيبية بسيطة للتأكد من العمل
    bot.reply_to(message, "أهلاً بك في بوت رفع الشدات! 🚀\nالبوت شغال الآن على السيرفر الجديد.")

# سطر التأكد من التشغيل في السيرفر
print("✅ Bot is running successfully...")

# تشغيل البوت
if __name__ == "__main__":
    bot.infinity_polling()
