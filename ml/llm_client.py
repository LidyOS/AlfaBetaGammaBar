from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

class AsyncLLMClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        # model: str = "tngtech/deepseek-r1t2-chimera:free"
        model: str = "meta-llama/llama-3.3-70b-instruct:free",
    ):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

    async def chat(self, system: str, user: str, max_tokens: int = 300):
        """Асинхронная отправка запроса к модели"""

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.7,
            max_tokens=max_tokens
        )

        return completion.choices[0].message.content

load_dotenv() 
API_KEY = os.getenv('CREDENTIALS')
llm = AsyncLLMClient(api_key=API_KEY)