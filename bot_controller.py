import asyncio
import json
from telethon import TelegramClient, events, Button
from config import load_json
from save_restrictor import get_channel_list, set_config_key, channel_cache, get_paginated_buttons

config = load_json()
bot = TelegramClient("bot", config["api_id"], config["api_hash"]).start(bot_token=config["bot_token"])
anon = TelegramClient("anon", config["api_id"], config["api_hash"])

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("🤖 Save Restrict Bot Ready!")

@bot.on(events.NewMessage(pattern="/set_source"))
async def set_source(event):
    await anon.start()
    await get_channel_list(anon, limit=1000)
    buttons = get_paginated_buttons(0, "/set_source")
    await event.respond("📤 Select Source Channel", buttons=buttons)

@bot.on(events.NewMessage(pattern="/set_target"))
async def set_target(event):
    await anon.start()
    await get_channel_list(anon, limit=1000)
    buttons = get_paginated_buttons(0, "/set_target")
    await event.respond("📥 Select Target Channel", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"/set_source_page_(\d+)"))
async def paginate_source(event):
    page = int(event.pattern_match.group(1))
    buttons = get_paginated_buttons(page, "/set_source")
    await event.edit("📤 Select Source Channel", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"/set_target_page_(\d+)"))
async def paginate_target(event):
    page = int(event.pattern_match.group(1))
    buttons = get_paginated_buttons(page, "/set_target")
    await event.edit("📥 Select Target Channel", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=r"/set_source_(-?\d+)"))
async def set_source_channel(event):
    channel_id = int(event.pattern_match.group(1))
    set_config_key("source_channel_id", channel_id)
    await event.respond(f"✅ Source channel set to `{channel_id}`.")
    await event.delete()

@bot.on(events.CallbackQuery(pattern=r"/set_target_(-?\d+)"))
async def set_target_channel(event):
    channel_id = int(event.pattern_match.group(1))
    set_config_key("target_channel_id", channel_id)
    await event.respond(f"✅ Target channel set to `{channel_id}`.")
    await event.delete()

if __name__ == "__main__":
    print("🚀 Bot controller started.")
    with bot:
        bot.run_until_disconnected()