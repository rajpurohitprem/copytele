# save_restrictor.py
import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import Message
from config import load_json, set_config_key
from tqdm import tqdm

CONFIG = load_json()
SESSION = "anon"
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

anon = TelegramClient(SESSION, CONFIG["api_id"], CONFIG["api_hash"])

async def get_channel_list():
    await anon.connect()
    dialogs = await anon.get_dialogs()
    return [d.entity for d in dialogs if d.is_channel and not d.is_user]

def set_config_key(key, value):
    CONFIG[key] = value
    with open("config.json", "w") as f:
        json.dump(CONFIG, f, indent=2)

async def check_channel_access():
    try:
        await anon.connect()
        await anon.get_entity(int(CONFIG["source_channel_id"]))
        await anon.get_entity(int(CONFIG["target_channel_id"]))
        return True
    except:
        return False

async def save_messages_in_range(start_id, end_id, msg_obj, bot):
    await anon.connect()
    src = await anon.get_entity(int(CONFIG["source_channel_id"]))
    tgt = await anon.get_entity(int(CONFIG["target_channel_id"]))

    total = end_id - start_id + 1
    progress = tqdm(total=total, desc="Processing", unit="msg")

    for msg_id in range(start_id, end_id + 1):
        try:
            msg = await anon.get_messages(src, ids=msg_id)
            if not msg or not isinstance(msg, Message):
                continue

            text = msg.text or msg.message or ""

            if msg.media:
                path = await anon.download_media(msg, file=DOWNLOAD_DIR)
                if path:
                    await anon.send_file(tgt, path, caption=text)
                    os.remove(path)
            elif text:
                await anon.send_message(tgt, text)

            progress.update(1)

        except Exception as e:
            await bot.send_message(CONFIG.get("log_channel_id"), f"❌ Failed for ID {msg_id}: {e}")
    progress.close()
    await msg_obj.edit(f"✅ Done saving {total} messages.")

