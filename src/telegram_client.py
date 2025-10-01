import asyncio
from telegram import Bot
from typing import List


class TelegramClient:
    def __init__(self, api_token):
        self.client = Bot(token=api_token)

    async def send_message(self, chat_ids: List[str], text: str):
        await asyncio.gather(
            *[
                self.client.send_message(chat_id=chat_id, text=text)
                for chat_id in chat_ids
            ]
        )
