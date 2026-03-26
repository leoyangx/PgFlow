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
> PgFlow 基于 [HKUDS/nanobot](https://github.com/HKUDS/nanobot) 二次开发，在此对原作者及所有贡献者表示衷心感谢。
> PgFlow is built upon [HKUDS/nanobot](https://github.com/HKUDS/nanobot). We sincerely thank the original authors and contributors.

---

PgFlow 是一个本地优先的个人 AI 助手，运行在你自己的电脑或服务器上，随着每次对话变得更聪明。通过 Telegram、Discord 等聊天应用控制它，你的数据永远不会离开你的机器。

## ✨ 核心功能

- 🧠 **随你成长** — 通过 `MEMORY.md` 跨会话记住你的偏好、习惯和上下文
- 🏠 **本地优先** — 完全运行在你的电脑上，文件、数据、隐私全掌握在你手中
- 💬 **随处聊天** — 支持 Telegram、Discord、Slack、飞书、钉钉、WhatsApp、邮件、QQ、企业微信、Matrix 等
- 🔧 **真实操作** — 读写文件、执行命令、搜索网页、管理日程
- 🎯 **技能扩展** — 从 ClawHub 安装技能包，或自己编写
- 🌊 **管理面板** — 本地 Web UI，访问 `http://localhost:18791` 管理状态、配置和日志
- 🖥️ **系统托盘** — 双击 exe 即可启动，托盘图标管理网关、开机自启
- 🔄 **一键更新** — 面板检测到新版本后，点击即可自动下载、替换、完成升级

---

## 🆚 相比原版 nanobot 的改进

PgFlow 在 nanobot 核心引擎的基础上，面向 C 端普通用户做了大量工程化改进：

### 🖥️ 图形化管理面板（全新）
- 原版无 Web UI，PgFlow 新增完整的本地管理面板（`http://localhost:18791`）
- **状态页**：实时显示网关运行状态、已启用渠道、工作区文件、版本信息
- **配置页**：替代原版的手写 JSON，提供直观的表单配置，支持所有 AI 服务商预设（OpenRouter、DeepSeek、硅基流动、阶跃星辰等 12 家），自动填入 API Base URL 和推荐模型名
- **技能页**：可视化管理已安装技能，一键启用/禁用
- **日志页**：实时查看运行日志，支持自动刷新和跳到底部
- **文档页**：内置 Windows / macOS / Linux / VPS 部署教程

### 🔄 一键自动更新
- 面板检测到新版本后，显示进度条，一键完成下载 → 解压 → 替换，无需手动操作

### 🪟 Windows 桌面应用体验
- 系统托盘图标，双击 `pgflow.exe` 自动启动网关并打开面板
- 支持开机自启（注册表方式，托盘一键配置）
- PyInstaller 打包，解压即用，无需安装 Python
- 图标、托盘状态动态反映网关运行状态

### ⚙️ 服务商配置完善
- 新增支持：硅基流动、智谱 AI、阿里云百炼、月之暗面、火山引擎豆包、阶跃星辰等国内服务商
- 所有服务商预设 API Base URL，国内用户无需手动填写接口地址
- 修复了 DeepSeek 等需要 apiBase 的服务商配置字段丢失问题

### 📡 渠道完善
- 从原版同步并整合了消息发送重试机制（指数退避，最多 3 次）
- 从原版同步了 Telegram streaming 消息边界修复
- 面板支持 10 个渠道的可视化配置

---

## 📦 安装

### 方式 A — 独立 exe（Windows，推荐普通用户）

直接从 [Releases](https://github.com/leoyangx/PgFlow/releases) 下载最新的 `pgflow-vX.X.X-windows.zip`，解压后双击 `pgflow.exe` 即可。

无需安装 Python，无需命令行。

### 方式 B — 源码运行（开发者）

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow
pip install -e .
pgflow gateway
```

### 方式 C — 自行打包 exe

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow
pip install -e .
py -m PyInstaller build/windows/pgflow.spec --noconfirm
# 输出在 dist/pgflow/pgflow.exe
```

---

## 🚀 快速开始

### Windows 用户

1. 解压 `pgflow-vX.X.X-windows.zip`，双击 `pgflow.exe`
2. 浏览器自动打开管理面板，点击「配置」Tab
3. 选择 AI 服务商，填写 API Key，保存
4. 展开 Telegram 渠道，填写 Bot Token 和你的用户 ID，启用，保存
5. 右键托盘图标 → **重启服务**，向 Bot 发消息测试

### VPS / Linux 用户

```bash
# 1. 下载并解压（以 Linux 包为例）
tar -xzf pgflow-linux.tar.gz
cd pgflow
chmod +x pgflow

# 2. 启动网关（保持终端开启）
./pgflow gateway

# 3. 浏览器访问管理面板（SSH 隧道方式）
# 在本地执行：ssh -L 18791:127.0.0.1:18791 root@你的服务器IP
# 然后访问：http://localhost:18791

# 4. 后台持久运行
screen -S pgflow
./pgflow gateway
# 按 Ctrl+A 再按 D 放到后台
```

---

## 💬 支持的聊天渠道

| 渠道 | 所需配置 |
|------|----------|
| **Telegram** | @BotFather 创建的 Bot Token |
| **Discord** | Bot Token + Message Content 权限 |
| **Slack** | Bot Token + App-Level Token |
| **飞书 Feishu** | App ID + App Secret |
| **钉钉 DingTalk** | Client ID + Client Secret |
| **QQ** | App ID + App Secret |
| **企业微信 Wecom** | Corp ID + Corp Secret + Agent ID |
| **Matrix** | Homeserver URL + Access Token |
| **WhatsApp** | Node.js + 桥接服务 |
| **邮件 Email** | IMAP/SMTP 凭据 |

---

## ⚙️ 配置

配置文件：`~/.pgflow/config.json`

**推荐配置（DeepSeek，国内直连）：**

```json
{
  "providers": {
    "deepseek": {
      "apiKey": "sk-xxx",
      "apiBase": "https://api.deepseek.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "deepseek-chat"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}
```

**推荐配置（OpenRouter，支持所有模型）：**

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

> **安全提示：** `allowFrom` 是白名单。空列表 `[]` 拒绝所有人，`["*"]` 允许所有人（不推荐用于公开 Bot）。

---

## 🤖 支持的 AI 服务商

| 服务商 | 推荐模型 | 适合人群 |
|--------|----------|----------|
| OpenRouter | `anthropic/claude-opus-4-5` | 想用所有模型 |
| DeepSeek | `deepseek-chat` | 国内用户首选 |
| 硅基流动 SiliconFlow | `deepseek-ai/DeepSeek-V3` | 国内，有免费额度 |
| 智谱 AI | `glm-4-flash` | 国内直连 |
| 阿里云百炼 DashScope | `qwen-plus` | 国内直连 |
| 月之暗面 Moonshot | `moonshot-v1-8k` | 国内直连 |
| 火山引擎（豆包）| `doubao-pro-32k` | 国内直连 |
| 阶跃星辰 Step Fun | `step-2-16k` | 国内直连 |
| Anthropic | `claude-opus-4-5` | Claude 官方 |
| OpenAI | `gpt-4o` | GPT 系列 |
| Google Gemini | `gemini/gemini-2.0-flash` | Gemini 系列 |
| Groq | `groq/llama-3.3-70b-versatile` | 高速推理 |
| 自定义 | 任意 | OpenAI 兼容接口 |

---

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
| `pgflow skill install <slug>` | 安装技能 |

---

## 🎯 技能

技能扩展 PgFlow 的能力，可从 ClawHub 安装：

```bash
pgflow skill search "web scraping"
pgflow skill install web-scraper
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

---

## 🏗️ 工作原理

```
你的电脑 / 服务器
├── pgflow.exe（托盘）     ← 双击启动，管理后台进程（Windows）
│   └── pgflow gateway    ← 本地运行，持续监听
│       ├── Agent (LLM)   ← 调用 AI 服务商，思考和行动
│       ├── Tools         ← 读写文件、执行命令、搜索网页
│       └── Channels      ← 连接 Telegram / Discord 等渠道
├── Dashboard (HTTP)      ← http://localhost:18791 管理面板
└── ~/.pgflow/
    ├── config.json       ← 你的配置
    └── workspace/
        ├── SOUL.md       ← AI 人格设定
        ├── USER.md       ← 你的个人资料
        ├── MEMORY.md     ← AI 的记忆（自动维护）
        ├── HEARTBEAT.md  ← 定时主动消息
        └── skills/       ← 已安装的技能包
```

---

## 📁 项目结构

```
PgFlow/
├── nanobot/            # 核心 Python 包
│   ├── agent/          # Agent 逻辑和 LLM 循环
│   ├── channels/       # 聊天渠道集成（Telegram、Discord 等）
│   ├── cli/            # CLI 命令
│   ├── config/         # 配置加载和 schema
│   ├── dashboard/      # 本地 Web 管理面板（单文件 server.py）
│   ├── providers/      # LLM 服务商接入（LiteLLM）
│   ├── service/        # 自启动服务管理
│   ├── skills/         # 内置技能包
│   ├── store/          # 技能商店客户端
│   ├── tray/           # Windows 系统托盘应用
│   └── templates/      # 默认工作区文件模板
├── build/
│   └── windows/        # PyInstaller 打包配置
├── bridge/             # WhatsApp Node.js 桥接服务
├── tests/              # 测试套件
├── version.json        # GitHub Pages 版本检查文件
└── MAINTAINER_GUIDE.md # 维护操作手册
```

---

## 🔒 安全

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `tools.restrictToWorkspace` | `false` | 将文件/命令访问限制在工作区目录内 |
| `tools.exec.enable` | `true` | 设为 `false` 可禁用命令执行 |
| `channels.*.allowFrom` | `[]`（拒绝所有） | 允许交互的用户 ID 白名单 |

> ⚠️ 管理面板（端口 18791）仅监听本地地址，请勿直接开放到公网。VPS 用户请通过 SSH 隧道访问。

---

## 🤝 贡献

欢迎提交 Issue 和 PR：[https://github.com/leoyangx/PgFlow/issues](https://github.com/leoyangx/PgFlow/issues)


## 📄 许可证

MIT — 详见 [LICENSE](./LICENSE)

---

<div align="center">
  <sub>基于 <a href="https://github.com/HKUDS/nanobot">HKUDS/nanobot</a> 二次开发 · Built upon HKUDS/nanobot</sub>
</div>
