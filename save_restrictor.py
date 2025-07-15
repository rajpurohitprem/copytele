import os
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest, UpdatePinnedMessageRequest
from telethon.tl.types import Message
from tqdm import tqdm

CONFIG_FILE = "config.json"
SESSION = "anon"
SENT_LOG = "sent_ids.txt"
ERROR_LOG = "errors.txt"

os.makedirs("downloads", exist_ok=True)
open(SENT_LOG, "a").close()
open(ERROR_LOG, "a").close()

def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)

def log_error(msg):
    with open(ERROR_LOG, "a") as f:
        f.write(msg + "\n")

async def get_channel_list(client):
    dialogs = await client.get_dialogs()
    return [d for d in dialogs if d.is_channel and not d.is_user]

async def is_forward_restricted(client, entity):
    try:
        history = await client(GetHistoryRequest(
            peer=entity, offset_id=0, offset_date=None,
            add_offset=0, limit=1, max_id=0, min_id=0, hash=0))
        return not history.messages or not getattr(history.messages[0], 'forward', None)
    except:
        return True

async def save_messages_in_range(start_id, end_id, send_status, client):
    config = load_config()
    source = await client.get_entity(int(config["source_channel_id"]))
    target = await client.get_entity(int(config["target_channel_id"]))

    sent = 0
    for msg_id in range(start_id, end_id + 1):
        try:
            msg = await client.get_messages(source, ids=msg_id)
            if not isinstance(msg, Message):
                continue

            if msg.media:
                path = await client.download_media(msg, file="downloads/")
                if path:
                    await client.send_file(target, path, caption=msg.text or "")
                    os.remove(path)
            elif msg.text or msg.message:
                await client.send_message(target, msg.text or msg.message)

            if msg.pinned:
                try:
                    await client(UpdatePinnedMessageRequest(peer=target, id=msg_id, silent=True))
                except: pass

            with open(SENT_LOG, "a") as f:
                f.write(f"{msg_id}\n")

            sent += 1
            await asyncio.sleep(0.5)

        except Exception as e:
            log_error(f"Failed {msg_id}: {e}")

        await send_status(f"Cloned {sent} messages so far...")

    await send_status(f"✅ Done. Total: {sent} messages.")

