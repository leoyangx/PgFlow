# Contributing to PgFlow

PgFlow 是一个本地优先的个人 AI 助手，目标是成为真正的高级智能体，而不仅仅是聊天机器人。

欢迎任何形式的贡献：Bug 修复、新渠道接入、技能包、文档改进。

---

## 分支策略

| 分支 | 用途 | 稳定性 |
|------|------|--------|
| `main` | 稳定版本 | 生产可用 |
| `nightly` | 实验性功能 | 可能有 Bug |

- 新功能、重构、API 变更 → 目标分支 `nightly`
- Bug 修复、文档、小调整 → 目标分支 `main`

---

## 开发环境

推荐使用 [uv](https://docs.astral.sh/uv/)（更快）：

```bash
git clone https://github.com/leoyangx/PgFlow.git
cd PgFlow

# 安装全部依赖（含 dev/test extras）
uv sync --all-extras

# 运行测试
uv run pytest tests/ -q

# 单个测试文件
uv run pytest tests/agent/test_loop_save_turn.py -v

# 代码检查 + 格式化
uv run ruff check pgflow/
uv run ruff format pgflow/
```

也可以用 pip：

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

---

## 代码规范

- 行长上限：100 字符（`ruff` 配置）
- Python 版本：3.11+（CI 在 3.11、3.12、3.13 上运行）
- Lint 规则：`ruff` E、F、I、N、W
- 异步模型：全程 `asyncio`，测试用 `pytest-asyncio`（`asyncio_mode = "auto"`）
- 风格倾向：可读性优先于技巧性，聚焦的小补丁优于大范围重写

---

## 添加新渠道

参见 `docs/CHANNEL_PLUGIN_GUIDE.md`。简要流程：

1. 继承 `BaseChannel`，实现 `start()` / `stop()` / `send()`
2. 在收到消息时调用 `self._handle_message()`
3. 通过 `pgflow.channels` entry point 注册

---

## 添加新技能

在 `pgflow/skills/<skill-name>/SKILL.md` 中定义技能，或放在 `~/.pgflow/workspace/skills/<skill-name>/SKILL.md` 作为用户技能。格式参考现有技能包（如 `pgflow/skills/weather/SKILL.md`）。

---

## 打包 Windows exe

```bash
py -m PyInstaller build/windows/pgflow.spec --noconfirm
# 输出：dist/pgflow/pgflow.exe
```

---

## 提问 / 反馈

- Bug 报告 → [GitHub Issues](https://github.com/leoyangx/PgFlow/issues)
- 功能讨论 → [GitHub Discussions](https://github.com/leoyangx/PgFlow/discussions)
