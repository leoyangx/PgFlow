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
    --muted: #6b7280; --radius: 10px;
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
  .card h2 { font-size: 15px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; margin-bottom: 16px; }
  .row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); }
  .row:last-child { border-bottom: none; }
  .row label { color: var(--muted); font-size: 13px; }
  .row value { font-size: 14px; font-family: monospace; }
  .badge { display: inline-block; padding: 3px 10px; border-radius: 99px; font-size: 12px; font-weight: 600; }
  .badge.green { background: #0d2e1f; color: var(--green); }
  .badge.red { background: #2e0d0d; color: var(--red); }
  .badge.gray { background: #1e2030; color: var(--muted); }
  .skill-list { list-style: none; }
  .skill-list li { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
  .skill-list li:last-child { border-bottom: none; }
  .skill-icon { font-size: 20px; }
  .skill-name { font-size: 14px; font-weight: 500; }
  .skill-desc { font-size: 12px; color: var(--muted); margin-top: 2px; }
  pre { background: #0a0c15; border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-size: 12px; overflow-x: auto; line-height: 1.6; color: #a8b3cf; white-space: pre-wrap; word-break: break-all; }
  .empty { color: var(--muted); font-size: 14px; text-align: center; padding: 40px 0; }
  .refresh-btn { float: right; background: var(--accent); color: #fff; border: none; border-radius: 6px; padding: 6px 14px; cursor: pointer; font-size: 13px; margin-top: -4px; }
  .refresh-btn:hover { opacity: .85; }
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
    <ul id="skill-list" class="skill-list"><li class="empty">加载中…</li></ul>
  </div>
</div>

<!-- CONFIG TAB -->
<div id="tab-config" class="tab">
  <div class="card">
    <h2>当前配置 <button class="refresh-btn" onclick="loadConfig()">刷新</button></h2>
    <div id="config-content"><div class="empty">加载中…</div></div>
  </div>
</div>

<!-- LOGS TAB -->
<div id="tab-logs" class="tab">
  <div class="card">
    <h2>运行日志 <button class="refresh-btn" onclick="loadLogs()">刷新</button></h2>
    <pre id="log-content">加载中…</pre>
  </div>
</div>

</main>
<script>
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
  if (name === 'config') loadConfig();
  if (name === 'logs') loadLogs();
}

function mask(v) {
  if (!v || v.length <= 4) return '****';
  return '*'.repeat(Math.max(0, v.length - 4)) + v.slice(-4);
}

function row(label, val) {
  return `<div class="row"><label>${label}</label><span>${val}</span></div>`;
}

async function api(path) {
  const r = await fetch(path);
  return r.json();
}

async function loadStatus() {
  const d = await api('/api/status');
  const sr = document.getElementById('status-rows');
  const wr = document.getElementById('workspace-rows');

  // Show setup banner if not configured
  const banner = document.getElementById('setup-banner');
  if (!d.config_exists) {
    banner.style.display = 'block';
    // Show the actual exe path so user can copy and run it
    const cmd = document.getElementById('onboard-cmd');
    const exe = d.exe_path || 'pgflow';
    cmd.innerText = `"${exe}" onboard --wizard`;
  } else {
    banner.style.display = 'none';
  }

  const configBadge = d.config_exists
    ? `<span class="badge green">已配置</span>`
    : `<span class="badge red">未配置</span>`;
  const modelVal = d.model ? `<code>${d.model}</code>` : `<span class="badge gray">未设置</span>`;
  const providerVal = d.provider ? `<code>${d.provider}</code>` : `<span class="badge gray">auto</span>`;
  const apiKeyVal = d.api_key_set
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
    row('SOUL.md', d.soul_md ? '<span class="badge green">存在</span>' : '<span class="badge gray">未创建</span>') +
    row('USER.md', d.user_md ? '<span class="badge green">存在</span>' : '<span class="badge gray">未创建</span>') +
    row('MEMORY.md', d.memory_md ? '<span class="badge green">存在</span>' : '<span class="badge gray">未创建</span>');
}

async function loadSkills() {
  const d = await api('/api/skills');
  const el = document.getElementById('skill-list');
  if (!d.skills || d.skills.length === 0) {
    el.innerHTML = '<li><div class="empty">暂无技能 — 在工作区 skills/ 目录下放置 SKILL.md 文件即可添加</div></li>';
    return;
  }
  el.innerHTML = d.skills.map(s => `
    <li>
      <span class="skill-icon">${s.icon || '🔧'}</span>
      <div>
        <div class="skill-name">${s.name}</div>
        <div class="skill-desc">${s.description || ''}</div>
      </div>
    </li>
  `).join('');
}

async function loadConfig() {
  const d = await api('/api/config');
  const el = document.getElementById('config-content');
  if (!d.config) {
    el.innerHTML = '<div class="empty">配置文件不存在，请先运行 pgflow onboard</div>';
    return;
  }
  // Render as flat key-value rows, masking sensitive fields
  const sensitive = ['apiKey', 'api_key', 'token', 'secret', 'password'];
  function renderObj(obj, prefix) {
    let html = '';
    for (const [k, v] of Object.entries(obj)) {
      const fullKey = prefix ? prefix + '.' + k : k;
      if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
        html += renderObj(v, fullKey);
      } else {
        const isSensitive = sensitive.some(s => k.toLowerCase().includes(s.toLowerCase()));
        let display = v === null || v === '' ? '<span class="masked">未设置</span>' : String(v);
        if (isSensitive && v) display = `<span class="masked">${mask(String(v))}</span>`;
        html += row(`<span class="config-key">${fullKey}</span>`, `<span class="config-val">${display}</span>`);
      }
    }
    return html;
  }
  el.innerHTML = renderObj(d.config, '');
}

async function loadLogs() {
  const d = await api('/api/logs');
  document.getElementById('log-content').textContent = d.logs || '（暂无日志）';
}

// Initial load
loadStatus();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# API handlers
# ---------------------------------------------------------------------------

def _get_status() -> dict:
    from nanobot import __version__
    from nanobot.config.loader import get_config_path, load_config

    config_path = get_config_path()
    config_exists = config_path.exists()

    # Resolve the exe path so the dashboard can show the correct command
    import sys
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


def _get_skills() -> dict:
    from nanobot.store.skills import list_installed

    try:
        skills = list_installed()
    except Exception:
        skills = []

    return {"skills": skills}




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
            lines = content.splitlines()[-200:]  # last 200 lines
        else:
            lines = ["（日志目录为空）"]
    except Exception:
        lines = ["（无法读取日志）"]

    return {"logs": "\n".join(lines)}


# ---------------------------------------------------------------------------
# HTTP request handler
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silence default access log
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

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            self._send_html(_HTML)
        elif path == "/api/status":
            self._send_json(_get_status())
        elif path == "/api/skills":
            self._send_json(_get_skills())
        elif path == "/api/config":
            self._send_json(_get_config())
        elif path == "/api/logs":
            self._send_json(_get_logs())
        else:
            self.send_response(404)
            self.end_headers()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start_dashboard(port: int = DASHBOARD_PORT, open_browser: bool = True) -> HTTPServer:
    """Start the dashboard HTTP server in a background daemon thread.

    Returns the HTTPServer instance (call .shutdown() to stop).
    """
    server = HTTPServer(("127.0.0.1", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    url = f"http://localhost:{port}"
    if open_browser:
        threading.Timer(0.3, webbrowser.open, args=(url,)).start()

    return server
