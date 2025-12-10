import os
import telebot
from telebot import types
import time

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

CHANNEL = "@cultural_wave"
FILE = "gift.pdf"

print(f"🤖 Бот запущен. Проверяет канал: {CHANNEL}")

def is_subscribed(user_id):
    """Проверяет подписку на канал"""
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    print(f"👤 Пользователь {user_id} нажал /start")
    
    # Всегда отправляем сообщение ДО проверки
    if is_subscribed(user_id):
        # Подписан
        try:
            bot.send_message(user_id, "✅ Спасибо за подписку! Вот ваш файл:")
            with open(FILE, 'rb') as f:
                bot.send_document(user_id, f, caption="🎁 Наслаждайтесь!")
            print(f"📤 Файл отправлен пользователю {user_id}")
        except:
            bot.send_message(user_id, "❌ Файл временно недоступен")
    else:
        # НЕ подписан — ГАРАНТИРОВАННО отправляем сообщение
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("📢 ПОДПИСАТЬСЯ", url=f"https://t.me/{CHANNEL[1:]}")
        btn2 = types.InlineKeyboardButton("✅ Я ПОДПИСАЛСЯ", callback_data="check")
        markup.add(btn1, btn2)
        
        # ЭТО СООБЩЕНИЕ ОТПРАВИТСЯ ВСЕГДА для неподписанных
        msg = bot.send_message(
            user_id,
            f"⚠️ *ВНИМАНИЕ!*\n\n"
            f"Для получения файла нужно подписаться на канал:\n"
            f"🔗 {CHANNEL}\n\n"
            f"*Инструкция:*\n"
            f"1. Нажмите 'ПОДПИСАТЬСЯ'\n"
            f"2. Подпишитесь на канал\n"
            f"3. Вернитесь сюда и нажмите 'Я ПОДПИСАЛСЯ'",
            parse_mode='Markdown',
            reply_markup=markup
        )
        print(f"📝 Сообщение о подписке отправлено пользователю {user_id} (ID сообщения: {msg.message_id})")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "check":
        user_id = call.from_user.id
        
        if is_subscribed(user_id):
            bot.answer_callback_query(call.id, "✅ Вы подписаны! Отправляем файл...")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(user_id, "✅ Отлично! Вот ваш файл:")
            with open(FILE, 'rb') as f:
                bot.send_document(user_id, f, caption="🎁 Наслаждайтесь!")
        else:
            bot.answer_callback_query(
                call.id,
                f"❌ Вы всё ещё не подписаны на {CHANNEL}. Подпишитесь и попробуйте снова.",
                show_alert=True
            )

# Команда для тестирования
@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, f"Бот работает! Канал: {CHANNEL}")

print("=" * 50)
print("✅ БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ")
print("=" * 50)

while True:
    try:
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
