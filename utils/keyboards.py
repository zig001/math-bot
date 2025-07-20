from telebot import types
from config import bot_state, CHANNEL_ID

def admin_panel_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton("⏯️ Отключить бота", callback_data="toggle_bot"),
        types.InlineKeyboardButton("📨​ Рассылка всем", callback_data="send_to_all")
    ]
    if bot_state.current_collection['active']:
        buttons.append(types.InlineKeyboardButton("🔄 Добивка", callback_data="resend_collection"))
        buttons.append(types.InlineKeyboardButton("❌ Отключить сбор изображений", callback_data="undo_collection"))
    else:
        buttons.append(types.InlineKeyboardButton("🖼️ Начать сбор результатов", callback_data="collect_images"))

    markup.add(*buttons)
    return markup

def cancel_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('❌ Отменить', callback_data='cancel_action')
    ]
    markup.add(*buttons)
    return markup