from core.skills import *
from core.chat import *
from core.summarize import *
#from backend.tg_bot import bot

async def test():
    print(list_skills("Dashevich"))
    ids = add_skill(username='Dashevich', title="Пост в инстаграмм", prompt_content="Напиши пять идея для поста в инстаграмм")
    resp = await use_skill(username='Dashevich', prompt_id=ids['prompt_id'])
    print(resp)
    print(list_skills(username='Dashevich'))

#bot.infinity_polling()

import asyncio
asyncio.run(test())
