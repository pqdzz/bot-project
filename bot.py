import telebot
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time
from datetime import datetime, timedelta

# --- الإعدادات ---
API_TOKEN = '8260522692:AAFQjw5-3-Qo7Oie2vb_WsTdNIRgaoAFK_E'
ADMIN_ID = 96799666 
bot = telebot.TeleBot(API_TOKEN)

# قائمة الإيميلات (تأكد من صحتها هنا أيضاً)
EMAILS_DATA = [
    {"email": "your_email1@gmail.com", "password": "app_password_here"},
    {"email": "your_email2@gmail.com", "password": "app_password_here"}
]

TARGET_EMAIL = "support@telegram.org"
users_db = {} 
user_tasks = {}
stop_flags = {}

# --- دالة التحقق من صيغة الإيميل ---
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    return user_id in users_db and datetime.now() < users_db[user_id]

# --- الكيبوردات ---
def main_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🚀 بدء عملية الرفع', '📂 إدارة الإيميلات', '📊 الإحصائيات')
    return markup

def stop_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🛑 إيقاف العملية", callback_data="stop_process"))
    return markup

# --- البداية ونظام الاشتراك ---
@bot.message_handler(commands=['start'])
def start(message):
    if is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, "🚀 نظام الرفع V11 جاهز.\nالإيميلات المسجلة: " + str(len(EMAILS_DATA)), reply_markup=main_keyboard())
    else:
        bot.send_message(message.chat.id, "⚠️ طلبك قيد المراجعة لدى المسؤول...")
        admin_markup = telebot.types.InlineKeyboardMarkup()
        admin_markup.add(telebot.types.InlineKeyboardButton("✅ تفعيل (يوم)", callback_data=f"sub_{message.from_user.id}_1"),
                         telebot.types.InlineKeyboardButton("❌ رفض", callback_data=f"sub_{message.from_user.id}_0"))
        bot.send_message(ADMIN_ID, f"🔔 طلب دخول:\n👤 {message.from_user.first_name}\n🆔 `{message.from_user.id}`", reply_markup=admin_markup, parse_mode="Markdown")

# --- منطق الرفع والتحقق ---
@bot.message_handler(func=lambda message: message.text == '🚀 بدء عملية الرفع')
def init_process(message):
    if not is_subscribed(message.from_user.id): return
    # فحص أولي للإيميلات المضافة في الكود
    invalid_emails = [acc['email'] for acc in EMAILS_DATA if not is_valid_email(acc['email'])]
    if invalid_emails:
        bot.send_message(message.chat.id, f"❌ خطأ: هناك إيميلات تنسيقها خاطئ في السيرفر:\n{', '.join(invalid_emails)}")
        return
    
    user_tasks[message.chat.id] = {}
    stop_flags[message.chat.id] = False
    msg = bot.send_message(message.chat.id, "1️⃣ أرسل نص الرسالة (كود الرفع):")
    bot.register_next_step_handler(msg, get_text)

def get_text(message):
    user_tasks[message.chat.id]['text'] = message.text
    msg = bot.send_message(message.chat.id, "2️⃣ عدد الرسائل من كل إيميل؟")
    bot.register_next_step_handler(msg, get_count)

def get_count(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "⚠️ أرسل رقم فقط!"); bot.register_next_step_handler(message, get_count); return
    user_tasks[message.chat.id]['count'] = int(message.text)
    msg = bot.send_message(message.chat.id, "3️⃣ الفاصل الزمني (بالثواني)؟")
    bot.register_next_step_handler(msg, get_delay)

def get_delay(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "⚠️ أرسل رقم فقط!"); bot.register_next_step_handler(message, get_delay); return
    user_tasks[message.chat.id]['delay'] = int(message.text)
    
    data = user_tasks[message.chat.id]
    summary = f"📋 **مراجعة:**\n✉️ النص: `{data['text'][:20]}...`\n🔢 العدد: {data['count']}\n⏳ الفاصل: {data['delay']}ث"
    
    confirm_markup = telebot.types.InlineKeyboardMarkup()
    confirm_markup.add(telebot.types.InlineKeyboardButton("✅ ابدأ", callback_data="confirm_start"),
                       telebot.types.InlineKeyboardButton("❌ كنسل", callback_data="cancel_task"))
    bot.send_message(message.chat.id, summary, parse_mode="Markdown", reply_markup=confirm_markup)

# --- معالجة الكولباك ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    chat_id = call.message.chat.id
    if call.data == "confirm_start":
        bot.edit_message_text("🚀 انطلقنا...", chat_id, call.message.message_id)
        threading.Thread(target=run_spam, args=(call.message, user_tasks[chat_id])).start()
    elif call.data == "stop_process":
        stop_flags[chat_id] = True
    elif call.data.startswith('sub_'):
        # معالجة الاشتراك كما في النسخة السابقة
        pass

# --- محرك الإرسال مع كشف الباند ---
def run_spam(message, data):
    chat_id = message.chat.id
    sent = 0
    total = data['count'] * len(EMAILS_DATA)
    status_msg = bot.send_message(chat_id, "⏳ جاري العمل...", reply_markup=stop_keyboard())

    for i in range(data['count']):
        if stop_flags.get(chat_id): break
        
        for acc in EMAILS_DATA[:]: # نسخة من القائمة عشان نقدر نحذف منها
            if stop_flags.get(chat_id): break
            
            try:
                msg = MIMEMultipart()
                msg['From'] = acc['email']; msg['To'] = TARGET_EMAIL
                msg['Subject'] = f"Request {int(time.time())}"
                msg.attach(MIMEText(data['text'], 'plain'))
                
                with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as server:
                    server.starttls()
                    server.login(acc['email'], acc['password'])
                    server.send_message(msg)
                
                sent += 1
                bot.edit_message_text(f"🚀 **الحالة:**\n✅ تم الإرسال: {sent}\n📥 المتبقي: {total-sent}", chat_id, status_msg.message_id, reply_markup=stop_keyboard())
            
            except smtplib.SMTPAuthenticationError:
                bot.send_message(chat_id, f"🚨 **تنبيه باند!**\nالإيميل: {acc['email']}\nتم إيقافه وحذفه من الجلسة الحالية.")
                EMAILS_DATA.remove(acc) # حذفه عشان ما يكرر الخطأ
            except Exception as e:
                print(f"Error: {e}")
                
        time.sleep(data['delay'])
    
    bot.send_message(chat_id, f"🏁 انتهى. إجمالي الناجح: {sent}", reply_markup=main_keyboard())

bot.infinity_polling()
