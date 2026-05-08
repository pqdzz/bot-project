import telebot
import time
from datetime import datetime, timedelta

# --- الإعدادات الأساسية ---
# التوكن الصحيح والجاهز
API_TOKEN = '8260522692:AAFQjw5-3-Qo7Oie2vb_WsTdNIRgaoAFK_E'
ADMIN_ID = 96799666  # ايديك الخاص

bot = telebot.TeleBot(API_TOKEN)

# --- اسم ملف البيانات (إذا كنت تستخدمه) ---
DB_FILE = "global_subs.json"

# --- الأوامر ---

# أمر البداية /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.reply_to(message, f"هلا بك يا {user_name} في بوت رفيق المعرفة 🤖\nالبوت شغال الحين وجاهز لخدمتك!")

# أمر المساعدة /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "قائمة الأوامر المتوفرة:\n"
        "/start - تشغيل البوت\n"
        "/help - عرض هذه القائمة"
    )
    bot.reply_to(message, help_text)

# الرد على أي رسالة نصية أخرى
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "وصلت رسالتك! جاري تطوير باقي الخدمات..")

# --- تشغيل البوت ---
print("البوت بدأ العمل الآن بدون أخطاء...")
bot.infinity_polling()
