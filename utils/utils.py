import sqlite3
from typing import Optional, Dict, Any
from .logger import logger

def db_row_to_skill_dict(row: sqlite3.Row) -> Optional[Dict[str, Any]]:
    if not row:
        return None
    return {
        "id": row["id"],
        "name": row["title"],
        "description": row["description"],
        "prompt": row["content"],
        "max_tokens": row["max_tokens"],
        "is_public": bool(row["is_public"]),
        "created_by": row["created_by"],
    }

def populate_initial_public_skills(db_manager, system_username=""):
    """
    Добавляет в БД набор "встроенных" публичных навыков: генерация универсальных бизнес-текстов без подстановки переменных.
    """
    logger.info(f"Заполнение БД встроенными навыками от username='{system_username}'...")
    
    system_user_id = db_manager.get_user_id(system_username)
    exists_promts = db_manager.get_public_prompts()
    if  exists_promts:
        return 

    
    initial_skills = {
        "business_task_text": {
            "name": "Генерация текста бизнес-задачи",
            "prompt": "Составь грамотное описание бизнес-задачи: четко сформулируй цель, ожидаемый результат, сроки и рекомендации для исполнителя.",
            "max_tokens": 1000
        },
        "meeting_summary": {
            "name": "Суммаризация встречи или обсуждения",
            "prompt": "Сделай краткое резюме деловой встречи или обсуждения: выдели основные выводы, решения, ключевые итоги для бизнеса.",
            "max_tokens": 800
        },
        "email_business": {
            "name": "Текст делового письма",
            "prompt": "Сгенерируй образец письма бизнес-партнеру: добавь приветствие, основную часть, призыв к сотрудничеству и структуру для делового контакта.",
            "max_tokens": 1200
        },
        "business_post": {
            "name": "Пост в корпоративный чат",
            "prompt": "Напиши короткий мотивационный пост для корпоративного чата или канала, направленный на улучшение командной работы.",
            "max_tokens": 600
        },
        "business_tip": {
            "name": "Совет для бизнеса",
            "prompt": "Сформулируй лаконичный совет для предпринимателей или команды, как решить бизнес-задачу, улучшить процесс, повысить эффективность.",
            "max_tokens": 600
        },
        "product_pitch": {
            "name": "Презентация продукта или услуги",
            "prompt": "Создай текст для краткой презентации продукта или услуги, акцентируй ценность, выгоду и призыв к действию.",
            "max_tokens": 1000
        },
        "problem_analysis": {
            "name": "Анализ бизнес-проблемы",
            "prompt": "Сделай структурированный разбор бизнес-проблемы: выдели причины, последствия и предложи логичное решение.",
            "max_tokens": 1000
        }
    }
    
    count = 0
    for skill_id, data in initial_skills.items():
        try:
            db_manager.add_prompt(
                title=data["name"],
                content=data["prompt"],
                created_by=system_user_id,
                description=f"Встроенный навык: {skill_id}",
                is_public=True,
                max_tokens=data["max_tokens"]
            )
            count += 1
        except Exception as e:
            logger.error(f"Не удалось добавить встроенный навык '{skill_id}': {e}", exc_info=True)
            
    logger.info(f"Успешно добавлено {count} из {len(initial_skills)} встроенных навыков.")