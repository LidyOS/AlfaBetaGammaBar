import telebot
from tg_bot.utils import wait_wessage
from utils.logger import logger
from tg_bot.constants import BOT

from core.chat import chat
from telebot.states.asyncio.context import StateContext
from telebot.states.asyncio.middleware import StateMiddleware


@BOT.message_handler(commands=['chat'])
async def chat_message(message: telebot.types.Message, state: StateContext):
    logger.info(f"chat_message")

    # BOT.register_next_step_handler(message, receive_and_save_message)
    await state.set('waiting_question') 
    await BOT.reply_to(message, "Какой вопрос тебя интересует?")


@BOT.message_handler(state='waiting_question', content_types=['text'])
async def receive_and_save_message(message: telebot.types.Message, state: StateContext):
    logger.info(f"receive_and_save_message")
    # Разрешаем только текст
    if message.content_type != 'text' or not message.text:
        await BOT.reply_to(message, "Пожалуйста, отправьте текстовое сообщение.")
        # BOT.register_next_step_handler(message, receive_and_save_message)
        return

    await wait_wessage(message, chat, message.text.strip(), state=state)


@BOT.message_handler(state='waiting_question', content_types=[ 'photo', 'audio', 'video', 'document', 'sticker', 'voice', 'video_note', 'location', 'contact', 'animation', 'poll' ]) 
async def reject_non_text(message: telebot.types.Message): 
    logger.info(f"reject_non_text")
    await BOT.reply_to(message, "Пожалуйста, отправьте текстовое сообщение.")

BOT.add_custom_filter(telebot.asyncio_filters.StateFilter(BOT))
BOT.setup_middleware(StateMiddleware(BOT))