


from math import lcm
from telebot import logger
from core.summarize import summarize_chat_history
from tg_bot.constants import BOT, HISTORY
from data_base.database import storage_manager
from tg_bot.models import ChatHistory


async def wait_wessage(message, function, *args, state = None):
    thinking_msg = await BOT.send_message(message.chat.id, "Думаю…")

    try:
        answer = await function(*args)
        if not answer or 'response' not in answer:
            answer = "Не удалось получить ответ."
    except Exception as e:
        logger.exception("chat() failed")
        await BOT.edit_message_text(
            "Упс, не получилось ответить. Попробуйте ещё раз.",
            chat_id=message.chat.id,
            message_id=thinking_msg.message_id
        )
        if state is not None:
            await state.delete()
        return

    # Если ответ помещается в одно сообщение — просто редактируем «Думаю…»
    response = answer['response']
    if len(response) <= 4096:
        await BOT.edit_message_text(
            response,
            chat_id=message.chat.id,
            message_id=thinking_msg.message_id
        )
    else:
        # Иначе редактируем первым куском и досылаем остальные
        chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
        await BOT.edit_message_text(
            chunks[0],
            chat_id=message.chat.id,
            message_id=thinking_msg.message_id
        )
        for chunk in chunks[1:]:
            await BOT.send_message(message.chat.id, chunk)
    if state is not None:
        await state.delete()



def format_rows(rows) -> str: 
    text = '\n'.join(row['summarize'] for row in rows)
    return text[:4096]


def flush_history(messages, chat_id, chat_name):
    summary = summarize_chat_history(lcm, messages)
    storage_manager.add_chat(chat_id, summary)
    HISTORY[chat_name] = ChatHistory()