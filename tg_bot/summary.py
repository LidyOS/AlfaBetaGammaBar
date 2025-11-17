import datetime
import telebot
from tg_bot.utils import flush_history, format_rows
from utils.logger import logger
from core.summarize import summarize_chat_history
from tg_bot.models import ChatHistory
from tg_bot.constants import MAX_CHARS, HISTORY, BOT
from data_base.database import storage_manager
from telebot.states.asyncio.context import StateContext
from ml.llm_client import llm


@BOT.message_handler(func=lambda message: message.text == 'Пересказ истории чата')
async def get_summary(message: telebot.types.Message):
    logger.info(f"get_summary")
    sender = message.from_user.username
    user_id = storage_manager.get_user_id(sender)
    all_chats = storage_manager.get_user_chats(user_id)
    keyboard = telebot.types.InlineKeyboardMarkup(
        keyboard=[
            [
                telebot.types.InlineKeyboardButton(
                    text=chat_name['name'],
                    callback_data=f'select_chat={chat_name['name']}'
                )
            ]
            for chat_name in all_chats
        ]
    )

    logger.info(f"Найденые чаты {all_chats}")
    # logger.info(f"Найденые чаты {[(chat_name['name'], type(chat_name['name'])) for chat_name in storage_manager.get_user_chats(user_id)]}")
    # logger.info(f"Найденые чаты {[key[0].to_dict() for key in keyboard.keyboard]}")


    if not all_chats:
        await BOT.send_message(message.chat.id, "У вас нет зарегистрированных чатов. Добавь бота в группу и поприветсвуй его")
        return 
    logger.info(f"GG")

    await BOT.send_message(message.chat.id, "Выбери чат, в котором хочешь увидеть пересказ  истории сообщений", reply_markup=keyboard)
    logger.info(f"WP")


@BOT.callback_query_handler(func=lambda call: call.data.startswith('select_chat'))
async def select_chat(call: telebot.types.CallbackQuery): 
    logger.info("select_chat") 
    # await BOT.answer_callback_query(call.id)
    # selected_chat = call.data[len('select_chat='):]

    kb = telebot.types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        telebot.types.InlineKeyboardButton("1 час", callback_data=f"period=1h&{call.data}"),
        telebot.types.InlineKeyboardButton("24 часа", callback_data=f"period=24h&{call.data}"),
        telebot.types.InlineKeyboardButton("7 дней", callback_data=f"period=7d&{call.data}"),
        telebot.types.InlineKeyboardButton("30 дней", callback_data=f"period=30d&{call.data}"),
        telebot.types.InlineKeyboardButton("Все время", callback_data=f"period=all&{call.data}"),
        telebot.types.InlineKeyboardButton("Своя дата…", callback_data=f"period=custom&{call.data}"),
    )

    await BOT.edit_message_text(
        "За какой период показать записи?",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=kb
    )


@BOT.callback_query_handler(func=lambda call: call.data.startswith('period=')) 
async def handle_period(call: telebot.types.CallbackQuery, state): 
    # await BOT.answer_callback_query(call.id) 
    time_value = call.data[len("period="):call.data.find('&')]
    chat_value = call.data[call.data.find('&') + 1:][len('select_chat='):]
    # Если пользователь выбрал ручной ввод даты
    if time_value == 'custom':
        await state.set('waiting_summary_since_input')
        await BOT.edit_message_text(
            "Введите дату/время в формате YYYY-MM-DD HH:MM:SS\n"
            "Например: 2025-11-01 00:00:00",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        return

    # Пресеты
    now = datetime.datetime.now()
    if time_value == 'all':
        created_after = '1970-01-01 00:00:00'
    elif time_value.endswith('h'):
        hours = int(time_value[:-1])
        created_after = (now - datetime.timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    elif time_value.endswith('d'):
        days = int(time_value[:-1])
        created_after = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        created_after = '1970-01-01 00:00:00'

    chat_id = storage_manager.get_chat_id(chat_value)
    flush_history(HISTORY[chat_value], chat_id, chat_value)
    rows = storage_manager.get_chats_created_after(created_after, chat_value)
    text = format_rows(rows) or "Нет записей за выбранный период."

    await BOT.edit_message_text(
        text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    await state.delete()


@BOT.message_handler(state='waiting_summary_since_input', content_types=['text']) 
async def handle_since_input(message: telebot.types.Message, state: StateContext): 
    raw = (message.text or "").strip() 
    try: # Поддержим форматы YYYY-MM-DD и YYYY-MM-DD HH:MM
        if len(raw) == 10: 
            dt = datetime.strptime(raw, "%Y-%m-%d") 
            created_after = dt.strftime("%Y-%m-%d 00:00:00") 
        else: 
            dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S") 
            created_after = dt.strftime("%Y-%m-%d %H:%M:%S") 
    except ValueError: 
        await BOT.reply_to( message, "Неверный формат. Введите дату в формате YYYY-MM-DD или YYYY-MM-DD HH:MM" ) 
        return

    flush_history(HISTORY[chat_name], chat_id, chat_name)
    rows = storage_manager.get_chats_created_after(created_after, "")
    text = format_rows(rows) or "Нет записей за указанный период."

    await BOT.send_message(message.chat.id, text)
    await state.delete()


@BOT.message_handler(content_types=["text"])
async def rememeber_all_messages(message: telebot.types.Message):
    logger.info(f"rememeber_all_messages")
    chat_name = message.chat.title or message.chat.username
    chat_id = storage_manager.get_chat_id(chat_name)

    if chat_name not in HISTORY:
        HISTORY[chat_name] = ChatHistory()

    chat_history = HISTORY[chat_name]
    chat_history.add_message(message)
    if chat_history.total_chars > MAX_CHARS:
        flush_history(chat_history.messages, chat_id, chat_name)
