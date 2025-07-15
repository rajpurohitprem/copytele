import json
import asyncio
from telethon.sync import TelegramClient, events, Button
from save_restrictor import save_messages_in_range, get_channel_list, is_forward_restricted

CONFIG_FILE = "config.json"
SESSION = "anon"

with open(CONFIG_FILE) as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
bot_token = config["bot_token"]
admin_id = config.get("admin_id")  # Your Telegram user ID

client = TelegramClient(SESSION, api_id, api_hash)
bot = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    if event.sender_id != admin_id:
        return
    await event.respond(
        "👋 Choose an action:",
        buttons=[
            [Button.inline("📥 Set Source", b"set_source"), Button.inline("📤 Set Target", b"set_target")],
            [Button.inline("📁 Set Log Channel", b"set_log"), Button.inline("🔧 View Config", b"view_cfg")]
        ]
    )

@bot.on(events.CallbackQuery)
async def callback_handler(event):
    if event.sender_id != admin_id:
        return

    action = event.data.decode()
    await event.answer()

    async with client:
        channels = await get_channel_list(client)
        buttons = [Button.inline(c.title, f"{action}:{c.entity.id}".encode()) for c in channels]
        await event.edit("Select channel:", buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"(set_.*?)\:"))
async def set_channel_handler(event):
    action, cid = event.data.decode().split(":")
    cid = int(cid)
    config[action.replace("set_", "") + "_channel_id"] = cid

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    async with client:
        entity = await client.get_entity(cid)
        name = entity.title
        restricted = await is_forward_restricted(client, entity) if action == "set_source" else False

    msg = f"✅ {action.replace('set_', '').capitalize()} set to {name}"
    if restricted and action == "set_source":
        msg += "\n⚠️ Source is forward-restricted."

    await event.edit(msg)

@bot.on(events.NewMessage(pattern="/view"))
async def view(event):
    if event.sender_id != admin_id:
        return
    info = f"""
🔧 Config:
API: {config["api_id"]}
Phone: {config["phone"]}
Source: {config.get("source_channel_id", "Not Set")}
Target: {config.get("target_channel_id", "Not Set")}
Log: {config.get("log_channel_id", "Not Set")}
"""
    await event.respond(info)

@bot.on(events.NewMessage(pattern=r"/save (\d+)-(\d+)"))
async def save_range(event):
    if event.sender_id != admin_id:
        return
    start_id, end_id = map(int, event.pattern_match.groups())

    msg = await event.respond(f"⏳ Saving messages {start_id} to {end_id}...")

    async def update_progress(text):
        await msg.edit(text)

    async with client:
        await save_messages_in_range(start_id, end_id, update_progress, client)

print("🤖 Bot running...")
bot.run_until_disconnected()
