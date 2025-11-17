from typing import Optional, Dict, Any, List
from utils.utils import logger
from ml.llm_client import llm

async def chat(message: str, max_tokens: int = 200) -> Dict[str, str]:
    """
    Обычное общение (без навыков).
    """
    logger.info(f"Вызов chat: '{message[:50]}...', max_tokens={max_tokens}")
    system = "Ты умный и дружелюбный ассистент. Отвечай кратко, по делу, на русском языке."
    
    try:
        response = await llm.chat(
            system=system,
            user=message,
            max_tokens=max_tokens
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Ошибка в функции chat: {e}", exc_info=True)
        return {"error": str(e)}
