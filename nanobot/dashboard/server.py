"""PgFlow local management dashboard — runs on http://localhost:18791"""

from __future__ import annotations

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

DASHBOARD_PORT = 18791


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PgFlow Dashboard</title>
<style>
  :root {
    --bg: #0f1117; --card: #1a1d2e; --border: #2a2d3e;
    --accent: #4f8ef7; --green: #3ecf8e; --red: #f66; --text: #e2e8f0;
    --muted: #6b7280; --radius: 10px; --amber: #f59e0b;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }
  header { background: var(--card); border-bottom: 1px solid var(--border); padding: 16px 32px; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 20px; font-weight: 700; color: var(--accent); }
  header span.logo { font-size: 24px; }
  nav { display: flex; gap: 0; padding: 0 32px; background: var(--card); border-bottom: 1px solid var(--border); }
  nav button { background: none; border: none; color: var(--muted); padding: 12px 20px; cursor: pointer; font-size: 14px; border-bottom: 2px solid transparent; transition: all .2s; }
  nav button.active, nav button:hover { color: var(--accent); border-bottom-color: var(--accent); }
  main { padding: 32px; max-width: 960px; margin: 0 auto; }
  .tab { display: none; } .tab.active { display: block; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; margin-bottom: 20px; }
  .card h2 { font-size: 15px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
  .row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); }
  .row:last-child { border-bottom: none; }
  .row label { color: var(--muted); font-size: 13px; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 99px; font-size: 12px; font-weight: 600; }
  .badge.green { background: #0d2e1f; color: var(--green); }
  .badge.red { background: #2e0d0d; color: var(--red); }
  .badge.gray { background: #1e2030; color: var(--muted); }
  .badge.amber { background: #2e1f0d; color: var(--amber); }
  .skill-list { list-style: none; }
  .skill-list li { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
  .skill-list li:last-child { border-bottom: none; }
  .skill-icon { font-size: 20px; }
  .skill-name { font-size: 14px; font-weight: 500; }
  .skill-desc { font-size: 12px; color: var(--muted); margin-top: 2px; }
  pre { background: #0a0c15; border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-size: 12px; overflow-x: auto; line-height: 1.6; color: #a8b3cf; white-space: pre-wrap; word-break: break-all; max-height: 500px; overflow-y: auto; }
  .empty { color: var(--muted); font-size: 14px; text-align: center; padding: 40px 0; }
  .btn { border: none; border-radius: 6px; padding: 6px 14px; cursor: pointer; font-size: 13px; font-weight: 500; transition: opacity .15s; }
  .btn:hover { opacity: .85; }
  .btn:disabled { opacity: .4; cursor: not-allowed; }
  .btn-primary { background: var(--accent); color: #fff; }
  .btn-green  { background: #0d5c32; color: var(--green); }
  .btn-red    { background: #5c1a1a; color: var(--red); }
  .btn-muted  { background: #2a2d3e; color: var(--muted); }
  .btn-row { display: flex; gap: 8px; }
  .config-key { color: var(--muted); font-size: 12px; font-family: monospace; }
  .config-val { font-size: 13px; font-family: monospace; word-break: break-all; }
  .setup-banner { background: linear-gradient(135deg, #1a2744 0%, #1a1d2e 100%); border: 1px solid var(--accent); border-radius: var(--radius); padding: 40px 32px; text-align: center; margin-bottom: 20px; }
  .setup-banner h2 { font-size: 22px; color: var(--accent); margin-bottom: 12px; }
  .setup-banner p { color: var(--muted); font-size: 14px; line-height: 1.8; margin-bottom: 24px; }
  .setup-steps { text-align: left; display: inline-block; margin: 0 auto 24px; }
  .setup-steps li { color: var(--text); font-size: 14px; padding: 6px 0; list-style: none; }
  .setup-steps li::before { content: attr(data-step); display: inline-block; width: 24px; height: 24px; background: var(--accent); color: #fff; border-radius: 50%; text-align: center; line-height: 24px; font-size: 12px; font-weight: 700; margin-right: 10px; }
  .cmd-block { background: #0a0c15; border: 1px solid var(--border); border-radius: 8px; padding: 14px 20px; font-family: monospace; font-size: 14px; color: var(--green); text-align: left; margin: 0 auto 12px; display: inline-block; min-width: 320px; cursor: pointer; }
  .cmd-block:hover { border-color: var(--accent); }
  .copy-hint { font-size: 12px; color: var(--muted); }
  /* Gateway status */
  .gateway-status { display: flex; align-items: center; gap: 10px; }
  .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
  .dot.green { background: var(--green); box-shadow: 0 0 8px var(--green); }
  .dot.red   { background: var(--red); box-shadow: 0 0 4px var(--red); }
  .dot.amber { background: var(--amber); }
  /* Config editor */
  .editor-wrap { position: relative; }
  #config-editor { width: 100%; min-height: 320px; background: #0a0c15; border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-size: 13px; font-family: monospace; color: #a8b3cf; line-height: 1.6; resize: vertical; outline: none; }
  #config-editor:focus { border-color: var(--accent); }
  .editor-actions { display: flex; gap: 8px; margin-top: 12px; align-items: center; }
  .save-msg { font-size: 13px; margin-left: 8px; }
  .save-msg.ok  { color: var(--green); }
  .save-msg.err { color: var(--red); }
  /* Toggle switch for skills */
  .toggle { position: relative; width: 36px; height: 20px; flex-shrink: 0; }
  .toggle input { opacity: 0; width: 0; height: 0; }
  .toggle-slider { position: absolute; inset: 0; background: #2a2d3e; border-radius: 20px; cursor: pointer; transition: .2s; }
  .toggle input:checked + .toggle-slider { background: var(--green); }
  .toggle-slider:before { content: ''; position: absolute; width: 14px; height: 14px; left: 3px; top: 3px; background: #fff; border-radius: 50%; transition: .2s; }
  .toggle input:checked + .toggle-slider:before { transform: translateX(16px); }
  .skill-row { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
  .skill-row:last-child { border-bottom: none; }
  .skill-meta { flex: 1; }
</style>
</head>
<body>
<header>
  <span class="logo">🌊</span>
  <h1>PgFlow Dashboard</h1>
</header>
<nav>
  <button class="active" onclick="show('status', this)">状态</button>
  <button onclick="show('skills', this)">技能</button>
  <button onclick="show('config', this)">配置</button>
  <button onclick="show('logs', this)">日志</button>
</nav>
<main>

<!-- STATUS TAB -->
<div id="tab-status" class="tab active">
  <div id="setup-banner" style="display:none" class="setup-banner">
    <h2>👋 欢迎使用 PgFlow</h2>
    <p>检测到尚未完成初始配置。<br>请打开命令行（终端），运行以下命令完成配置：</p>
    <div class="cmd-block" id="onboard-cmd" onclick="copyCmd(this)" title="点击复制">加载中…</div>
    <br><span class="copy-hint">点击命令可复制到剪贴板</span>
    <br><br>
    <ol class="setup-steps">
      <li data-step="1">选择工作目录（直接回车使用默认）</li>
      <li data-step="2">选择 AI 服务商并填写 API Key</li>
      <li data-step="3">选择聊天渠道（如 Telegram）</li>
      <li data-step="4">保存配置</li>
    </ol>
    <p>配置完成后，刷新此页面即可查看状态。</p>
  </div>

  <!-- Gateway Status (read-only — use tray icon to start/stop) -->
  <div class="card">
    <h2>网关状态</h2>
    <div class="row">
      <label>运行状态</label>
      <div class="gateway-status">
        <span class="dot" id="gw-dot"></span>
        <span id="gw-label">检测中…</span>
      </div>
    </div>
    <div class="row">
      <label>提示</label>
      <span style="font-size:12px;color:var(--muted)">通过系统托盘图标启动或停止网关</span>
    </div>
  </div>

  <div class="card">
    <h2>运行状态</h2>
    <div id="status-rows"><div class="empty">加载中…</div></div>
  </div>
  <div class="card">
    <h2>工作区</h2>
    <div id="workspace-rows"><div class="empty">加载中…</div></div>
  </div>
</div>

<!-- SKILLS TAB -->
<div id="tab-skills" class="tab">
  <div class="card">
    <h2>已安装技能</h2>
    <div id="skill-list"><div class="empty">加载中…</div></div>
  </div>
</div>

<!-- CONFIG TAB -->
<div id="tab-config" class="tab">
  <div class="card">
    <h2>
      <span>编辑配置</span>
      <button class="btn btn-muted" onclick="loadConfigEditor()">↺ 重新加载</button>
    </h2>
    <p style="font-size:12px;color:var(--muted);margin-bottom:12px">直接编辑 JSON，点击保存后立即写入 config.json 文件。敏感字段（API Key 等）以明文显示，请勿截图分享。</p>
    <div class="editor-wrap">
      <textarea id="config-editor" spellcheck="false"></textarea>
    </div>
    <div class="editor-actions">
      <button class="btn btn-primary" onclick="saveConfig()">💾 保存配置</button>
      <button class="btn btn-muted"   onclick="loadConfigEditor()">取消</button>
      <span class="save-msg" id="save-msg"></span>
    </div>
  </div>
</div>

<!-- LOGS TAB -->
<div id="tab-logs" class="tab">
  <div class="card">
    <h2>
      <span>运行日志</span>
      <button class="btn btn-muted" onclick="loadLogs()">↺ 刷新</button>
    </h2>
    <pre id="log-content">加载中…</pre>
  </div>
</div>

</main>
<script>
// ── Utilities ──────────────────────────────────────────────────────────────
function copyCmd(el) {
  navigator.clipboard.writeText(el.innerText).then(() => {
    const orig = el.innerText;
    el.innerText = '已复制 ✓';
    setTimeout(() => { el.innerText = orig; }, 1500);
  });
}

function show(name, btn) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
  if (name === 'status') loadStatus();
  if (name === 'skills') loadSkills();
  if (name === 'config') loadConfigEditor();
  if (name === 'logs')   loadLogs();
}

function mask(v) {
  if (!v || v.length <= 4) return '****';
  return '*'.repeat(Math.max(0, v.length - 4)) + v.slice(-4);
}

function row(label, val) {
  return `<div class="row"><label>${label}</label><span>${val}</span></div>`;
}

async function api(path, opts) {
  const r = await fetch(path, opts);
  return r.json();
}

// ── Status ─────────────────────────────────────────────────────────────────
async function loadStatus() {
  const d = await api('/api/status');
  const sr = document.getElementById('status-rows');
  const wr = document.getElementById('workspace-rows');

  const banner = document.getElementById('setup-banner');
  if (!d.config_exists) {
    banner.style.display = 'block';
    const cmd = document.getElementById('onboard-cmd');
    const exe = d.exe_path || 'pgflow';
    cmd.innerText = `"${exe}" onboard --wizard`;
  } else {
    banner.style.display = 'none';
  }

  const configBadge = d.config_exists
    ? `<span class="badge green">已配置</span>`
    : `<span class="badge red">未配置</span>`;
  const modelVal    = d.model    ? `<code>${d.model}</code>`    : `<span class="badge gray">未设置</span>`;
  const providerVal = d.provider ? `<code>${d.provider}</code>` : `<span class="badge gray">auto</span>`;
  const apiKeyVal   = d.api_key_set
    ? `<span class="badge green">已设置</span>`
    : `<span class="badge red">未设置</span>`;

  sr.innerHTML =
    row('配置文件', configBadge) +
    row('配置路径', `<code class="config-key">${d.config_path}</code>`) +
    row('模型', modelVal) +
    row('Provider', providerVal) +
    row('API Key', apiKeyVal) +
    row('版本', `<code>${d.version}</code>`);

  const wsExists = d.workspace_exists
    ? `<span class="badge green">存在</span>`
    : `<span class="badge red">不存在</span>`;
  wr.innerHTML =
    row('工作区路径', `<code class="config-key">${d.workspace}</code>`) +
    row('工作区状态', wsExists) +
    row('SOUL.md',   d.soul_md   ? '<span class="badge green">存在</span>' : '<span class="badge gray">未创建</span>') +
    row('USER.md',   d.user_md   ? '<span class="badge green">存在</span>' : '<span class="badge gray">未创建</span>') +
    row('MEMORY.md', d.memory_md ? '<span class="badge green">存在</span>' : '<span class="badge gray">未创建</span>');

  // Also refresh gateway status
  loadGatewayStatus();
}

// ── Gateway Status ──────────────────────────────────────────────────────────
async function loadGatewayStatus() {
  const d = await api('/api/gateway');
  const dot   = document.getElementById('gw-dot');
  const label = document.getElementById('gw-label');

  if (d.running) {
    dot.className     = 'dot green';
    label.textContent = '运行中';
  } else {
    dot.className     = 'dot red';
    label.textContent = '已停止';
  }
}

// ── Skills ─────────────────────────────────────────────────────────────────
async function loadSkills() {
  const d  = await api('/api/skills');
  const el = document.getElementById('skill-list');
  if (!d.skills || d.skills.length === 0) {
    el.innerHTML = '<div class="empty">暂无技能 — 在工作区 skills/ 目录下放置 SKILL.md 文件即可添加</div>';
    return;
  }
  el.innerHTML = d.skills.map((s, i) => `
    <div class="skill-row">
      <span class="skill-icon">${s.icon || '🔧'}</span>
      <div class="skill-meta">
        <div class="skill-name">${s.name}</div>
        <div class="skill-desc">${s.description || ''}</div>
      </div>
      <label class="toggle" title="${s.enabled === false ? '启用' : '禁用'}技能">
        <input type="checkbox" ${s.enabled !== false ? 'checked' : ''}
               onchange="toggleSkill('${s.name}', this.checked)">
        <span class="toggle-slider"></span>
      </label>
    </div>
  `).join('');
}

async function toggleSkill(name, enabled) {
  try {
    await api('/api/skills', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, enabled}),
    });
  } catch(e) {
    // reload to show real state
    loadSkills();
  }
}

// ── Config Editor ──────────────────────────────────────────────────────────
async function loadConfigEditor() {
  const ta  = document.getElementById('config-editor');
  const msg = document.getElementById('save-msg');
  msg.textContent = '';
  ta.value = '加载中…';
  try {
    const d = await api('/api/config/raw');
    ta.value = d.raw || '';
  } catch(e) {
    ta.value = '读取失败';
  }
}

async function saveConfig() {
  const ta  = document.getElementById('config-editor');
  const msg = document.getElementById('save-msg');
  msg.textContent = '';

  // Validate JSON first
  try {
    JSON.parse(ta.value);
  } catch(e) {
    msg.className = 'save-msg err';
    msg.textContent = '❌ JSON 格式错误：' + e.message;
    return;
  }

  try {
    const r = await api('/api/config/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({raw: ta.value}),
    });
    if (r.ok) {
      msg.className = 'save-msg ok';
      msg.textContent = '✓ 已保存';
      setTimeout(() => { msg.textContent = ''; }, 3000);
    } else {
      msg.className = 'save-msg err';
      msg.textContent = '❌ ' + (r.error || '保存失败');
    }
  } catch(e) {
    msg.className = 'save-msg err';
    msg.textContent = '❌ 网络错误';
  }
}

// ── Logs ───────────────────────────────────────────────────────────────────
async function loadLogs() {
  const d = await api('/api/logs');
  const el = document.getElementById('log-content');
  el.textContent = d.logs || '（暂无日志）';
  el.scrollTop = el.scrollHeight;
}

// ── Init ───────────────────────────────────────────────────────────────────
loadStatus();
setInterval(loadGatewayStatus, 8000);  // auto-refresh gateway status every 8s
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Gateway process management (shared with tray when running in-process)
# ---------------------------------------------------------------------------

_gateway_proc = None
_gateway_lock = threading.Lock()


def _get_exe_path():
    import sys
    import shutil
    if getattr(sys, "frozen", False):
        return str(sys.executable)
    found = shutil.which("pgflow")
    return found if found else str(sys.executable)


def _gateway_running() -> bool:
    """Detect a running gateway by probing its port (18790).

    Port probe is sub-millisecond and works regardless of how the gateway
    was started (tray, CLI, or any other means).
    """
    import socket
    try:
        with socket.create_connection(("127.0.0.1", 18790), timeout=0.5):
            return True
    except (ConnectionRefusedError, OSError):
        return False


def _start_gateway_proc() -> None:
    global _gateway_proc
    import sys
    import subprocess
    with _gateway_lock:
        if _gateway_proc and _gateway_proc.poll() is None:
            return
        exe = _get_exe_path()
        kwargs: dict = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x08000000
        try:
            _gateway_proc = subprocess.Popen([exe, "gateway"], **kwargs)
        except Exception:
            pass


def _stop_gateway_proc() -> None:
    global _gateway_proc
    import subprocess
    with _gateway_lock:
        if _gateway_proc and _gateway_proc.poll() is None:
            _gateway_proc.terminate()
            try:
                _gateway_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _gateway_proc.kill()
        _gateway_proc = None


# ---------------------------------------------------------------------------
# API handlers
# ---------------------------------------------------------------------------

def _get_status() -> dict:
    from nanobot import __version__
    from nanobot.config.loader import get_config_path, load_config
    import sys

    config_path = get_config_path()
    config_exists = config_path.exists()

    if getattr(sys, "frozen", False):
        exe_path = sys.executable
    else:
        import shutil
        found = shutil.which("pgflow")
        exe_path = found if found else sys.executable

    status: dict = {
        "version": __version__,
        "config_path": str(config_path),
        "config_exists": config_exists,
        "exe_path": exe_path,
        "model": None,
        "provider": None,
        "api_key_set": False,
        "workspace": str(Path.home() / ".pgflow" / "workspace"),
        "workspace_exists": False,
        "soul_md": False,
        "user_md": False,
        "memory_md": False,
    }

    if config_exists:
        try:
            cfg = load_config(config_path)
            status["model"] = cfg.agents.defaults.model
            status["provider"] = cfg.agents.defaults.provider
            status["api_key_set"] = bool(cfg.get_api_key())
            ws = cfg.workspace_path
            status["workspace"] = str(ws)
            status["workspace_exists"] = ws.exists()
            status["soul_md"] = (ws / "SOUL.md").exists()
            status["user_md"] = (ws / "USER.md").exists()
            status["memory_md"] = (ws / "memory" / "MEMORY.md").exists()
        except Exception:
            pass

    return status


def _get_gateway() -> dict:
    return {"running": _gateway_running()}


def _post_gateway(action: str) -> dict:
    if action == "start":
        _start_gateway_proc()
    elif action == "stop":
        _stop_gateway_proc()
    elif action == "restart":
        _stop_gateway_proc()
        import time
        time.sleep(0.8)
        _start_gateway_proc()
    else:
        return {"ok": False, "error": f"unknown action: {action}"}
    return {"ok": True}


def _get_skills() -> dict:
    from nanobot.store.skills import list_installed
    try:
        skills = list_installed()
    except Exception:
        skills = []
    return {"skills": skills}


def _post_skills(name: str, enabled: bool) -> dict:
    """Toggle a skill's enabled state by adding/removing a .disabled marker file."""
    from nanobot.config.loader import get_config_path, load_config
    try:
        cfg = load_config(get_config_path())
        ws = cfg.workspace_path
        skill_dir = ws / "skills" / name
        marker = skill_dir / ".disabled"
        if enabled:
            marker.unlink(missing_ok=True)
        else:
            skill_dir.mkdir(parents=True, exist_ok=True)
            marker.touch()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _get_config_raw() -> dict:
    from nanobot.config.loader import get_config_path
    config_path = get_config_path()
    if not config_path.exists():
        return {"raw": ""}
    try:
        return {"raw": config_path.read_text(encoding="utf-8")}
    except Exception as e:
        return {"raw": "", "error": str(e)}


def _save_config(raw: str) -> dict:
    from nanobot.config.loader import get_config_path
    config_path = get_config_path()
    try:
        # Validate JSON
        json.loads(raw)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(raw, encoding="utf-8")
        return {"ok": True}
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"JSON 格式错误: {e}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _get_config() -> dict:
    from nanobot.config.loader import get_config_path, load_config
    config_path = get_config_path()
    if not config_path.exists():
        return {"config": None}
    try:
        cfg = load_config(config_path)
        return {"config": cfg.model_dump(mode="json", by_alias=True)}
    except Exception as e:
        return {"config": None, "error": str(e)}


def _get_logs() -> dict:
    from nanobot.config.paths import get_logs_dir
    logs_dir = get_logs_dir()
    lines: list[str] = []
    try:
        log_files = sorted(logs_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if log_files:
            content = log_files[0].read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()[-300:]
        else:
            lines = ["（日志目录为空）"]
    except Exception:
        lines = ["（无法读取日志）"]
    return {"logs": "\n".join(lines)}


# ---------------------------------------------------------------------------
# HTTP request handler
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send_html(_HTML)
        elif path == "/api/status":
            self._send_json(_get_status())
        elif path == "/api/gateway":
            self._send_json(_get_gateway())
        elif path == "/api/skills":
            self._send_json(_get_skills())
        elif path == "/api/config":
            self._send_json(_get_config())
        elif path == "/api/config/raw":
            self._send_json(_get_config_raw())
        elif path == "/api/logs":
            self._send_json(_get_logs())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_body()
        except Exception:
            body = {}

        if path == "/api/gateway":
            self._send_json(_post_gateway(body.get("action", "")))
        elif path == "/api/skills":
            self._send_json(_post_skills(body.get("name", ""), body.get("enabled", True)))
        elif path == "/api/config/save":
            self._send_json(_save_config(body.get("raw", "")))
        else:
            self.send_response(404)
            self.end_headers()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_dashboard(port: int = DASHBOARD_PORT, open_browser: bool = True) -> HTTPServer:
    """Start the dashboard HTTP server in a background daemon thread."""
    server = HTTPServer(("127.0.0.1", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{port}"
    if open_browser:
        threading.Timer(0.3, webbrowser.open, args=(url,)).start()

    return server
