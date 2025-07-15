# bot_controller.py
import asyncio
import json
from telethon import TelegramClient, events, Button, idle
from save_restrictor import get_channel_list, set_config_key, save_messages_in_range
from config import load_json

config = load_json()
bot = TelegramClient("bot", config["api_id"], config["api_hash"]).start(bot_token=config["bot_token"])

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    await event.respond(
        "**Welcome to Save Restrict Bot**\n\n"
        "Commands:\n"
        "/set_source - Set source channel\n"
        "/set_target - Set target channel\n"
        "/set_log - Set log channel\n"
        "/save <start_id>-<end_id> - Save message range\n"
        "/check_access - Check anon client channel access\n"
        "/panel - Show control panel"
    )

@bot.on(events.NewMessage(pattern="/panel"))
async def panel_handler(event):
    await event.respond(
        "🔘 Choose Action",
        buttons=[
            [Button.inline("📥 Set Source", "set_src")],
            [Button.inline("📤 Set Target", "set_tgt")],
            [Button.inline("🧾 Set Log", "set_log")],
            [Button.inline("✅ Check Access", "check_access")]
        ]
    )

@bot.on(events.NewMessage(pattern=r"/save (\d+)-(\d+)"))
async def save_handler(event):
    start_id, end_id = map(int, event.pattern_match.groups())
    msg = await event.respond(f"📦 Saving messages {start_id} to {end_id}...")
    await save_messages_in_range(start_id, end_id, msg, bot)

@bot.on(events.NewMessage(pattern="/check_access"))
async def access_check(event):
    from save_restrictor import check_channel_access
    msg = await event.respond("🔍 Checking channel access...")
    ok = await check_channel_access()
    if ok:
        await msg.edit("✅ Anon client is joined to source and target channels.")
    else:
        await msg.edit("❌ Anon client is NOT in one or more channels.")

@bot.on(events.NewMessage(pattern="/set_source"))
async def manual_set_source(event):
    msg = event.raw_text.strip().split()
    if len(msg) < 2:
        return await event.respond("Usage: `/set_source <channel_id>`")
    try:
        set_config_key("source_channel_id", int(msg[1]))
        await event.respond("✅ Source channel set manually.")
    except:
        await event.respond("❌ Failed to set source channel.")

@bot.on(events.NewMessage(pattern="/set_target"))
async def manual_set_target(event):
    msg = event.raw_text.strip().split()
    if len(msg) < 2:
        return await event.respond("Usage: `/set_target <channel_id>`")
    try:
        set_config_key("target_channel_id", int(msg[1]))
        await event.respond("✅ Target channel set manually.")
    except:
        await event.respond("❌ Failed to set target channel.")

@bot.on(events.NewMessage(pattern="/set_log"))
async def manual_set_log(event):
    msg = event.raw_text.strip().split()
    if len(msg) < 2:
        return await event.respond("Usage: `/set_log <channel_id>`")
    try:
        set_config_key("log_channel_id", int(msg[1]))
        await event.respond("✅ Log channel set manually.")
    except:
        await event.respond("❌ Failed to set log channel.")

# Inline button handling
@bot.on(events.CallbackQuery(data=lambda d: d in [b"set_src", b"set_tgt", b"set_log"]))
async def inline_channel_select(event):
    chs = await get_channel_list()
    n = event.data.decode().split("_")[-1]
    btns = [
        Button.inline(f"{d.title[:30]} [{str(d.id)[-4:]}]", f"set_{n}:{d.id}")
        for d in chs
    ]
    await event.edit(f"Select {n} channel ({len(btns)} found):", buttons=[[b] for b in btns])

@bot.on(events.CallbackQuery(pattern=r"set_(src|tgt|log):"))
async def set_id_handler(event):
    key, cid = event.data.decode().split(":")
    real_key = {
        "src": "source_channel_id",
        "tgt": "target_channel_id",
        "log": "log_channel_id"
    }.get(key)
    set_config_key(real_key, int(cid))
    await event.edit(f"✅ {real_key.replace('_', ' ').title()} set to `{cid}`", buttons=None)

if __name__ == "__main__":
    print("🚀 Bot controller started.")
    async def main():
        print("🚀 Bot controller started.")
        await bot.start()
        await idle()  # Keep the bot running

    asyncio.run(main())
    bot.run_until_disconnected()
