import os
from telethon.tl.types import Message

os.makedirs("downloads", exist_ok=True)

async def save_messages_in_range(anon, start_id, end_id, progress_hook):
    from config import load_json
    cfg = load_json()
    src_id, tgt_id = cfg.get("source_channel_id"), cfg.get("target_channel_id")
    if not src_id or not tgt_id:
        await progress_hook("❗ Missing source/target in config.")
        return

    src = await anon.get_entity(src_id)
    tgt = await anon.get_entity(tgt_id)
    total = end_id - start_id + 1
    done = 0

    await progress_hook(f"⏳ Starting: {total} msgs from {start_id} to {end_id}")

    for msg_id in range(start_id, end_id + 1):
        try:
            msg = await anon.get_messages(src, ids=msg_id)
            if not msg or not isinstance(msg, Message):
                continue

            if msg.media:
                path = await anon.download_media(msg, file="downloads/")
                if path:
                    await anon.send_file(tgt, path, caption=msg.text or "", silent=True)
                    os.remove(path)
            elif msg.text:
                await anon.send_message(tgt, msg.text, silent=True)

            done += 1

        except Exception as e:
            await progress_hook(f"❌ Failed ID {msg_id}: {e}")

        if done % 5 == 0 or done == total:
            await progress_hook(f"📤 Sent {done}/{total}")

    await progress_hook(f"✅ Completed! {done}/{total} messages copied.")
