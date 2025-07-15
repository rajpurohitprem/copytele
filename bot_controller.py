import asyncio
import json
from telethon import TelegramClient, events, Button
from config import load_json
from save_restrictor import (
    get_channel_list, set_config_key, channel_cache,
    get_paginated_buttons, save_messages_in_range,
    check_joined_status
)

config = load_json()
bot = TelegramClient("bot", config["api_id"], config["api_hash"]).start(bot_token=config["bot_token"])
anon = TelegramClient("anon", config["api_id"], config["api_hash"])


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("🤖 Save Restrict Bot Ready!\nUse /panel to open control panel.")

@bot.on(events.NewMessage(pattern="/panel"))
async def panel(event):
    buttons = [
        [Button.inline("📤 Set Source", b"panel_set_source")],
        [Button.inline("📥 Set Target", b"panel_set_target")],
        [Button.inline("🛠 Check Access", b"panel_check_access")]
    ]
    await event.respond("🔘 Control Panel", buttons=buttons)

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

@bot.on(events.CallbackQuery(pattern=b"panel_set_source"))
async def panel_source_cb(event):
    await set_source(event)

@bot.on(events.CallbackQuery(pattern=b"panel_set_target"))
async def panel_target_cb(event):
    await set_target(event)

@bot.on(events.CallbackQuery(pattern=b"panel_check_access"))
async def panel_check_access(event):
    await anon.start()
    result = await check_joined_status(anon)
    await event.respond(result)

@bot.on(events.NewMessage(pattern="/check_access"))
async def check_access(event):
    await anon.start()
    result = await check_joined_status(anon)
    await event.respond(result)

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

@bot.on(events.NewMessage(pattern=r"/save (\d+)-(\d+)"))
async def save_range(event):
    await anon.start()
    start_id = int(event.pattern_match.group(1))
    end_id = int(event.pattern_match.group(2))
    await event.respond(f"📥 Saving messages from {start_id} to {end_id}...")
    await save_messages_in_range(anon, start_id, end_id, bot, event)

if __name__ == "__main__":
    print("🚀 Bot controller started.")
    with bot:
        bot.run_until_disconnected()
