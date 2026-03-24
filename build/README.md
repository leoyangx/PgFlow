# PgFlow 桌面打包指南

## Windows (.exe 安装包)

### 环境要求
- Python 3.11+（已安装 pgflow 依赖）
- [NSIS 3.x](https://nsis.sourceforge.io/)（可选，用于生成 .exe 安装包）

### 构建步骤

```bat
REM 在项目根目录运行
build\windows\build.bat
```

产物：
- `dist\pgflow\` — 独立可执行文件夹（可直接压缩分发）
- `dist\PgFlow-0.1.0-Setup.exe` — Windows 安装包（需要 NSIS）

### 安装包功能
- 安装到 `C:\Program Files\PgFlow\`
- 自动将 `pgflow.exe` 加入系统 PATH
- 创建桌面快捷方式
- 添加「程序与功能」卸载入口
- 卸载时**保留**用户数据（`~\.pgflow\`）

---

## macOS (.dmg)

### 环境要求
- Python 3.11+（已安装 pgflow 依赖）
- [create-dmg](https://github.com/create-dmg/create-dmg)（`brew install create-dmg`，可选）

### 构建步骤

```bash
# 在项目根目录运行
bash build/macos/build.sh
```

产物：
- `dist/pgflow/` — 独立可执行文件夹
- `dist/PgFlow-<version>-macOS.dmg` — macOS 磁盘镜像（需要 create-dmg）

---

## 常见问题

### Q: 打包后运行报错找不到模块
在 `pgflow.spec` 的 `hiddenimports` 里添加缺失的模块名，然后重新打包。

### Q: Windows 打包体积太大
`dist\pgflow\` 通常 200-400MB（含 Python 运行时）。
可以用 7-Zip 压缩成 .7z 分发，压缩率约 50%。

### Q: 如何测试打包结果是否正常

```bat
REM Windows
dist\pgflow\pgflow.exe --help
dist\pgflow\pgflow.exe onboard --wizard

REM macOS
./dist/pgflow/pgflow --help
./dist/pgflow/pgflow onboard --wizard
```

### Q: 如何更新版本号
修改 `nanobot/__init__.py` 里的 `__version__`，然后重新打包。

---

## 发布检查清单

- [ ] `pgflow --help` 正常显示
- [ ] `pgflow onboard --wizard` 可以完成配置
- [ ] `pgflow agent -m "你好"` 可以正常对话
- [ ] `pgflow dashboard` 可以打开管理面板
- [ ] `pgflow skill list` 显示内置技能
- [ ] 安装包可以正常安装和卸载
