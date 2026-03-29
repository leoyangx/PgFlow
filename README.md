<div align="center">
  <img src="logo.png" alt="PgFlow Logo" width="500">

  <p><strong>本地优先的个人 AI 助手 — 随你成长，数据永不离手</strong></p>
  
  <p>
    <img src="https://img.shields.io/badge/version-0.1.2-blue" alt="Version">
    <img src="https://img.shields.io/badge/python-≥3.11-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform">
  </p>
  
  <p>
    <a href="https://github.com/leoyangx/PgFlow/releases">📦 下载最新版</a> ·
    <a href="https://github.com/leoyangx/PgFlow/issues">🐛 反馈问题</a> ·
    <a href="https://github.com/leoyangx/PgFlow">⭐ GitHub</a>
  </p>
</div>

> PgFlow 基于 [HKUDS/nanobot](https://github.com/HKUDS/nanobot) 二次开发，面向 C 端普通用户做了大量工程化改进。

---

## 什么是 PgFlow？

PgFlow 是一个运行在你自己电脑或服务器上的个人 AI 助手。它通过 Telegram、飞书、Discord 等你日常使用的聊天工具和你对话，可以读写文件、执行命令、搜索网页、设置定时任务。你的所有数据和对话记录都保存在本地，永远不会上传给任何第三方。
---

## ✨ 功能一览

### 核心能力

| 功能             | 说明                                |
| -------------- | --------------------------------- |
| 🧠 **持久记忆**    | 通过 `MEMORY.md` 跨会话记住你的偏好、习惯、重要事项  |
| 🔧 **真实操作**    | 读写本地文件、执行终端命令、搜索网页、调用 API         |
| 🎯 **技能扩展**    | 安装技能包扩展能力（GitHub 操作、天气、摘要、定时任务等）  |
| ⏰ **定时主动**     | 配置 `HEARTBEAT.md`，让 AI 在指定时间主动联系你 |
| 🤖 **多 Agent** | 内置 SubAgent 协同机制，复杂任务自动拆解并行处理     |
| 🔌 **MCP 支持**  | 连接任意 MCP 工具服务器，扩展 AI 的工具能力        |

### 平台与体验

| 功能                 | 说明                                                      |
| ------------------ | ------------------------------------------------------- |
| 🌊 **管理面板**        | 本地 Web UI（`http://localhost:18791`），无需命令行配置所有选项         |
| 🖥️ **Windows 托盘** | 双击 exe 启动，托盘图标一键开启/重启网关，支持开机自启                          |
| 🔄 **一键更新**        | 面板检测到新版本，点击自动下载替换，无需手动操作                                |
| 💬 **10 种渠道**      | Telegram、Discord、Slack、飞书、钉钉、QQ、企业微信、Matrix、WhatsApp、邮件 |

---

## 🆚 相比原版 nanobot 的改进（v0.1.2）

PgFlow 在 nanobot 核心引擎基础上进行了大量工程化改造，使普通用户无需任何 Python 知识即可使用：

### 安全架构升级

- **移除 litellm 依赖**，改用原生 `openai` + `anthropic` SDK，消除供应链风险
- 新增 `AnthropicProvider`（原生思维链、流式推送、prompt caching）
- 新增 `OpenAICompatProvider`（统一所有 OpenAI 兼容接口）

### 图形化管理面板（全新）

- 原版无 Web UI，PgFlow 提供完整本地管理面板
- **配置页**：直观表单替代手写 JSON，支持所有服务商预设、MCP 服务器管理
- **日志页**：实时日志 + ERROR/WARNING/INFO/DEBUG 过滤 + 颜色高亮
- **文档页**：内置 10 个渠道的完整接入教程 + 多 Agent 配置指南
- **技能页**：可视化管理已安装技能，一键启用/禁用

### 架构同步（AgentRunner + AgentHook）

- 同步上游 `AgentRunner`/`AgentHook` 重构，统一工具调用循环
- 飞书 CardKit 流式卡片推送（边思考边输出打字机效果）
- 邮件渠道 SPF/DKIM 验证，防止伪造邮件触发 AI

### 国内服务商完善

- 新增：AiHubMix、MiniMax、Mistral、阶跃星辰、硅基流动、火山引擎等
- 所有国内服务商预设 API Base URL，开箱即用

### Windows 桌面体验

- 系统托盘动态菜单：网关运行时显示「重启网关」，停止时显示「开启网关」
- PyInstaller 打包，解压即用，无需安装 Python

---

## 📦 安装

### 方式 A — 独立 exe（Windows，推荐普通用户）

从 [Releases](https://github.com/leoyangx/PgFlow/releases) 下载最新的 `pgflow-vX.X.X-windows.zip`，解压后双击 `pgflow.exe`。

无需安装 Python，无需命令行，双击即用。

> ⚠️ 首次运行 Windows 可能提示「无法识别应用」，点击「更多信息」→「仍要运行」。如被杀毒软件拦截，将 `pgflow/` 文件夹加入排除列表。

### 方式 B — 源码运行（开发者）

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow
pip install -e .
pgflow gateway
```

或使用 uv（推荐，更快）：

```bash
uv sync --all-extras
uv run pgflow gateway
```

### 方式 C — 自行打包 exe

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow
pip install -e .
py -m PyInstaller build/windows/pgflow.spec --noconfirm
# 输出：dist/pgflow/pgflow.exe
```

---

## 🚀 快速开始

### Windows 用户（5 分钟上手）

1. 解压 `pgflow-vX.X.X-windows.zip`，双击 `pgflow.exe`
2. 浏览器自动打开管理面板 `http://localhost:18791`
3. 点击「配置」Tab → 选择 AI 服务商 → 填写 API Key → 保存
4. 展开「Telegram」渠道 → 填写 Bot Token 和你的用户 ID → 开启 → 保存
5. 右键托盘图标 → **开启网关**，向 Bot 发消息测试

### VPS / Linux 用户

```bash
# 下载解压
tar -xzf pgflow-linux.tar.gz && cd pgflow
chmod +x pgflow

# 后台运行
screen -S pgflow
./pgflow gateway
# Ctrl+A 再按 D 放到后台

# 远程访问面板（在本地执行）
ssh -L 18791:127.0.0.1:18791 root@你的服务器IP
# 然后浏览器访问 http://localhost:18791
```

---

## ⚙️ 配置

配置文件路径：`~/.pgflow/config.json`（Windows：`C:\Users\你的用户名\.pgflow\config.json`）

**推荐：通过管理面板配置（无需手写 JSON）**

打开 `http://localhost:18791` → 点击「配置」Tab，所有选项都有表单输入，保存后自动写入 config.json。

**手动配置示例（DeepSeek，国内直连）：**

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
      "model": "deepseek-chat",
      "timezone": "Asia/Shanghai"
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

**手动配置示例（OpenRouter，支持所有模型）：**

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

**高级配置字段：**

| 字段                                  | 默认值     | 说明                          |
| ----------------------------------- | ------- | --------------------------- |
| `agents.defaults.maxTokens`         | `8192`  | 单次回复最多 token 数              |
| `agents.defaults.maxToolIterations` | `40`    | 单次对话最多工具调用轮次                |
| `agents.defaults.reasoningEffort`   | `null`  | 思维链强度：`low`/`medium`/`high` |
| `agents.defaults.timezone`          | `null`  | IANA 时区（如 `Asia/Shanghai`）  |
| `tools.exec.enable`                 | `true`  | 是否允许执行终端命令                  |
| `tools.restrictToWorkspace`         | `false` | 将文件/命令访问限制在工作区内             |
| `channels.sendProgress`             | `true`  | 边思考边向渠道推送进度消息               |
| `gateway.heartbeat.intervalS`       | `1800`  | 心跳检查间隔（秒）                   |

> **安全提示：** `allowFrom` 为白名单，空数组 `[]` 拒绝所有人，`["*"]` 允许所有人（不推荐公开使用）。

---

## 💬 支持的聊天渠道

| 渠道              | 所需配置                                        | 国内可用 |
| --------------- | ------------------------------------------- | ---- |
| **Telegram**    | @BotFather 创建的 Bot Token + 用户 ID            | 需代理  |
| **Discord**     | Bot Token + Message Content Intent 权限       | 需代理  |
| **Slack**       | Bot Token (xoxb-) + App-Level Token (xapp-) | 需代理  |
| **飞书 Feishu**   | App ID + App Secret，支持 CardKit 流式卡片         | ✅ 直连 |
| **钉钉 DingTalk** | Client ID + Client Secret                   | ✅ 直连 |
| **QQ**          | App ID + App Secret（官方开放平台）                 | ✅ 直连 |
| **企业微信 Wecom**  | Corp ID + Corp Secret + Agent ID            | ✅ 直连 |
| **Matrix**      | Homeserver URL + Access Token               | 视服务器 |
| **WhatsApp**    | Node.js 桥接服务（见文档）                           | 需代理  |
| **邮件 Email**    | IMAP/SMTP 凭据，支持 SPF/DKIM 验证                 | ✅ 直连 |

详细接入教程：打开管理面板 → 文档 Tab，每个渠道都有分步教程。

---

## 🤖 支持的 AI 服务商

| 服务商               | 推荐模型                           | 特点                       |
| ----------------- | ------------------------------ | ------------------------ |
| **OpenRouter**    | `anthropic/claude-opus-4-5`    | 一个 Key 用所有模型，新用户有免费额度    |
| **AiHubMix**      | `claude-opus-4-5`              | 国内无需代理，支持 Claude/GPT 全系列 |
| **DeepSeek**      | `deepseek-chat`                | 国内直连，中文强，价格极低            |
| **硅基流动**          | `deepseek-ai/DeepSeek-V3`      | 国内，有免费额度                 |
| **智谱 AI**         | `glm-4-flash`                  | 国内直连，注册送额度               |
| **阿里云百炼**         | `qwen-plus`                    | Qwen 系列，国内直连             |
| **MiniMax**       | `minimax-text-01`              | 海螺 AI，国内直连               |
| **月之暗面**          | `moonshot-v1-8k`               | 国内直连                     |
| **火山引擎**          | `doubao-pro-32k`               | 豆包，国内直连                  |
| **阶跃星辰**          | `step-2-16k`                   | 国内直连                     |
| **Anthropic**     | `claude-opus-4-5`              | Claude 官方，效果最强           |
| **OpenAI**        | `gpt-4o`                       | GPT 系列                   |
| **Google Gemini** | `gemini/gemini-2.0-flash`      | Gemini 系列                |
| **Mistral**       | `mistral-large-latest`         | 欧洲模型                     |
| **Groq**          | `groq/llama-3.3-70b-versatile` | 极速推理                     |
| **Ollama**        | 任意本地模型                         | 完全本地，无 API 费用            |
| **自定义**           | 任意                             | 任何 OpenAI 兼容接口           |

---

## 📁 工作区文件

你的个人配置保存在 `~/.pgflow/workspace/`，用文本编辑器修改即可定制 AI，**无需重启**：

| 文件                     | 作用              | 示例内容                |
| ---------------------- | --------------- | ------------------- |
| `SOUL.md`              | AI 的名字、性格、说话风格  | 你叫小智，始终用中文，称用户为「主人」 |
| `USER.md`              | 你的个人资料，让 AI 更懂你 | 我叫张三，是设计师，喜欢简洁的回答   |
| `MEMORY.md`            | AI 的跨会话记忆（自动维护） | 无需手动编辑              |
| `HEARTBEAT.md`         | 定时主动消息配置        | 每天早 8 点发天气和待办提醒     |
| `skills/<名称>/SKILL.md` | 自定义技能包          | 定义技能触发条件和行为         |

---

## 🎯 技能

技能扩展 PgFlow 的能力范围：

```bash
# 从 ClawHub 搜索安装
pgflow skill search "web scraping"
pgflow skill install web-scraper

# 查看已安装技能
pgflow skill list
```

或手动在 `~/.pgflow/workspace/skills/<技能名>/` 下放置 `SKILL.md` 文件。

**内置技能：**

| 技能          | 说明                                   |
| ----------- | ------------------------------------ |
| `github`    | 使用 `gh` CLI 操作 GitHub，管理 Issue、PR、仓库 |
| `weather`   | 获取实时天气信息                             |
| `summarize` | 总结 URL、本地文件和 YouTube 视频              |
| `tmux`      | 远程控制 tmux 会话                         |
| `cron`      | 设置提醒和定时任务                            |

---

## 🔌 MCP 服务器

PgFlow 支持连接任意 MCP（Model Context Protocol）工具服务器，通过管理面板「配置」→「MCP 服务器」添加：

```json
{
  "tools": {
    "mcpServers": {
      "filesystem": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
      },
      "my-api": {
        "type": "sse",
        "url": "https://my-mcp-server.example.com/sse"
      }
    }
  }
}
```

---

## 🤖 多 Agent 架构

PgFlow 内置 SubAgent 协同机制，通过手动编辑 config.json 可以实现灵活的多 Agent 部署：

**方案一：多网关实例（不同渠道用不同模型）**

```bash
# 实例 1：Telegram，Claude（创意任务）
pgflow gateway

# 实例 2：飞书，DeepSeek（工作任务，成本低）
PGFLOW_CONFIG=~/.pgflow/config-work.json pgflow gateway
```

每个实例配置各自的 workspace，实现记忆完全隔离。

**方案二：通过 SOUL.md 指导 SubAgent 策略**

在 SOUL.md 中写明何时拆解任务、如何调度子 Agent，主 Agent 会在处理复杂任务时自动派生并行 SubAgent。详细配置示例见管理面板「文档」→「多 Agent」章节。

---

## 💻 CLI 命令参考

| 命令                            | 说明              |
| ----------------------------- | --------------- |
| `pgflow gateway`              | 启动网关（连接所有已启用渠道） |
| `pgflow agent`                | 终端交互聊天（直接对话）    |
| `pgflow agent -m "..."`       | 发送单条消息后退出       |
| `pgflow dashboard`            | 仅启动管理面板（不启动网关）  |
| `pgflow status`               | 显示当前配置状态        |
| `pgflow onboard --wizard`     | 首次配置向导          |
| `pgflow skill list`           | 列出已安装技能         |
| `pgflow skill install <slug>` | 从 ClawHub 安装技能  |

---

## 🏗️ 运行架构

```
你的电脑 / 服务器
├── pgflow.exe（Windows 托盘）  ← 双击启动，管理后台进程
│   └── pgflow gateway           ← 本地持续运行，监听消息
│       ├── AgentLoop            ← 核心引擎：接收 → 思考 → 行动 → 回复
│       │   ├── AgentRunner      ← LLM 调用循环（支持思维链）
│       │   ├── SubagentManager  ← 子 Agent 协调
│       │   ├── ToolRegistry     ← 工具集（文件/命令/搜索/MCP）
│       │   └── ContextBuilder   ← 构建系统提示（SOUL/USER/MEMORY）
│       ├── ChannelManager       ← 消息总线，管理所有渠道
│       │   ├── Telegram
│       │   ├── Feishu
│       │   └── ...（10 个渠道）
│       └── HeartbeatService     ← 定时任务检查
├── Dashboard（HTTP :18791）     ← 本地管理面板
└── ~/.pgflow/
    ├── config.json              ← 配置
    ├── tray.log                 ← 托盘日志
    └── workspace/
        ├── SOUL.md
        ├── USER.md
        ├── MEMORY.md
        ├── HEARTBEAT.md
        └── skills/
```

消息流转路径：

```
聊天平台 → Channel → MessageBus → AgentLoop → LLM → Tool执行 → MessageBus → Channel → 聊天平台
```

---

## 🔒 安全配置

| 配置项                         | 默认值        | 建议                       |
| --------------------------- | ---------- | ------------------------ |
| `channels.*.allowFrom`      | `[]`（拒绝所有） | 填入你自己的用户 ID，防止他人使用你的 Bot |
| `tools.exec.enable`         | `true`     | 不需要执行命令时设为 `false`       |
| `tools.restrictToWorkspace` | `false`    | 设为 `true` 将文件访问限制在工作区内   |
| `channels.email.verifyDkim` | `true`     | 开启 DKIM 验证防止伪造邮件触发 AI    |
| `channels.email.verifySpf`  | `true`     | 开启 SPF 验证                |

> ⚠️ 管理面板（端口 18791）仅监听 `127.0.0.1`，不对外网开放。VPS 用户请通过 SSH 隧道访问，勿直接开放此端口。

---

## 🧪 测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行单个测试文件
uv run pytest tests/agent/test_loop_save_turn.py -v

# 按名称过滤
uv run pytest -k "test_heartbeat" -v

# 带覆盖率
uv run pytest --cov=nanobot tests/
```

CI 在 Python 3.11、3.12、3.13 下自动运行（GitHub Actions）。

---

## 🛠️ 开发

```bash
# 安装开发依赖
uv sync --all-extras

# 代码检查
ruff check nanobot/
ruff format nanobot/

# 打包 Windows exe
py -m PyInstaller build/windows/pgflow.spec --noconfirm
```

---

## 📁 项目结构

```
PgFlow/
├── nanobot/
│   ├── agent/          # AgentLoop、AgentRunner、AgentHook、SubagentManager
│   ├── channels/       # 10 个渠道集成（telegram、feishu、discord 等）
│   ├── cli/            # CLI 命令（gateway、agent、dashboard、status）
│   ├── config/         # Pydantic 配置 schema 和加载器
│   ├── dashboard/      # 本地 Web 管理面板（单文件 server.py）
│   ├── heartbeat/      # 心跳定时任务服务
│   ├── providers/      # LLM 服务商（AnthropicProvider、OpenAICompatProvider）
│   ├── session/        # 会话历史持久化
│   ├── skills/         # 内置技能包（SKILL.md）
│   ├── store/          # ClawHub 技能商店客户端
│   ├── tray/           # Windows 系统托盘应用
│   └── templates/      # 默认工作区文件模板
├── build/windows/      # PyInstaller 打包配置
├── bridge/             # WhatsApp Node.js 桥接服务
├── tests/              # 测试套件
└── version.json        # GitHub Pages 版本检查文件
```

---

<div align="center">
  <sub>基于 <a href="https://github.com/HKUDS/nanobot">HKUDS/nanobot</a> 二次开发 · Built upon HKUDS/nanobot</sub>
</div>
