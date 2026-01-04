# Murkaverse Gatekeeper Bot

A Telegram lobby/gatekeeper bot for the Murkaverse community. Users complete a bilingual (EN/RU) verification in DM before joining the supergroup.

## Features

- **DM Lobby**: Bilingual welcome + rules + button-based captcha
- **Auto-Approval**: Verified users get auto-approved when requesting to join
- **Soft/Strict Modes**: Leave unverified pending (soft) or decline (strict)
- **Lockdown Mode**: Decline all join requests during emergencies
- **No Group Messages**: Bot never posts in the group — everything is DM
- **Admin Controls**: Simple commands to manage the bot

## Setup

### 1. Create the Bot with BotFather

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the **API token** (e.g., `123456789:ABCdef...`)
4. Configure bot settings:
   - `/setprivacy` → Disable (so bot can see messages if needed)
   - `/setjoingroups` → Enable

### 2. Configure Your Supergroup

1. Create or open your supergroup
2. Go to **Group Settings** → **Group Type** → Enable **Join Requests** (Approve New Members)
3. Create an **invite link with join requests**:
   - Go to **Invite Links** → **Create a New Link**
   - Enable "Approve New Members" toggle
   - Copy this link (e.g., `https://t.me/+abc123...`)
4. Add the bot as **admin** with these permissions:
   - ✅ Add new members (needed to approve/decline requests)
   - Other permissions can be disabled
5. Get the **Group Chat ID**:
   - Add [@userinfobot](https://t.me/userinfobot) to the group temporarily
   - It will show the chat ID (negative number like `-1001234567890`)
   - Remove the bot after getting the ID

### 3. Environment Variables

Create a `.env` file in the project root:

```bash
# Required
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
GROUP_CHAT_ID=-1001234567890
JOIN_REQUEST_INVITE_LINK=https://t.me/+abcdefghijk

# Optional (defaults shown)
VERIFY_TTL_SECONDS=300
COOLDOWN_SECONDS=600
MAX_ATTEMPTS=3
STRICT_MODE=false
LOCKDOWN=false
SQLITE_PATH=./data/gatekeeper.sqlite

# Admin user IDs (comma-separated)
ADMIN_IDS=123456789,987654321
```

To get your user ID, message [@userinfobot](https://t.me/userinfobot).

### 4. Install and Run

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python -m src.main
```

The bot uses **long polling** — no domain/webhook needed.

## Usage

### User Flow

1. User clicks deep link: `https://t.me/YOUR_BOT?start=join`
2. Bot shows rules in DM → user agrees
3. Bot shows captcha (pick an emoji) → user passes
4. Bot gives join-request invite link
5. User requests to join group → bot auto-approves

### Admin Commands (DM only)

| Command | Description |
|---------|-------------|
| `/lockdown on\|off` | Enable/disable lockdown (decline all requests) |
| `/mode soft\|strict` | Toggle verification mode |
| `/status` | Show current status and stats |
| `/adminhelp` | Show admin commands |

### Modes

- **Soft mode** (default): Unverified users left pending for manual approval
- **Strict mode**: Unverified users are declined with a message to verify first
- **Lockdown**: All join requests declined (emergency mode)

## Deployment on AWS Lightsail

1. Create a Lightsail instance (Ubuntu recommended)
2. SSH into the instance
3. Install Python 3.11+:
   ```bash
   sudo apt update && sudo apt install python3 python3-pip python3-venv
   ```
4. Clone/upload your project
5. Set up environment variables (use `.env` file or export them)
6. Run with a process manager:

   **Using systemd:**
   ```bash
   sudo nano /etc/systemd/system/gatekeeper.service
   ```
   
   ```ini
   [Unit]
   Description=Murkaverse Gatekeeper Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/Bot
   Environment=PATH=/home/ubuntu/Bot/venv/bin
   EnvironmentFile=/home/ubuntu/Bot/.env
   ExecStart=/home/ubuntu/Bot/venv/bin/python -m src.main
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```
   
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable gatekeeper
   sudo systemctl start gatekeeper
   sudo systemctl status gatekeeper
   ```

## Project Structure

```
Bot/
├── requirements.txt
├── README.md
├── data/                    # SQLite database (created automatically)
│   └── gatekeeper.sqlite
└── src/
    ├── __init__.py
    ├── main.py              # Entry point
    ├── config.py            # Environment config
    ├── db.py                # SQLite persistence
    ├── texts.py             # Bilingual message copy
    ├── keyboards.py         # Inline keyboards
    └── handlers/
        ├── __init__.py
        ├── start.py         # /start command
        ├── lobby.py         # Agreement & captcha flow
        ├── join_requests.py # Auto-approval logic
        └── admin.py         # Admin commands
```

## Troubleshooting

### Bot doesn't receive join requests
- Ensure bot is admin with "Add new members" permission
- Check that join requests are enabled on the group
- Verify `GROUP_CHAT_ID` is correct (should be negative)

### Bot can't DM users
- Bots can only DM users who have started the bot first
- Users must click the bot link before requesting to join

### Auto-approval not working
- Check that `VERIFY_TTL_SECONDS` hasn't passed (default 5 minutes)
- User must complete captcha before requesting to join
- Check logs for any API errors

## License

MIT License - Murkaverse 2024

