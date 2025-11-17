import asyncio
import telebot
from utils.logger import logger
from core.summarize import summarize_chat_history
from tg_bot.models import ChatHistory
from tg_bot.constants import MAX_CHARS, HISTORY, BOT
from data_base.database import storage_manager
from core.chat import chat
from ml.llm_client import llm


from telebot.states.asyncio.middleware import StateMiddleware


@BOT.message_handler(commands=['start'])
async def start_message(message: telebot.types.Message):
    logger.info(f"start_message")

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_hello = telebot.types.KeyboardButton(text="Привет")
    button_summary = telebot.types.KeyboardButton(text="Пересказ истории чата")
    keyboard.add(button_hello)
    keyboard.add(button_summary)


    if message.chat.title is not None:
        storage_manager.add_chat(message.chat.title)

    await BOT.reply_to(message, "Привет!", reply_markup=keyboard)


@BOT.message_handler(func=lambda message: message.text == 'Привет')
async def say_hello(message: telebot.types.Message):
    logger.info(f"say_hello")
    user_id = storage_manager.get_user_id(message.from_user.username)
    if message.chat.title is not None:
        chat_id = storage_manager.get_chat_id(message.chat.title)
        storage_manager.add_user_to_chat(user_id, chat_id)

    await BOT.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {message.from_user.last_name}!")






