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

> **致谢 / Acknowledgement**
> PgFlow 基于 [nanobot-ai/nanobot](https://github.com/nanobot-ai/nanobot) 二次开发，在此对原作者及所有贡献者表示衷心感谢。
> PgFlow is built upon [nanobot-ai/nanobot](https://github.com/nanobot-ai/nanobot). We sincerely thank the original authors and contributors.

---

PgFlow 是一个本地优先的个人 AI 助手，运行在你自己的电脑上，随着每次对话变得更聪明。通过 Telegram、Discord 等聊天应用控制它，你的数据永远不会离开你的机器。

## ✨ 核心功能

- 🧠 **随你成长** — 通过 `MEMORY.md` 跨会话记住你的偏好、习惯和上下文
- 🏠 **本地优先** — 完全运行在你的电脑上，文件、数据、隐私全掌握在你手中
- 💬 **随处聊天** — 支持 Telegram、Discord、Slack、微信、飞书、钉钉、WhatsApp、邮件、QQ 等
- 🔧 **真实操作** — 读写文件、执行命令、搜索网页、管理日程
- 🎯 **技能扩展** — 从 ClawHub 安装技能包，或自己编写
- 🌊 **管理面板** — 本地 Web UI，访问 `http://localhost:18791` 管理状态、技能和配置
- 🖥️ **系统托盘** — 双击 exe 即可启动，托盘图标管理网关、开机自启

## 📦 安装

### 方式 A — 独立 .exe（Windows，推荐普通用户）

无需安装 Python，下载最新 Release 或自行构建：

```bat
:: 1. 克隆仓库
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow

:: 2. 安装依赖（需要 Python 3.11+）
pip install -e .

:: 3. 打包 exe
build\windows\build.bat
```

输出目录：`dist\pgflow\pgflow.exe`，将整个 `dist\pgflow\` 文件夹复制到任意位置即可使用。

> **提示：** 双击 `pgflow.exe` 会自动启动系统托盘，在后台运行网关并打开管理面板。

### 方式 B — 源码运行（开发者）

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow
pip install -e .
```

然后直接使用 `pgflow` 命令。

## 🚀 快速开始

### 第一步 — 初始化配置

双击 `pgflow.exe` 启动托盘，面板会引导你运行：

```bash
"path\to\pgflow.exe" onboard --wizard
```

向导将引导你完成：
- 选择工作区目录（默认 `~/.pgflow/workspace/`）
- 配置 LLM 服务商和 API Key
- 连接聊天渠道（如 Telegram）

### 第二步 — 启动网关

双击 `pgflow.exe`，托盘自动在后台启动网关。

或手动运行：

```bash
pgflow gateway
```

### 第三步 — 开机自启

右键托盘图标 → **开机自启**（打勾即启用），无需任何命令行操作。

### 第四步 — 打开管理面板

右键托盘图标 → **打开管理面板**，或访问：

```
http://localhost:18791
```

## 💬 支持的聊天渠道

| 渠道 | 所需配置 |
|------|----------|
| **Telegram** | @BotFather 创建的 Bot Token |
| **Discord** | Bot Token + Message Content 权限 |
| **Slack** | Bot Token + App-Level Token |
| **WhatsApp** | Node.js + 扫码登录 |
| **微信 (Weixin)** | 扫码登录 |
| **飞书 (Feishu)** | App ID + App Secret |
| **钉钉 (DingTalk)** | App Key + App Secret |
| **Matrix** | Homeserver URL + Access Token |
| **邮件 (Email)** | IMAP/SMTP 凭据 |
| **QQ** | App ID + App Secret |
| **企业微信 (Wecom)** | Bot ID + Bot Secret |

## ⚙️ 配置

配置文件：`~/.pgflow/config.json`

**设置 API Key**（推荐 OpenRouter，兼容 Claude、GPT-4、Gemini 等）：

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

**连接 Telegram：**

1. 在 Telegram 向 [@BotFather](https://t.me/BotFather) 发送消息创建 Bot，复制 Token
2. 通过 [@userinfobot](https://t.me/userinfobot) 获取你的用户 ID
3. 添加到配置文件：

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

> **安全提示：** `allowFrom` 是白名单。空列表 `[]` 拒绝所有人，`["*"]` 允许所有人（不推荐用于公开 Bot）。

## 💻 CLI 命令参考

| 命令 | 说明 |
|------|------|
| `pgflow onboard --wizard` | 首次配置向导 |
| `pgflow agent` | 终端交互聊天 |
| `pgflow agent -m "..."` | 发送单条消息 |
| `pgflow gateway` | 启动网关（连接所有渠道） |
| `pgflow dashboard` | 打开本地管理面板 |
| `pgflow status` | 显示当前配置和连接状态 |
| `pgflow skill list` | 列出已安装技能 |
| `pgflow skill search <query>` | 搜索技能 |
| `pgflow skill install <slug>` | 安装技能 |

## 🎯 技能

技能扩展 PgFlow 的能力，可从 ClawHub 安装（需要 Node.js）：

```bash
pgflow skill search "web scraping"
pgflow skill install web-scraper
pgflow skill list
```

或手动在 `~/.pgflow/workspace/skills/<skill-name>/` 下放置 `SKILL.md` 文件。

**内置技能：**

| 技能 | 说明 |
|------|------|
| `github` | 使用 `gh` CLI 操作 GitHub |
| `weather` | 获取天气信息 |
| `summarize` | 总结 URL、文件和 YouTube 视频 |
| `tmux` | 远程控制 tmux 会话 |
| `cron` | 设置提醒和定时任务 |

## 🔒 安全

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `tools.restrictToWorkspace` | `false` | 将文件/命令访问限制在工作区目录内 |
| `tools.exec.enable` | `true` | 设为 `false` 可禁用命令执行 |
| `channels.*.allowFrom` | `[]`（拒绝所有） | 允许交互的用户 ID 白名单 |

## 🏗️ 工作原理

```
你的电脑
├── pgflow.exe（托盘）     ← 双击启动，管理后台进程
│   └── pgflow gateway    ← 本地运行，持续监听
│       ├── Agent (LLM)   ← 思考和行动
│       ├── Tools         ← 读文件、执行命令
│       └── Channels      ← 连接 Telegram 等渠道
└── ~/.pgflow/
    ├── config.json       ← 你的配置
    └── workspace/
        ├── SOUL.md       ← AI 人格设定
        ├── USER.md       ← 你的个人资料
        ├── MEMORY.md     ← AI 的记忆
        ├── HEARTBEAT.md  ← 定时任务
        └── skills/       ← 已安装的技能包
```

## 📁 项目结构

```
PgFlow/
├── nanobot/        # 核心 Python 包
│   ├── agent/      # Agent 逻辑和 LLM 循环
│   ├── channels/   # 聊天渠道集成
│   ├── cli/        # CLI 命令
│   ├── config/     # 配置加载
│   ├── dashboard/  # 本地 Web 面板
│   ├── service/    # 自启动服务管理
│   ├── skills/     # 内置技能包
│   ├── store/      # 技能商店客户端
│   ├── tray/       # 系统托盘应用
│   └── templates/  # 默认工作区文件
├── build/          # 打包脚本（.exe）
├── bridge/         # WhatsApp 桥接（Node.js）
└── tests/          # 测试套件
```

## 🤝 贡献

欢迎提交 Issue 和 PR：[https://github.com/leoyangx/PgFlow/issues](https://github.com/leoyangx/PgFlow/issues)

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 📄 许可证

MIT — 详见 [LICENSE](./LICENSE)

---

<div align="center">
  <sub>基于 <a href="https://github.com/nanobot-ai/nanobot">nanobot-ai/nanobot</a> 二次开发 · Built upon nanobot-ai/nanobot</sub>
</div>
