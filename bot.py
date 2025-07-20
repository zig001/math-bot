from telebot import TeleBot
from config import BOT_TOKEN, bot_state
from database.crud import init_db
from handlers import admin, collection, user

def main():
    bot = TeleBot(BOT_TOKEN)
    init_db()
    
    admin.setup_admin_handlers(bot)
    collection.setup_collection_handlers(bot)
    user.setup_user_handlers(bot)
    
    print("Бот запущен...")
    bot.infinity_polling()

if __name__ == '__main__':
    main()
