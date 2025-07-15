# bot_controller.py

import json
import os
import asyncio
from telethon import TelegramClient, events
from save_restrictor import save_messages_in_range

# Load config
CONFIG_FILE = "config.json"
SESSION_FILE = "anon"

def load_json():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_json(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

config = load_json()
API_ID = config.get("api_id")
API_HASH = config.get("api_hash")
BOT_TOKEN = config.get("bot_token")
ADMIN_ID = config.get("admin_id")

# Create clients
anon = TelegramClient(SESSION_FILE, API_ID, API_HASH)
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

current_task = None

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id != ADMIN_ID:
        return
    await event.respond("🤖 *Save Restrict Bot Ready!*\n\n"
                        "Commands:\n"
                        "`/set_source <id>`\n"
                        "`/set_target <id>`\n"
                        "`/save <start>-<end>`\n"
                        "`/stop`",
                        parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/set_source (-?\d+)"))
async def set_source(event):
    if event.sender_id != ADMIN_ID:
        return
    ch_id = int(event.pattern_match.group(1))
    config = load_json()
    config["source_channel_id"] = ch_id
    save_json(config)
    await event.respond(f"✅ Source channel set to ID: `{ch_id}`", parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/set_target (-?\d+)"))
async def set_target(event):
    if event.sender_id != ADMIN_ID:
        return
    ch_id = int(event.pattern_match.group(1))
    config = load_json()
    config["target_channel_id"] = ch_id
    save_json(config)
    await event.respond(f"✅ Target channel set to ID: `{ch_id}`", parse_mode="md")

@bot.on(events.NewMessage(pattern=r"/save (\d+)-(\d+)"))
async def save_range(event):
    global current_task
    if event.sender_id != ADMIN_ID:
        return
    start_id = int(event.pattern_match.group(1))
    end_id = int(event.pattern_match.group(2))

    await event.respond(f"📥 Saving messages from `{start_id}` to `{end_id}`...", parse_mode="md")

    async def run_save():
        await save_messages_in_range(bot, anon, start_id, end_id, event)

    current_task = asyncio.create_task(run_save())

@bot.on(events.NewMessage(pattern="/stop"))
async def stop(event):
    global current_task
    if event.sender_id != ADMIN_ID:
        return
    if current_task:
        current_task.cancel()
        await event.respond("⛔ Task stopped.")
        current_task = None
    else:
        await event.respond("ℹ️ No task running.")

if __name__ == "__main__":
    anon.start()
    bot.start()
    print("✅ Bot is running...")
    bot.run_until_disconnected()
