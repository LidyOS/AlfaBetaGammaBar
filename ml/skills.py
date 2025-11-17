# class SkillRegistry:
#     def __init__(self):
#         # Встроенные навыки
#         self.skills = {
#             "social_post": {
#                 "name": "Генерация соц. поста",
#                 "prompt": """Создай короткий пост для соцсетей на тему: {topic}
# Стиль: {tone}.
# Включи призыв к действию и хэштеги.""",
#                 "max_tokens": 2000
#             },
#             "audience_analysis": {
#                 "name": "Анализ целевой аудитории",
#                 "prompt": """Проанализируй целевую аудиторию продукта: {product}
# Формат:
# 1. Сегменты
# 2. Демография
# 3. Боли
# 4. Рекомендации""",
#                 "max_tokens": 2000
#             }
#         }

#     def get_all(self):
#         return self.skills

#     def get(self, skill_id):
#         return self.skills.get(skill_id)

#     def add(self, skill_id: str, prompt: str, max_tokens: int = 350):
#         self.skills[skill_id] = {
#             "name": skill_id,
#             "prompt": prompt,
#             "max_tokens": max_tokens
#         }
