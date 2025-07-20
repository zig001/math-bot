from telebot import types
from datetime import datetime
from config import bot_state, ADMINS, CHANNEL_ID, DEBUG
from database.crud import add_sent_image, add_user
from database.models import User


def setup_user_handlers(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        if DEBUG:
            bot.send_message(message.chat.id, "🔧 Debug enviroment")
        if not bot_state.active:
            bot.send_message(message.chat.id, "⛔ Работа бота временно приостановлена")
            return
        username = message.from_user.username if message.from_user.username else None
        add_user(User(message.chat.id, username))

        # invite_link = bot.export_chat_invite_link(CHANNEL_ID)
        invite_link = "https://t.me/+0fqNDpG-Nf0yMDJi"
        markup = types.InlineKeyboardMarkup()
        buttons = [
            types.InlineKeyboardButton("🔗 Перейти в канал", url=invite_link),
        ]
        markup.add(*buttons)

        bot.send_message(
            message.chat.id,
            "Привет, привет 🩷\n"
            "На связи Маша Математичка! \n\n"
            "Присоединиться к каналу, где мы целый месяц будем активно ботать профмат можно ниже 👇🏼\n\n"
            "_Не забывай, у нас токсик фри зона. мы чисто тут, чтобы профмат на сотку сдать_ 💪🏼\n",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        

        markup = types.InlineKeyboardMarkup()
        link_button = types.InlineKeyboardButton(text="YouTube ▶️", url="https://youtube.com/@matematika_el")
        markup.add(link_button)

        bot.send_message(
            message.chat.id,
            "В рамках закрытого канала, многие видео будут находиться на ютубе, так что сразу подпишитесь на мой ютуб-канал, чтобы ничего не пропустить!!!\n\n"
            "_ссылочку на канал найдёте по кнопочке_ 👇\n",
            reply_markup=markup,
            parse_mode='Markdown'
        )