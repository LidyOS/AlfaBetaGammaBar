import telebot
from core.skills import list_skills, use_skill, add_skill
from tg_bot.utils import wait_wessage
from utils.logger import logger
from tg_bot.constants import BOT
from data_base.database import storage_manager


@BOT.message_handler(commands=['skills'])
async def get_all_skills(message: telebot.types.Message):
    logger.info(f"get_all_skills")

    username = message.from_user.username

    all_skills = list_skills(username)
    if 'error' in all_skills:
        await BOT.reply_to(
            message,
            "Упс, не получилось ответить. Попробуйте ещё раз.",
        )
        return
    logger.info(f"{all_skills}")

    keyboard = telebot.types.InlineKeyboardMarkup(
        keyboard=[
            [
                telebot.types.InlineKeyboardButton(
                    text=user_skill['name'],
                    callback_data=f'select_skill={user_skill['id']}'
                )
            ]
            for user_skill in all_skills['user_skills']
            # for skills in all_skills
        ]
        +
        [
            [
                telebot.types.InlineKeyboardButton(
                    text=public_skill['name'],
                    callback_data=f'select_skill={public_skill['id']}'
                )
            ]
            for public_skill in all_skills['public_skills']
        ]
    )

    logger.info(f"{keyboard.keyboard}")

    if not all_skills['public_skills'] and not all_skills['user_skills']:
        await BOT.send_message(message.chat.id, "У вас нет навыков. Попробуйте создать новый")
        return 

    await BOT.reply_to(message, "Выбери навыки которые хочешь использовать", reply_markup=keyboard)


@BOT.callback_query_handler(func=lambda call: call.data.startswith('select_skill'))
async def select_skill(call: telebot.types.CallbackQuery):
    logger.info(f"select_skill")
    message = call.message
    username = call.from_user.username
    chat_id = message.chat.id
    prompt_id = int(call.data[len('select_skill='):])

    await wait_wessage(message, use_skill, username, prompt_id)



@BOT.message_handler(commands=['add_skill'])
async def get_all_skills(message: telebot.types.Message):
    pass