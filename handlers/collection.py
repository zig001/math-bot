from telebot import types
from telebot.types import Message, CallbackQuery
from datetime import datetime
from config import bot_state, ADMINS, DEBUG
from database.crud import (
    add_sent_image,
    get_users_with_images,
    get_users_without_images
)

def setup_collection_handlers(bot):
    @bot.message_handler(content_types=['photo'], 
                        func=lambda m: bot_state.current_collection['active'])
    def handle_user_images(message: Message):
        if message.from_user.id is bot_state.current_collection['send_to_id'] and not DEBUG:
            return
        if not bot_state.active:
            bot.send_message(message.chat.id, "⛔ Работа бота временно приостановлена")

        user_id = message.from_user.id
        username = message.from_user.username or f"ID:{user_id}"

        processed_count = 0
        file_id = message.photo[-1].file_id

        if add_sent_image(user_id, file_id):
            caption_text = f"Дата: {datetime.now():%Y-%m-%d %H:%M}, от @{username}"

            if message.caption:
                caption_text += f"\nПодпись: {message.caption}"

            bot.send_photo(
                bot_state.current_collection['send_to_id'],
                file_id,
                caption=caption_text
            )

    @bot.message_handler(content_types=['text'], 
                     func=lambda m: bot_state.current_collection['active'])
    def handle_user_text(message: Message):
        bot.send_message(
            bot_state.current_collection['send_to_id'],
            f"Получен текст от @{message.from_user.username or f'ID:{message.from_user.id}'}: \n{message.text}"
        )
    
    @bot.message_handler(commands=['collection_stats'], 
                        func=lambda m: m.from_user.id in ADMINS)
    def handle_collection_stats(message: Message):
        users_with_images = get_users_with_images()
        users_without_images = get_users_without_images()
        bot.send_message(
            message.chat.id,
            f"📊 Статистика сбора:\n"
            f"Отправили результаты: {users_with_images}/{users_without_images}.\n"
        )
