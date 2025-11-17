from data_base.database import storage_manager
from ml.llm_client import llm
from typing import Optional, Dict, Any, List
from utils.logger import logger
from utils.utils import db_row_to_skill_dict

def list_skills(username: int) -> Dict[str, List[Dict]]:
    """
    Получить список навыков (личных и публичных) для пользователя.
    """
    user_id = storage_manager.get_user_id(username)
    logger.info(f"Вызов list_skills для user_id={user_id}")
    try:
        user_prompt_rows = storage_manager.get_user_prompts(user_id)
        public_prompt_rows = storage_manager.get_public_prompts()

        user_skills = [db_row_to_skill_dict(r) for r in user_prompt_rows]
        public_skills = [db_row_to_skill_dict(r) for r in public_prompt_rows]
        
        return {
            "user_skills": user_skills,
            "public_skills": public_skills
        }
    except Exception as e:
        logger.error(f"Ошибка в list_skills для user_id={user_id}: {e}", exc_info=True)
        return {"error": str(e)}


async def use_skill(username: int, prompt_id: int, params: Optional[Dict[str, Any]] = None, max_tokens_override: Optional[int] = None) -> Dict[str, str]:
    """
    Использование навыка по ID из БД.
    Проверяет, что у пользователя есть доступ (навык публичный или личный).
    """
    user_id = storage_manager.get_user_id(username)
    logger.info(f"Вызов use_skill: user_id={user_id}, prompt_id={prompt_id}, params={params}")
    
    if params is None:
        params = {}

    prompt_row = storage_manager.get_prompt_for_user(user_id=user_id, prompt_id=prompt_id)
    
    if not prompt_row:
        logger.warning(f"Навык (prompt_id={prompt_id}) не найден или недоступен для user_id={user_id}")
        return {"error": "Навык не найден или у вас нет доступа"}
    skill = db_row_to_skill_dict(prompt_row)

    try:
        prompt_content = skill["prompt"].format(**params)
    except KeyError as e:
        logger.error(f"Для навыка '{skill['name']}' (ID: {prompt_id}) нет параметра: {e}")
        return {"error": f"Нет параметра: {e}"}
    except Exception as e:
        logger.error(f"Ошибка форматирования промпта для ID: {prompt_id}: {e}", exc_info=True)
        return {"error": f"Ошибка форматирования промпта: {e}"}

    final_max_tokens = max_tokens_override or skill["max_tokens"]
    system = "Ты эксперт по маркетингу и бизнес-коммуникациям. Отвечай кратко, структурировано."

    try:
        response = await llm.chat(
            system=system,
            user=prompt_content,
            max_tokens=final_max_tokens
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Ошибка в use_skill (вызов LLM): {e}", exc_info=True)
        return {"error": str(e)}


def add_skill(username: int, title: str, prompt_content: str, description: Optional[str] = None, is_public: bool = False, max_tokens: int = 2000) -> Dict[str, str]:
    """
    Добавление нового навыка (промпта) в БД.
    Навык автоматически 'сохраняется' для создавшего его пользователя.
    """
    user_id = storage_manager.get_user_id(username)
    logger.info(f"Вызов add_skill: user_id={user_id}, title='{title}'")
    try:
        prompt_id = storage_manager.add_prompt(
            title=title,
            content=prompt_content,
            created_by=user_id,
            description=description,
            is_public=is_public,
            max_tokens=max_tokens
        )
        
        storage_manager.link_prompt_to_user(user_id, prompt_id)
        
        return {"status": "ok", "message": "Навык добавлен", "prompt_id": prompt_id}
    except Exception as e:
        logger.error(f"Ошибка в add_skill: {e}", exc_info=True)
        return {"error": f"Не удалось добавить навык: {e}"}