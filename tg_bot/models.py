
import telebot


MAX_CHARS = 1000

class ChatHistory:
    def __init__(self):
        self.messages: list[telebot.types.Message] = []
        self.total_chars: int = 0
    
    def add_message(self, message: telebot.types.Message):
        self.messages.append(message)
        self.total_chars += len(message.text)

