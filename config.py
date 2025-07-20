import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMINS = [int(admin_id) for admin_id in os.getenv('ADMINS').split(',')]
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')

class BotState:
    def __init__(self):
        self.active = True
        self.current_collection = {
            'active': True,
            'send_to_id': 206681109,
            'start_time': None
        }

bot_state = BotState()
