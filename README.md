<div align="center">
  <h1>🌊 PgFlow</h1>
  <p><strong>Your personal AI that grows with you</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform">
  </p>
</div>

PgFlow is a local-first personal AI assistant that lives on your own computer and grows smarter with every conversation. Control it from Telegram, Discord, or any chat app — your data never leaves your machine.

## ✨ Key Features

- 🧠 **Grows with you** — Remembers your preferences, habits, and context across sessions via `MEMORY.md`
- 🏠 **Local-first** — Runs entirely on your computer. Your files, your data, your privacy
- 💬 **Chat from anywhere** — Telegram, Discord, Slack, WeChat, Feishu, DingTalk, WhatsApp, Email, QQ, and more
- 🔧 **Real actions** — Reads/writes files, runs shell commands, searches the web, manages schedules
- 🎯 **Skills** — Extend with skill packs from ClawHub or write your own
- 🌊 **Dashboard** — Local web UI at `http://localhost:18791` to manage status, skills, and config

## 📦 Install

**Windows (recommended for end users):**

Build the standalone `.exe` installer:
```bat
build\windows\build.bat
```
Then run `dist\pgflow\pgflow.exe` — no Python required.

**Developers (from source):**
```bash
git clone <your-repo>
cd nanobot
pip install -e .
```

## 🚀 Quick Start

**1. Initialize**
```bash
pgflow onboard --wizard
```
Choose your workspace, configure your LLM provider, and connect a chat channel.

**2. Start**
```bash
pgflow gateway
```

**3. Enable autostart (recommended)**
```bash
pgflow service install
```
PgFlow will start automatically on login — no need to run it manually ever again.

**4. Open dashboard**
```bash
pgflow dashboard
```

## 💬 Supported Chat Channels

| Channel | What you need |
|---------|---------------|
| **Telegram** | Bot token from @BotFather |
| **Discord** | Bot token + Message Content intent |
| **Slack** | Bot token + App-Level token |
| **WhatsApp** | Node.js + QR code scan |
| **WeChat (Weixin)** | QR code scan |
| **Feishu** | App ID + App Secret |
| **DingTalk** | App Key + App Secret |
| **Matrix** | Homeserver URL + Access token |
| **Email** | IMAP/SMTP credentials |
| **QQ** | App ID + App Secret |
| **Wecom** | Bot ID + Bot Secret |

## ⚙️ Configuration

Config file: `~/.pgflow/config.json`

**Set your API key** (OpenRouter recommended):
```json
{
  "providers": {
    "openrouter": {
      "apiKey": "sk-or-v1-xxx"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5"
    }
  }
}
```

**Connect Telegram:**
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

## 💻 CLI Reference

| Command | Description |
|---------|-------------|
| `pgflow onboard --wizard` | First-time setup wizard |
| `pgflow agent` | Interactive chat in terminal |
| `pgflow agent -m "..."` | Send a single message |
| `pgflow gateway` | Start the gateway (connects all channels) |
| `pgflow dashboard` | Open local management dashboard |
| `pgflow service install` | Enable autostart on login |
| `pgflow service uninstall` | Disable autostart |
| `pgflow service status` | Check service status |
| `pgflow skill list` | List installed skills |
| `pgflow skill search <query>` | Search ClawHub for skills |
| `pgflow skill install <slug>` | Install a skill |
| `pgflow status` | Show current config status |
| `pgflow build` | Package as standalone executable |

## 🎯 Skills

Skills extend PgFlow's capabilities. Install from ClawHub (requires Node.js):

```bash
pgflow skill search "web scraping"
pgflow skill install web-scraper
pgflow skill list
```

Or place a `SKILL.md` file in `~/.pgflow/workspace/skills/<skill-name>/` manually.

## 🔒 Security

| Option | Default | Description |
|--------|---------|-------------|
| `tools.restrictToWorkspace` | `false` | Restrict all file/shell access to workspace directory |
| `tools.exec.enable` | `true` | Set `false` to disable shell command execution |
| `channels.*.allowFrom` | `[]` (deny all) | Whitelist of user IDs allowed to interact |

## 🏗️ How It Works

```
Your Computer
├── pgflow gateway          ← runs locally, always on
│   ├── Agent (LLM)         ← thinks and acts
│   ├── Tools               ← reads files, runs commands
│   └── Channels            ← connects to Telegram etc.
└── ~/.pgflow/
    ├── config.json         ← your settings
    └── workspace/
        ├── SOUL.md         ← AI personality
        ├── USER.md         ← your profile
        ├── MEMORY.md       ← what the AI remembers
        ├── HEARTBEAT.md    ← periodic tasks
        └── skills/         ← installed skill packs
```

## 📁 Project Structure

```
nanobot/
├── agent/          # Core agent logic
├── channels/       # Chat channel integrations
├── cli/            # CLI commands
├── config/         # Configuration loading
├── dashboard/      # Local web dashboard
├── service/        # Autostart service management
├── skills/         # Built-in skill packs
├── store/          # Skill store client
├── templates/      # Default workspace files
└── build/          # Packaging scripts
```

## 📄 License

MIT
