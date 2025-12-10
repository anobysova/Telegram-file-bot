import os
import telebot
from telebot import types

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ТВОИ ДАННЫЕ
CHANNEL = "@cultural_wave"  # канал для подписки
CHANNEL_LINK = "https://t.me/cultural_wave"  # ссылка на канал
FILE_NAME = "gift.pdf"  # твой файл

def check_subscription(user_id):
    """Проверяет, подписан ли пользователь на канал"""
    try:
        chat_member = bot.get_chat_member(CHANNEL, user_id)
        # Если статус 'left' или 'kicked' - не подписан
        if chat_member.status in ['left', 'kicked']:
            return False
        return True
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    
    # Проверяем подписку
    if check_subscription(user_id):
        # Пользователь подписан - отправляем файл
        try:
            bot.send_message(message.chat.id, "Спасибо за подписку! Вот ваш файл:")
            with open(FILE_NAME, 'rb') as file:
                bot.send_document(message.chat.id, file, caption="Наслаждайтесь!")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "❌ Файл временно недоступен")
    else:
        # Не подписан - показываем кнопки
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "📢 Подписаться на канал",
                url=CHANNEL_LINK
            ),
            types.InlineKeyboardButton(
                "✅ Я подписался",
                callback_data="check_subscription"
            )
        )
        
        bot.send_message(
            message.chat.id,
            f"👋 Для получения файла *{FILE_NAME}* подпишитесь на наш канал:\n"
            f"📢 {CHANNEL}\n\n"
            "После подписки нажмите кнопку ниже:",
            parse_mode='Markdown',
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription_callback(call):
    """Обработка нажатия кнопки 'Я подписался'"""
    user_id = call.from_user.id
    
    # Показываем "проверяем"
    bot.answer_callback_query(call.id, "🔍 Проверяем подписку...")
    
    if check_subscription(user_id):
        # Удаляем старое сообщение с кнопками
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        # Отправляем файл
        try:
            bot.send_message(call.message.chat.id, "Спасибо за подписку! Вот ваш файл:")
            with open(FILE_NAME, 'rb') as file:
                bot.send_document(call.message.chat.id, file, caption="Наслаждайтесь!")
        except:
            bot.send_message(call.message.chat.id, "✅ Вы подписаны! Но файл временно недоступен.")
    else:
        bot.answer_callback_query(
            call.id,
            f"❌ Вы не подписаны на {CHANNEL}. Подпишитесь и попробуйте снова.",
            show_alert=True
        )

print("=" * 50)
print("🤖 Бот запущен с проверкой подписки!")
print(f"📢 Канал: {CHANNEL}")
print(f"📁 Файл: {FILE_NAME}")
print("=" * 50)

bot.polling(none_stop=True)
