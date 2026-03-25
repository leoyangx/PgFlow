# 🌊 PgFlow 用户使用教程

> 本教程面向普通用户，无需编程基础，按步骤操作即可完成安装和使用。

---

## 目录

1. [PgFlow 是什么](#一pgflow-是什么)
2. [安装前准备](#二安装前准备)
3. [下载与安装](#三下载与安装)
4. [第一次启动配置](#四第一次启动配置)
5. [连接 Telegram 开始聊天](#五连接-telegram-开始聊天)
6. [设置开机自动启动](#六设置开机自动启动)
7. [管理面板使用](#七管理面板使用)
8. [常见问题](#八常见问题)
9. [与原版对比](#九与原版对比)

---

## 一、PgFlow 是什么

PgFlow 是一个运行在你自己电脑上的 AI 助手。

**核心特点：**
- 数据完全本地存储，不上传到任何服务器
- 通过 Telegram、微信、QQ 等你已有的 App 与 AI 对话
- AI 会记住你的习惯和偏好，越用越懂你
- 可以帮你管理文件、搜索网络、设置提醒、执行任务

**适合人群：** 希望拥有私人 AI 助手、重视数据隐私的用户。

---

## 二、安装前准备

### 必须有的东西

| 项目 | 说明 |
|------|------|
| Windows 电脑 | Windows 10 或 Windows 11，64位 |
| 网络连接 | 用于连接 AI 服务和 Telegram |
| AI 服务 API Key | 推荐使用 OpenRouter（见下方说明） |
| Telegram 账号 | 用于和 AI 对话（也可选其他渠道） |

### 获取 API Key（以 OpenRouter 为例）

OpenRouter 支持 Claude、GPT-4、Gemini 等多种模型，注册即可使用。

1. 打开 [https://openrouter.ai](https://openrouter.ai)
2. 注册账号并登录
3. 点击右上角头像 → **API Keys** → **Create Key**
4. 复制生成的 Key（格式类似 `sk-or-v1-xxx...`），妥善保存

---

## 三、下载与安装

### 方式一：直接使用打包好的 .exe（推荐）

从发布页下载最新版本的压缩包：

👉 [https://github.com/leoyangx/PgFlow/releases](https://github.com/leoyangx/PgFlow/releases)

1. 下载 `pgflow-windows.zip`（或类似名称）
2. 解压到任意位置，例如 `C:\PgFlow\`
3. 文件夹内有 `pgflow.exe` 即为主程序

> **注意：** 直接双击 `pgflow.exe` 会闪退，这是正常现象。
> CLI 工具必须在命令行（终端）里运行，见下方说明。

### 如何打开命令行

1. 按 `Win + R`，输入 `cmd`，回车
2. 或者在文件夹空白处按住 `Shift` 右键 → **在此处打开命令窗口**
3. 进入 pgflow.exe 所在目录：

```cmd
cd C:\PgFlow\pgflow
```

验证安装成功：

```cmd
pgflow.exe --help
```

看到命令列表说明安装成功。

---

## 四、第一次启动配置

在命令行中运行初始化向导：

```cmd
pgflow.exe onboard --wizard
```

向导会依次询问：

**第 1 步：选择工作目录**
- 直接回车使用默认路径 `C:\Users\你的用户名\.pgflow\workspace`
- 或输入自定义路径

**第 2 步：配置 AI 服务**
- 选择 `openrouter` 作为提供商
- 粘贴你的 API Key
- 选择模型（推荐 `anthropic/claude-opus-4-5`）

**第 3 步：选择聊天渠道**
- 推荐选择 `telegram`
- 后续步骤会指导你填写 Bot Token

配置完成后，配置文件保存在：
```
C:\Users\你的用户名\.pgflow\config.json
```

---

## 五、连接 Telegram 开始聊天

### 步骤 1：创建 Telegram Bot

1. 打开 Telegram，搜索 `@BotFather`
2. 发送 `/newbot`
3. 输入机器人名称（例如：`我的AI助手`）
4. 输入机器人用户名（必须以 `bot` 结尾，例如：`myai_helper_bot`）
5. BotFather 返回一串 Token，格式类似：
   ```
   1234567890:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   复制保存。

### 步骤 2：获取你的 Telegram 用户 ID

1. Telegram 搜索 `@userinfobot`
2. 发送任意消息
3. 它会回复你的用户 ID（纯数字，例如 `123456789`）

### 步骤 3：填写配置文件

用记事本打开 `C:\Users\你的用户名\.pgflow\config.json`，找到 `channels` 部分，修改为：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "你的Bot Token",
      "allowFrom": ["你的用户ID"]
    }
  }
}
```

### 步骤 4：启动网关

```cmd
pgflow.exe gateway
```

看到类似 `Telegram bot started` 的提示说明连接成功。

现在打开 Telegram，给你的 Bot 发消息，AI 就会回复你了！

---

## 六、设置开机自动启动

每次开机手动运行很麻烦，一键设置自动启动：

```cmd
pgflow.exe service install
```

设置成功后，每次开机登录 Windows，PgFlow 会自动在后台启动，无需任何操作。

**检查状态：**

```cmd
pgflow.exe service status
```

**取消自动启动：**

```cmd
pgflow.exe service uninstall
```

---

## 七、管理面板使用

PgFlow 提供一个本地网页管理面板：

```cmd
pgflow.exe dashboard
```

执行后会自动在浏览器打开 `http://localhost:18791`

面板功能：

| 标签页 | 功能 |
|--------|------|
| 状态 | 查看当前运行状态、连接的渠道 |
| 技能 | 查看已安装的 AI 技能 |
| 配置 | 浏览当前配置内容 |
| 日志 | 查看运行日志，排查问题 |

---

## 八、常见问题

**Q：双击 pgflow.exe 闪退是坏了吗？**
A：不是，这是正常现象。请在命令行（cmd）里运行，不要双击。

**Q：提示"Config: ✗"是什么意思？**
A：说明还没有完成初始化配置，运行 `pgflow.exe onboard --wizard` 完成配置。

**Q：Telegram 发消息没有回复？**
A：检查以下几点：
- `pgflow.exe gateway` 是否在运行
- `allowFrom` 里是否填了你的用户 ID
- API Key 是否正确、余额是否充足

**Q：关掉命令行窗口后 AI 就不工作了？**
A：设置开机自启后就不用开着命令行了。或者在运行 gateway 时不要关闭那个窗口。

**Q：如何修改 AI 的性格？**
A：编辑 `C:\Users\你的用户名\.pgflow\workspace\SOUL.md`，按你的喜好描述 AI 的性格和行为方式。

**Q：如何让 AI 记住关于我的信息？**
A：编辑 `C:\Users\你的用户名\.pgflow\workspace\USER.md`，填写你的基本信息、偏好等。

**Q：如何安装更多技能？**
A：需要先安装 Node.js，然后运行：
```cmd
pgflow.exe skill search "你想要的功能"
pgflow.exe skill install 技能名称
```

---

## 九、与原版对比

PgFlow 基于开源项目 [nanobot](https://github.com/HKUDS/nanobot) 开发，在保留全部原版功能的基础上，针对普通用户做了多项改进。

### 功能对比

| 功能 | 原版 nanobot | PgFlow |
|------|-------------|--------|
| 核心 AI 能力 | ✅ | ✅ 完整保留 |
| 多渠道支持（Telegram/QQ/微信等） | ✅ | ✅ 完整保留 |
| 技能系统（Skills） | ✅ | ✅ 完整保留 |
| 文件/命令/搜索工具 | ✅ | ✅ 完整保留 |
| 本地管理面板 | ❌ 无 | ✅ 新增（localhost:18791） |
| 开机自动启动 | ❌ 无 | ✅ 新增（一键安装） |
| Windows .exe 独立打包 | ❌ 需要 Python 环境 | ✅ 新增（无需 Python） |
| macOS .dmg 打包脚本 | ❌ 无 | ✅ 新增 |
| 配置文件路径 | `~/.nanobot/` | `~/.pgflow/`（独立空间） |
| CLI 命令 | `nanobot` | `pgflow` |

### 定位差异

| 维度 | 原版 nanobot | PgFlow |
|------|-------------|--------|
| 主要目标用户 | 开发者、技术用户 | 普通用户（C 端） |
| 安装方式 | 需要 Python + pip | 下载 .exe 即用 |
| 运行方式 | 手动启动 | 开机自动运行 |
| 管理方式 | 命令行 | 命令行 + 网页面板 |
| 数据隔离 | 与代码路径混用 | 独立的 `~/.pgflow/` 目录 |

### 总结

PgFlow 的核心引擎与 nanobot 完全一致，稳定性和 AI 能力没有折扣。主要差别在于**更低的上手门槛**：普通用户不需要了解 Python、虚拟环境、pip 等概念，下载解压后按本教程操作即可开始使用。

---

*如有问题请访问：[https://github.com/leoyangx/PgFlow/issues](https://github.com/leoyangx/PgFlow/issues)*
