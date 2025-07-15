from telethon.sync import TelegramClient
from config import load_json

config = load_json()
client = TelegramClient("anon", config["api_id"], config["api_hash"])

async def test():
    await client.start(phone=config["phone"])
    tgt = await client.get_entity(config["target_channel_id"])
    await client.send_message(tgt, "✅ Test message from script!")

import asyncio
asyncio.run(test())
