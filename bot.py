import os
import telebot
from telebot import types
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    logger.error("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
logger.info("✅ Бот инициализирован")

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
            logger.info(f"❌ Пользователь {user_id} НЕ подписан на канал")
            return False
        logger.info(f"✅ Пользователь {user_id} подписан на канал")
        return True
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    
    logger.info(f"👤 Пользователь @{username} ({user_id}) нажал /start")
    
    # Проверяем подписку
    if check_subscription(user_id):
        # Пользователь подписан - отправляем файл
        try:
            bot.send_message(message.chat.id, "✅ Спасибо за подписку! Вот ваш файл:")
            with open(FILE_NAME, 'rb') as file:
                bot.send_document(message.chat.id, file, caption="🎁 Наслаждайтесь!")
            logger.info(f"📤 Файл отправлен пользователю {user_id}")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "❌ Файл временно недоступен. Попробуйте позже.")
            logger.error("Файл не найден!")
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Ошибка отправки файла.")
            logger.error(f"Ошибка: {e}")
    
    else:
        # НЕ подписан - показываем сообщение и кнопки
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(
                "📢 ПОДПИСАТЬСЯ НА КАНАЛ",
                url=CHANNEL_LINK
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "✅ Я ПОДПИСАЛСЯ / ПРОВЕРИТЬ",
                callback_data="check_sub"
            )
        )
        
        # ОТПРАВЛЯЕМ СООБЩЕНИЕ для НЕподписанных
        bot.send_message(
            message.chat.id,
            f"🚫 *ДОСТУП ЗАКРЫТ*\n\n"
            f"Для получения файла *{FILE_NAME}* необходимо подписаться на наш канал:\n"
            f"👉 {CHANNEL}\n\n"
            f"📌 *Инструкция:*\n"
            f"1. Нажмите кнопку 'ПОДПИСАТЬСЯ НА КАНАЛ'\n"
            f"2. Подпишитесь на канал\n"
            f"3. Вернитесь в этот чат\n"
            f"4. Нажмите 'Я ПОДПИСАЛСЯ'\n\n"
            f"После этого я сразу отправлю вам файл!",
            parse_mode='Markdown',
            reply_markup=markup,
            disable_web_page_preview=True
        )
        
        logger.info(f"📝 Отправлено сообщение о подписке пользователю {user_id}")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription_callback(call):
    """Обработка нажатия кнопки 'Я подписался'"""
    user_id = call.from_user.id
    username = call.from_user.username or "без username"
    
    logger.info(f"🔍 Пользователь @{username} нажал 'Я подписался'")
    
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
            bot.send_message(call.message.chat.id, "✅ Отлично! Вы подписаны. Вот ваш файл:")
            with open(FILE_NAME, 'rb') as file:
                bot.send_document(call.message.chat.id, file, caption="🎁 Наслаждайтесь!")
            logger.info(f"📤 Файл отправлен через callback пользователю {user_id}")
        except Exception as e:
            bot.send_message(call.message.chat.id, "✅ Вы подписаны! Но файл временно недоступен.")
            logger.error(f"Ошибка отправки файла: {e}")
    
    else:
        # Всё равно не подписан
        bot.answer_callback_query(
            call.id,
            f"❌ Вы всё ещё не подписаны на {CHANNEL}\n\n"
            f"Нажмите кнопку 'ПОДПИСАТЬСЯ НА КАНАЛ', подпишитесь и попробуйте снова.",
            show_alert=True
        )
        logger.info(f"⚠️ Пользователь {user_id} всё ещё не подписан")

@bot.message_handler(commands=['help'])
def help_command(message):
    """Команда /help"""
    help_text = (
        "🤖 *Помощь по боту*\n\n"
        "📌 *Как получить файл:*\n"
        "1. Подпишитесь на канал @cultural_wave\n"
        "2. Нажмите /start\n"
        "3. Или нажмите кнопку 'Я ПОДПИСАЛСЯ'\n\n"
        "❓ *Проблемы?*\n"
        "• Убедитесь, что подписались на канал\n"
        "• После подписки нажмите 'Я ПОДПИСАЛСЯ'\n"
        "• Если не помогает, напишите администратору"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

print("=" * 50)
print("🤖 БОТ ЗАПУЩЕН С ПРОВЕРКОЙ ПОДПИСКИ")
print(f"📢 Канал: {CHANNEL}")
print(f"📁 Файл: {FILE_NAME}")
print("=" * 50)
logger.info("🟢 Бот готов к работе!")

# Запускаем бота
bot.polling(none_stop=True, interval=1, timeout=30)
