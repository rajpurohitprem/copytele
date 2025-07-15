import json

CONFIG_FILE = "config.json"

def prompt_int(name):
    while True:
        try:
            return int(input(f"{name}: "))
        except ValueError:
            print("❌ Please enter a valid integer.")

def prompt_str(name):
    val = input(f"{name}: ").strip()
    return val

def main():
    print("🔧 Telegram Bot Config Builder\n")

    config = {
        "api_id": prompt_int("API ID"),
        "api_hash": prompt_str("API Hash"),
        "bot_token": prompt_str("Bot Token"),
        "phone": prompt_str("Phone number (with country code, e.g. +91...)"),
        "admin_id": prompt_int("Admin Telegram User ID")
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Config saved to {CONFIG_FILE}")

if __name__ == "__main__":
    main()
