# Changelog

All notable changes to PgFlow are documented here.

Format: `## vX.Y.Z — YYYY-MM-DD`

---

## v0.1.3 — 2026-04-03

### 智能体能力升级

- **SOUL.md 重构**：从人格描述升级为四层行为契约（身份 / 行为纪律 / 行动安全 / 沟通契约），明确 PgFlow 定位为高级智能体而非聊天机器人
- **MEMORY.md 截断保护**：超过 200 行或 25KB 时自动截断并追加警告，防止上下文无限膨胀

### 管理面板全面重构

- **布局**：顶部横向导航改为左侧竖排导航栏，内容区充分利用宽度
- **状态页**：网关状态 + 版本信息并排，运行状态 + 已启用渠道并排，减少纵向滚动
- **日志页**：修复 ERROR / WARNING / INFO / DEBUG 过滤按钮点击后无内容的 Bug；切换 Tab 时自动加载日志；过滤改用词边界正则，避免误匹配
- **文档页**：从滚动锚点导航改为子页面切换，15 个章节独立显示，默认展示 Windows 使用说明

### 文档完善

- `CONTRIBUTING.md`：补充 uv 命令、渠道和技能开发指南
- `COMMUNICATION.md`：重写为结构化社区指引
- 新增 `CHANGELOG.md`（本文件）

---

## v0.1.2 — 2026-03-XX

### 安全架构升级

- 移除 litellm 依赖，改用原生 `openai` + `anthropic` SDK，消除供应链风险
- 新增 `AnthropicProvider`（原生思维链、流式推送、prompt caching）
- 新增 `OpenAICompatProvider`（统一所有 OpenAI 兼容接口）

### 图形化管理面板（全新）

- 本地 Web UI，端口 18791，仅监听 127.0.0.1
- 配置页：表单化替代手写 JSON
- 日志页：实时日志 + 级别过滤 + 颜色高亮
- 文档页：内置 10 个渠道接入教程
- 技能页：可视化管理已安装技能

### 架构同步

- 同步上游 AgentRunner / AgentHook 重构
- 飞书 CardKit 流式卡片推送
- 邮件渠道 SPF / DKIM 验证

### Windows 体验

- PyInstaller 打包，解压即用
- 系统托盘动态菜单（网关运行时显示「重启」，停止时显示「开启」）
- 一键更新：bat 脚本替换文件，绕过 Windows 文件锁

### 国内服务商

- 新增：AiHubMix、MiniMax、Mistral、阶跃星辰、硅基流动、火山引擎等

---

## v0.1.1 及更早

请查看 [GitHub Releases](https://github.com/leoyangx/PgFlow/releases) 页面。
