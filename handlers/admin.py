from telebot import types
from telebot.types import Message, CallbackQuery
from datetime import datetime
from config import bot_state, ADMINS, DEBUG
from database.crud import get_all_users, get_users_without_images, get_user_count
from utils.keyboards import (
    admin_panel_markup,
    cancel_markup
)

def setup_admin_handlers(bot):
    # Вспомогательные функции
    def is_admin(user_id: int) -> bool:
        return user_id in ADMINS

    def send_not_admin_message(chat_id: int):
        bot.send_message(chat_id, "⛔ У вас нет прав администратора")

    # Обработчики команд
    def show_admin_panel(chat_id, message_id=None):
        """Универсальная функция отображения/обновления админ-панели"""
        
        users_count = get_user_count()
        users_without_images = get_users_without_images()
        users_with_images = users_count - len(users_without_images)
        
        status = "🟢 Активен" if bot_state.active else "🔴 Отключен"
        collection_status = f"🟢 В процессе, отправили: {users_with_images}/{users_count}" if bot_state.current_collection['active'] else "🔴 Не активно"
        
        text = (
            f"⚙️ Панель администратора\n"
            f"Статус бота: {status}\n"
            f"Сбор результатов: {collection_status}"
        )
        
        if message_id:
            # Редактируем существующее сообщение
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=admin_panel_markup()
            )
        else:
            # Отправляем новое сообщение
            bot.send_message(
                chat_id,
                text,
                reply_markup=admin_panel_markup()
            )

    @bot.message_handler(commands=['admin'])
    def handle_admin_command(message: Message):
        """Обработчик команды /admin"""
        if message.from_user.id not in ADMINS:
            return bot.send_message(message.chat.id, "⛔ У вас нет прав администратора")
        
        show_admin_panel(message.chat.id)

    # Обработчики callback-запросов
    @bot.callback_query_handler(func=lambda call: call.data == 'undo_collection')
    def handle_toggle_bot(call: CallbackQuery):
        if not is_admin(call.from_user.id):
            return bot.answer_callback_query(call.id, "⛔ Нет прав администратора", show_alert=True)
        
        bot_state.current_collection['active'] = False
        bot.answer_callback_query(call.id, "Сбор остановлен")
        show_admin_panel(call.message.chat.id, call.message.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'toggle_bot')
    def handle_toggle_bot(call: CallbackQuery):
        if not is_admin(call.from_user.id):
            return bot.answer_callback_query(call.id, "⛔ Нет прав администратора", show_alert=True)
        
        bot_state.active = not bot_state.active
        status = "включен" if bot_state.active else "выключен"
        
        bot.answer_callback_query(call.id, f"Бот {status}")
        show_admin_panel(call.message.chat.id, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'collect_images')
    def handle_collect_images(call: CallbackQuery):
        if not is_admin(call.from_user.id):
            return bot.answer_callback_query(call.id, "⛔ Нет прав администратора", show_alert=True)
        
        bot_state.current_collection['active'] = True
        bot_state.current_collection['send_to_id'] = call.message.chat.id
        bot_state.current_collection['start_time'] = datetime.now().timestamp()
        print("началось")
        
        msg = bot.send_message(
            call.message.chat.id,
            "📢 Введите сообщение для сбора изображений:",
            reply_markup=cancel_markup()
        )
        bot.register_next_step_handler(msg, send_message_to_users)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == 'resend_collection')
    def handle_resend_collection(call: CallbackQuery):
        if not is_admin(call.from_user.id):
            return bot.answer_callback_query(call.id, "⛔ Нет прав администратора", show_alert=True)
        
        users = get_users_without_images()
        if not users:
            return bot.answer_callback_query(call.id, "✅ Все уже отправили результаты", show_alert=True)
            
        msg = bot.send_message(
            call.message.chat.id,
            "✏️ Введите новое сообщение для добивки:",
            reply_markup=cancel_markup()
        )
        bot.register_next_step_handler(msg, lambda m: send_message_to_users(m, users))
        bot.answer_callback_query(call.id)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'send_to_all')
    def handle_resend_collection(call: CallbackQuery):
        if not is_admin(call.from_user.id):
            return bot.answer_callback_query(call.id, "⛔ Нет прав администратора", show_alert=True)
        
        msg = bot.send_message(
            call.message.chat.id,
            "✏️ Введите сообщение которое нужно отправить:",
            reply_markup=cancel_markup()
        )
        bot.register_next_step_handler(msg, send_message_to_users)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_action')
    def handle_cancel_action(call: CallbackQuery):
        bot.answer_callback_query(call.id)
        show_admin_panel(call.message.chat.id, call.message.message_id)

    def send_message_to_users(message: Message, users = None):
        if not users:
            users = get_all_users()
        
        if message.content_type == 'text':
            collection_text = message.text
        elif message.content_type == 'photo':
            collection_text = message.caption or ""
        else:
            bot.reply_to(message, "❌ Поддерживаются только текст или фото с подписью")
            return
        success = 0

        for user in users:
            try:
                if message.content_type == 'text':
                    bot.send_message(user.user_id, collection_text)
                elif message.content_type == 'photo':
                    bot.send_photo(user.user_id, message.photo[-1].file_id, caption=collection_text)
                success += 1
            except Exception as e:
                print(f"Ошибка отправки пользователю {user.user_id}: {e}")
        
        bot.send_message(
            bot_state.current_collection['send_to_id'],
            f"📢 Сообщение отправлено {success} из {len(users)} пользователей\n"
        )
        show_admin_panel(message.chat.id)