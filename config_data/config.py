import os
from pydantic import BaseModel, Field

class TgBot(BaseModel):
    token: str = Field(..., env="TG_BOT_TOKEN")

class GigaChat(BaseModel):
    token: str = Field(..., env="GIGACHAT_TOKEN")

class Config(BaseModel):
    tg_bot: TgBot
    gigachat_token: str


def load_config() -> Config:
    return Config(
        tg_bot=TgBot(token=os.getenv("TG_BOT_TOKEN", "6896115286:AAFIqKvAK_Y9h1QJ6s2VEQyWZgPFCh0YIqM")),
        gigachat_token=os.getenv("GIGACHAT_TOKEN", "NmRjYTc0NGMtODVmNy00YTg3LWJjZmQtY2Q4OGM0MzVhMWZkOjc4MDE3ZGQ3LTJiZDMtNDY2Ny1iNDY4LWU1NmYyYmI3MDNmMQ==")
    )
