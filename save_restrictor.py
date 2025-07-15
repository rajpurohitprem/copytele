from telethon.tl.custom import Button

channel_cache = []

async def get_channel_list(client, limit=1000):
    global channel_cache
    channel_cache = []
    count = 0
    async for dialog in client.iter_dialogs():
        if dialog.is_channel and not dialog.is_user:
            channel_cache.append(dialog)
            count += 1
            if count >= limit:
                break
    return channel_cache

def get_paginated_buttons(page: int, cmd_prefix: str, per_page: int = 100):
    total = len(channel_cache)
    start = page * per_page
    end = min(start + per_page, total)

    buttons = []
    for dialog in channel_cache[start:end]:
        label = dialog.name[:30] or "Unnamed"
        buttons.append([Button.inline(label, f"{cmd_prefix}_{dialog.entity.id}")])

    nav = []
    if start > 0:
        nav.append(Button.inline("⏮ Prev", f"{cmd_prefix}_page_{page-1}"))
    if end < total:
        nav.append(Button.inline("⏭ Next", f"{cmd_prefix}_page_{page+1}"))
    if nav:
        buttons.append(nav)

    return buttons

def set_config_key(key, value):
    import json
    with open("config.json", "r") as f:
        config = json.load(f)
    config[key] = value
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)