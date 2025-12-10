#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================== ИМПОРТЫ ====================
import config              # твой файл с настройками
import telebot
import logging
import time
from datetime import datetime

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== ИНИЦИАЛИЗАЦИЯ БОТА ====================
try:
    bot = telebot.TeleBot(config.TOKEN)
    logger.info(f"✅ Бот инициализирован с токеном: {config.TOKEN[:15]}...")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации бота: {e}")
    exit(1)

# ==================== ПЕРЕМЕННЫЕ ====================
CHANNEL = config.CHANNEL
FILE_NAME = config.FILE_NAME
ADMIN_ID = None  # можно добавить свой ID для уведомлений

# ==================== ФУНКЦИИ ====================
def check_subscription(user_id):
    """Проверяет подписку на канал"""
    try:
        chat_member = bot.get_chat_member(CHANNEL, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False

def send_file(chat_id):
    """Отправляет файл пользователю"""
    try:
        with open(FILE_NAME, 'rb') as file:
            bot.send_document(chat_id, file, caption="Наслаждайтесь!")
        logger.info(f"📤 Файл отправлен пользователю {chat_id}")
        return True
    except FileNotFoundError:
        logger.error(f"Файл {FILE_NAME} не найден!")
        bot.send_message(chat_id, "❌ Файл временно недоступен. Администратор уведомлен.")
        return False
    except Exception as e:
        logger.error(f"Ошибка отправки файла: {e}")
        return False

# ==================== КОМАНДЫ БОТА ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработка команды /start"""
    user = message.from_user
    user_id = user.id
    username = user.username or "без username"
    
    logger.info(f"👤 Пользователь @{username} ({user_id}) нажал /start")
    
    # Проверяем подписку
    if check_subscription(user_id):
        # Пользователь подписан
        bot.send_message(user_id, "Спасибо за подписку! Вот ваш файл:")
        send_file(user_id)
    else:
        # Не подписан - показываем кнопки
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            telebot.types.InlineKeyboardButton(
                f"📢 Подписаться на {CHANNEL}",
                url=f"https://t.me/{CHANNEL[1:]}"
            ),
            telebot.types.InlineKeyboardButton(
                "✅ Я подписался",
                callback_data="check_sub"
            )
        )
        
        bot.send_message(
            user_id,
            f"👋 Привет, {user.first_name}!\n\n"
            f"📋 Для получения файла *gift.pdf* подпишитесь на канал:\n"
            f"👉 {CHANNEL}\n\n"
            "После подписки нажмите кнопку ниже ⬇️",
            parse_mode='Markdown',
            reply_markup=markup
        )

@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработка команды /help"""
    help_text = """
🤖 *Доступные команды:*
/start - Получить файл
/help - Эта справка
/status - Статус бота

📢 *Канал для подписки:*
{c}

❓ *Проблемы?*
1. Подпишитесь на канал
2. Нажмите /start
3. Или кнопку "Я подписался"
    """.format(c=CHANNEL)
    
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_command(message):
    """Обработка команды /status"""
    status_text = f"""
✅ *Статус бота:*
• Работает: Да
• Время: {datetime.now().strftime('%H:%M:%S')}
• Файл: {FILE_NAME}
• Канал: {CHANNEL}

👤 *Ваши данные:*
• ID: {message.from_user.id}
• Username: @{message.from_user.username or 'не указан'}
    """
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')# ==================== CALLBACK КНОПКИ ====================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_subscription_callback(call):
    """Обработка нажатия кнопки 'Я подписался'"""
    user = call.from_user
    user_id = user.id
    
    # Показываем "проверяем"
    bot.answer_callback_query(call.id, "🔍 Проверяем подписку...")
    
    if check_subscription(user_id):
        # Удаляем старое сообщение с кнопками
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        
        # Отправляем файл
        bot.send_message(user_id, "Спасибо за подписку! Вот ваш файл:")
        send_file(user_id)
    else:
        # Не подписан
        bot.answer_callback_query(
            call.id,
            f"❌ Вы не подписаны на {CHANNEL}. Подпишитесь и попробуйте снова.",
            show_alert=True
        )

# ==================== ЗАПУСК БОТА ====================
if __name__ == '__main__':
    print("=" * 50)
    print(f"🤖 Запуск бота для канала: {CHANNEL}")
    print(f"📁 Файл для отправки: {FILE_NAME}")
    print(f"🕒 Время запуска: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    logger.info("🟢 Бот запущен и готов к работе!")
    
    # Бесконечный цикл с перезапуском при ошибках
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            logger.error(f"❌ Ошибка polling: {e}")
            logger.info("🔄 Перезапуск через 10 секунд...")
            time.sleep(10)
            continue
