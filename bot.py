import os
import telebot

# Получаем токен из переменных Railway
TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Если токена нет - бот не запустится
if not TOKEN:
    print("❌ ОШИБКА: TELEGRAM_TOKEN не найден!")
    print("Добавьте переменную TELEGRAM_TOKEN в Railway Variables")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        # Отправляем сообщение
        bot.send_message(message.chat.id, "Спасибо за подписку! Вот ваш файл:")
        
        # Отправляем файл
        with open('gift.pdf', 'rb') as file:
            bot.send_document(message.chat.id, file, caption="Наслаждайтесь!")
        
        print(f"✅ Файл отправлен пользователю {message.from_user.id}")
        
    except FileNotFoundError:
        bot.send_message(message.chat.id, "❌ Файл временно недоступен")
        print("❌ Файл gift.pdf не найден!")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Ошибка отправки файла")
        print(f"❌ Ошибка: {e}")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "📋 Команды:\n/start - получить файл\n/help - справка")

print("=" * 50)
print("🤖 Бот запускается...")
print(f"🔑 Токен: {'установлен' if TOKEN else 'НЕТ!'}")
print("=" * 50)

# Запускаем бота
bot.polling(none_stop=True)
