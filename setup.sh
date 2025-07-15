#!/data/data/com.termux/files/usr/bin/bash

echo "📦 Setting up Save Restrict Bot in Termux..."

# 1. Update Termux packages
pkg update -y && pkg upgrade -y

# 2. Install Python & Git
pkg install -y python git

# 3. Clone your GitHub repo
cd Copytele || { echo "❌ Failed to cd into Copy"; exit 1; }

# 4. Install Python requirements
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create downloads folder (for media)
mkdir -p downloads

# 6. Ask user to generate config.json
echo -e "\n🔧 Launching JSON Config Builder..."
python json_builder.py

# 7. Final ready message
echo -e "\n✅ Setup Complete! You can now run:"
echo "python bot_controller.py"

# Optional: Auto-start bot after setup
# python bot_controller.py
