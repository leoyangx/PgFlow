# PgFlow 维护操作手册

---

## 一、修改代码后推送到 GitHub

```bash
# 1. 查看改了哪些文件
git status

# 2. 把改动的文件加入暂存区（把 文件名 替换成实际文件）
git add 文件名

# 或者一次性加入所有改动
git add -A

# 3. 提交，引号内写本次改动说明
git commit -m "fix: 修复了什么问题"

# 4. 推送到 GitHub
git push origin main
```

---

## 二、打包 Windows exe

> 打包前必须先完全退出 PgFlow（托盘右键 → 退出）

```bash
# 在项目根目录执行
py -m PyInstaller build/windows/pgflow.spec --noconfirm
```

打包完成后文件在 `dist/pgflow/` 文件夹。

---

## 三、压缩成 zip 发布包

```bash
# 在 dist 目录下执行（把版本号改成实际版本）
cd dist
powershell -Command "Compress-Archive -Path pgflow -DestinationPath pgflow-v0.1.2-windows.zip -Force"
```

zip 文件生成在 `dist/` 目录下。

---

## 四、发布新版本（Releases）

**第一步：更新版本号**

改两个文件：

- `nanobot/__init__.py` → 把 `__version__ = "0.1.1"` 改成新版本号
- `version.json` → 把 `version` 和 `download_url` 改成新版本号

**第二步：推送代码**

```bash
git add -A
git commit -m "chore: release v0.1.2"
git push origin main
```

**第三步：打 tag**

```bash
# 把版本号改成实际版本
git tag v0.1.2
git push origin v0.1.2
```

**第四步：在 GitHub 网页创建 Release**

1. 打开 https://github.com/leoyangx/PgFlow/releases/new
2. Tag 选 `v0.1.2`
3. Title 填版本号和简短说明
4. 上传 `dist/pgflow-v0.1.2-windows.zip`
5. 点击 Publish release

---

## 五、从上游原版仓库同步更新

> 原版仓库地址：https://github.com/HKUDS/nanobot.git

**第一步：拉取上游最新代码**

```bash
git fetch upstream
```

> 如果提示 `upstream` 不存在，先执行一次：
> `git remote add upstream https://github.com/HKUDS/nanobot.git`

**第二步：查看上游有哪些新提交**

```bash
git log upstream/main --oneline -20
```

**第三步：挑选需要的提交合入（Cherry-pick）**

```bash
# 把 abc1234 替换成你要合入的 commit hash（从上面的日志里复制）
git cherry-pick abc1234
```

如果提示冲突，且冲突文件是 `README.md`，执行：

```bash
# 恢复我们自己的 README，不用上游的
git checkout HEAD -- README.md
git add README.md
git cherry-pick --continue --no-edit
```

**第四步：推送**

```bash
git push origin main
```

**注意事项：**
- `README.md` 永远保持我们自己的版本，不用上游的
- `tests/` 测试文件按需评估，上游的不一定适配我们的环境
- `nanobot/dashboard/server.py` 和 `nanobot/tray/app.py` 是我们自己的，不要用上游覆盖

---

## 六、常见问题

**打包报错 PermissionError / 文件被占用**
→ 托盘右键退出 PgFlow，再重新打包

**git push 报错 rejected**
→ 先执行 `git pull origin main`，再重新 push

**CI 报错（GitHub 上出现红叉）**
→ 点开 Actions 页面查看具体报错，通常是测试文件或依赖问题

---

## 七、给 AI 助手的提示词

如果你需要让 AI 帮你完成上述操作，把以下内容发给它：

```
你好，我是 PgFlow 项目的维护者。PgFlow 是基于 https://github.com/HKUDS/nanobot 二次开发的个人 AI 助手桌面应用，使用 Python + PyInstaller 打包为 Windows exe，有一个本地 Dashboard（HTTP 服务，端口 18791），通过系统托盘图标管理网关进程。

项目仓库：https://github.com/leoyangx/PgFlow
上游仓库：https://github.com/HKUDS/nanobot
本地路径：C:\Users\luck\Desktop\PgFlow

关键文件：
- nanobot/dashboard/server.py  （面板 HTML+API，单文件）
- nanobot/tray/app.py          （系统托盘）
- nanobot/__init__.py          （版本号）
- version.json                 （GitHub Pages 版本检查用）
- build/windows/pgflow.spec    （PyInstaller 打包配置）

规则：
- README.md 始终保持我们自己的版本，不用上游的
- tests/ 文件遇到冲突时保留我们的版本
- 打包命令：py -m PyInstaller build/windows/pgflow.spec --noconfirm
- 压缩命令：在 dist/ 目录执行 powershell -Command "Compress-Archive -Path pgflow -DestinationPath pgflow-vX.X.X-windows.zip -Force"

我现在需要你帮我：[在这里描述你要做的事]
```
