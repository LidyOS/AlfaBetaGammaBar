from typing import Optional, Dict, Any, List
from ml.llm_client import llm
from utils.utils import logger


async def summarize_chat_history(llm, messages: list[str], max_tokens: int = 500) -> str:
    """
    Суммаризация списка сообщений вида:
    ["[user1] текст", "[user2] текст", ...]
    
    llm — твой клиент LLMClient
    messages — список строк от бэкенда
    """

    # Склеиваем историю в единый текст
    joined_history = "\n".join(messages)

    system_prompt = (
        "Ты — ассистент, который делает краткую и точную суммаризацию "
        "истории диалога между несколькими пользователями.\n\n"
        "Правила:\n"
        "- Сохраняй структуру смысла, а не дословные цитаты.\n"
        "- Не переписывай имена пользователей, просто учитывай контекст.\n"
        "- Объединяй повторяющиеся мысли.\n"
        "- Игнорируй неинформативные фразы.\n"
        "- Финальная длина: 3–6 предложений.\n"
        "- Пиши только сам summary, без вступлений и пояснений."
    )

    user_prompt = f"Вот история сообщений:\n{joined_history}\n\nСделай сжатое содержательное резюме."

    return await llm.chat(
        system=system_prompt,
        user=user_prompt,
        max_tokens=max_tokens
    )
