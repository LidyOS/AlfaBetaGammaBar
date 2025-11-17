import os
from dotenv import load_dotenv
import telebot
from tg_bot.models import ChatHistory
from telebot.async_telebot import AsyncTeleBot


HISTORY : dict[str, ChatHistory] = {}
MAX_CHARS = 1000

load_dotenv() 
API_KEY = os.getenv('TG_BOT_ID')
BOT = AsyncTeleBot(API_KEY)