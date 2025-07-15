# login_anon.py
from telethon.sync import TelegramClient
#from telethon.errors import ValueError
from config import load_json

config = load_json()

client = TelegramClient("anon", config["api_id"], config["api_hash"])

client.start(phone=config["phone"])
print("✅ anon.session created and logged in.")

# Check channel membership
def check_channel(channel_id, name):
    try:
        entity = client.get_entity(int(channel_id))
        print(f"✅ {name} channel joined: {entity.title}")
    except Exception as e:
        print(f"❌ {name} channel not accessible: {e}")

print("\n🔎 Checking channel access...")
check_channel(config.get("source_channel_id"), "Source")
check_channel(config.get("target_channel_id"), "Target")
