import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=config.CHANNEL, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start(update: Update, context):
    user = update.effective_user
    
    if await check_subscription(user.id, context.bot):
        await update.message.reply_text("✅ Спасибо за подписку! Вот ваш файл:")
        
        with open(config.FILE_NAME, 'rb') as file:
            await update.message.reply_document(
                document=file,
                caption="Наслаждайтесь!"
            )
    else:
        keyboard = [
            [InlineKeyboardButton("📢 ПОДПИСАТЬСЯ НА КАНАЛ", url=f"https://t.me/{config.CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ Я ПОДПИСАЛСЯ", callback_data='check')]
        ]
        
        await update.message.reply_text(
            "📁 Чтобы получить файл, нужно подписаться на наш канал!\n\n"
            "1. Нажмите кнопку 'ПОДПИСАТЬСЯ НА КАНАЛ'\n"
            "2. Подпишитесь на канал\n"
            "3. Вернитесь сюда и нажмите 'Я ПОДПИСАЛСЯ'",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def button_click(update: Update, context):
    query = update.callback_query
    
    if query.data == 'check':
        user = query.from_user
        
        if await check_subscription(user.id, context.bot):
            await query.answer("✅ Отлично! Сейчас отправим файл...")
            
            with open(config.FILE_NAME, 'rb') as file:
                await context.bot.send_document(
                    chat_id=user.id,
                    document=file,
                    caption="Вот ваш файл! Спасибо за подписку!"
                )
        else:
            await query.answer("❌ Вы ещё не подписались на канал!", show_alert=True)

def main():
    app = Application.builder().token(config.TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("🤖 Бот запущен! Остановить: Ctrl+C")
    app.run_polling()

if __name__ == '__main__':
    main()
