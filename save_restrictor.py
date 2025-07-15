import os
from telethon.tl.types import Message

# Make sure downloads folder exists
os.makedirs("downloads", exist_ok=True)

async def save_messages_in_range(bot, anon, start_id, end_id, event):
    from config import load_json
    config = load_json()

    src_id = config.get("source_channel_id")
    tgt_id = config.get("target_channel_id")

    if not src_id or not tgt_id:
        await bot.send_message(event.chat_id, "❗ Source or Target channel ID missing in config.")
        return

    src = await anon.get_entity(src_id)
    tgt = await anon.get_entity(tgt_id)

    sent_count = 0

    await bot.send_message(event.chat_id, f"📥 Saving messages from `{start_id}` to `{end_id}`...")

    for msg_id in range(start_id, end_id + 1):
        try:
            msg = await anon.get_messages(src, ids=msg_id)
            if not msg or not isinstance(msg, Message):
                continue

            if msg.media:
                file_path = await anon.download_media(msg, file="downloads/")
                if file_path:
                    await anon.send_file(
                        tgt,
                        file_path,
                        caption=msg.text or msg.message or ""
                    )
                    os.remove(file_path)
            elif msg.text or msg.message:
                await anon.send_message(tgt, msg.text or msg.message)

            sent_count += 1

        except Exception as e:
            await bot.send_message(event.chat_id, f"❌ Error at ID {msg_id}: {e}")

    await bot.send_message(event.chat_id, f"✅ Done! Total messages saved: `{sent_count}`.")
