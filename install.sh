#!/bin/bash

# AI Workflow Shield - Guardian Agent Installation Script
# Usage: curl -s https://shield.mangotec.ai/install | bash

set -e

echo "🚀 Installing AI Workflow Shield Guardian Agent..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8+ first."
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/.shield-agent"
mkdir -p "$INSTALL_DIR"

# Clone or download agent files
echo "📦 Downloading agent files..."
# In production, this would download from a CDN or git repo
# For now, assume files are in current directory

# Install Python dependencies
echo "📚 Installing dependencies..."
pip3 install -r requirements.txt --user

# Create config file
echo "⚙️  Creating configuration..."
cat > "$INSTALL_DIR/config.env" << EOF
SHIELD_AGENT_ID=$(hostname)-$(date +%s)
SHIELD_WORKSPACE_ID=default
SHIELD_INGESTION_ENDPOINT=https://shield.mangotec.ai/api/v1/ingest
SHIELD_BATCH_SIZE=50
SHIELD_BATCH_INTERVAL=30
EOF

# Create systemd service (Linux)
if command -v systemctl &> /dev/null; then
    echo "🔧 Creating systemd service..."
    sudo tee /etc/systemd/system/shield-agent.service > /dev/null << EOF
[Unit]
Description=AI Workflow Shield Guardian Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$INSTALL_DIR/config.env
ExecStart=$(which python3) $INSTALL_DIR/guardian-agent/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    echo "✅ Service created. Start with: sudo systemctl start shield-agent"
fi

# Create launchd plist (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🔧 Creating launchd service..."
    cat > "$HOME/Library/LaunchAgents/com.mangotec.shield-agent.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mangotec.shield-agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which python3)</string>
        <string>$INSTALL_DIR/guardian-agent/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>SHIELD_AGENT_ID</key>
        <string>$(hostname)-$(date +%s)</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
    echo "✅ LaunchAgent created. Load with: launchctl load ~/Library/LaunchAgents/com.mangotec.shield-agent.plist"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit $INSTALL_DIR/config.env with your API key"
echo "2. Start the agent (see above for your OS)"
echo "3. Monitor logs: tail -f $INSTALL_DIR/logs/guardian.log"
echo ""

