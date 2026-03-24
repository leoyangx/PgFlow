<div align="center">
  <h1>🌊 PgFlow</h1>
  <p><strong>Your personal AI that grows with you</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform">
  </p>
  <p>
    <a href="https://github.com/leoyangx/PgFlow">GitHub</a> ·
    <a href="https://github.com/leoyangx/PgFlow/issues">Issues</a> ·
    <a href="https://github.com/leoyangx/PgFlow/releases">Releases</a>
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

### Option A — Standalone .exe (Windows, recommended for end users)

No Python required. Download the latest release or build it yourself:

```bat
:: 1. Clone the repo
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow

:: 2. Install Python dependencies (requires Python 3.11+)
pip install -e .

:: 3. Build the .exe
build\windows\build.bat
```

The output is `dist\pgflow\pgflow.exe`. Copy the entire `dist\pgflow\` folder anywhere you like.

> **Note:** Double-clicking `pgflow.exe` will flash and close — this is normal for a CLI tool.
> Always run it from a terminal (Command Prompt or PowerShell).

### Option B — From source (developers)

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow
pip install -e .
```

Then use the `pgflow` command directly.

## 🚀 Quick Start

### Step 1 — Initialize

```bash
pgflow onboard --wizard
```

The wizard will guide you through:
- Choosing a workspace folder (`~/.pgflow/workspace/` by default)
- Setting your LLM provider and API key
- Connecting a chat channel (e.g. Telegram)

### Step 2 — Start the gateway

```bash
pgflow gateway
```

The gateway connects all your configured channels. Keep this running in the background.

### Step 3 — Enable autostart (recommended)

```bash
pgflow service install
```

PgFlow will start automatically every time you log in — no need to run it manually again.

- **Windows:** Task Scheduler (`ONLOGON`, highest privilege)
- **macOS:** launchd (`~/Library/LaunchAgents/`)
- **Linux:** systemd user service

To disable autostart:

```bash
pgflow service uninstall
```

### Step 4 — Open the dashboard

```bash
pgflow dashboard
```

Opens `http://localhost:18791` in your browser — a local management UI showing status, installed skills, and config.

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

**Set your API key** (OpenRouter recommended — works with Claude, GPT-4, Gemini, etc.):

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

1. Message [@BotFather](https://t.me/BotFather) on Telegram → create a bot → copy the token
2. Get your user ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `~/.pgflow/config.json`:

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

> **Security:** `allowFrom` is a whitelist. An empty list `[]` denies everyone. Set `["*"]` to allow all users (not recommended for public bots).

## 💻 CLI Reference

| Command | Description |
|---------|-------------|
| `pgflow onboard --wizard` | First-time setup wizard |
| `pgflow agent` | Interactive chat in terminal |
| `pgflow agent -m "..."` | Send a single message |
| `pgflow gateway` | Start the gateway (connects all channels) |
| `pgflow dashboard` | Open local management dashboard at localhost:18791 |
| `pgflow status` | Show current config and connection status |
| `pgflow service install` | Enable autostart on login |
| `pgflow service uninstall` | Disable autostart |
| `pgflow service status` | Check autostart service status |
| `pgflow skill list` | List installed skills |
| `pgflow skill search <query>` | Search ClawHub for skills |
| `pgflow skill install <slug>` | Install a skill from ClawHub |
| `pgflow build` | Package as standalone executable |

## 🎯 Skills

Skills extend PgFlow's capabilities. Install from ClawHub (requires Node.js):

```bash
pgflow skill search "web scraping"
pgflow skill install web-scraper
pgflow skill list
```

Or place a `SKILL.md` file manually in `~/.pgflow/workspace/skills/<skill-name>/`.

**Built-in skills:**

| Skill | Description |
|-------|-------------|
| `github` | Interact with GitHub using the `gh` CLI |
| `weather` | Get weather info |
| `summarize` | Summarize URLs, files, and YouTube videos |
| `tmux` | Remote-control tmux sessions |
| `cron` | Schedule reminders and recurring tasks |

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
PgFlow/
├── nanobot/        # Core Python package
│   ├── agent/      # Agent logic and LLM loop
│   ├── channels/   # Chat channel integrations
│   ├── cli/        # CLI commands
│   ├── config/     # Configuration loading
│   ├── dashboard/  # Local web dashboard
│   ├── service/    # Autostart service management
│   ├── skills/     # Built-in skill packs
│   ├── store/      # Skill store client
│   └── templates/  # Default workspace files
├── build/          # Packaging scripts (.exe, .dmg)
├── bridge/         # WhatsApp bridge (Node.js)
└── tests/          # Test suite
```

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and guidelines.

Issues and PRs welcome: [https://github.com/leoyangx/PgFlow/issues](https://github.com/leoyangx/PgFlow/issues)

## 📄 License

MIT — see [LICENSE](./LICENSE)
