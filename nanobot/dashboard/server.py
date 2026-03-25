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
  /* Form controls */
  .form-group { margin-bottom: 16px; }
  .form-group:last-child { margin-bottom: 0; }
  .form-label { display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }
  .form-hint { font-size: 11px; color: #4b5563; margin-left: 6px; }
  .form-input { width: 100%; background: #0a0c15; border: 1px solid var(--border); border-radius: 6px; padding: 9px 12px; font-size: 13px; color: var(--text); outline: none; font-family: inherit; transition: border-color .15s; }
  .form-input:focus { border-color: var(--accent); }
  .form-select { width: 100%; background: #0a0c15; border: 1px solid var(--border); border-radius: 6px; padding: 9px 12px; font-size: 13px; color: var(--text); outline: none; cursor: pointer; transition: border-color .15s; }
  .form-select:focus { border-color: var(--accent); }
  .input-eye { position: relative; }
  .input-eye .form-input { padding-right: 40px; }
  .eye-btn { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 16px; color: var(--muted); padding: 4px; line-height: 1; }
  /* Channel blocks */
  .channel-block { border-bottom: 1px solid var(--border); }
  .channel-block:last-child { border-bottom: none; }
  .channel-header { display: flex; align-items: center; gap: 10px; padding: 12px 0; cursor: pointer; user-select: none; }
  .channel-icon { font-size: 18px; width: 28px; text-align: center; }
  .channel-name { flex: 1; font-size: 14px; font-weight: 500; }
  .channel-arrow { font-size: 11px; color: var(--muted); transition: transform .2s; }
  .channel-arrow.open { transform: rotate(90deg); }
  .channel-body { padding: 4px 0 16px 38px; }
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
  /* Docs */
  .doc-section { margin-bottom: 32px; }
  .doc-section h3 { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 8px; }
  .doc-section p { font-size: 14px; color: #a8b3cf; line-height: 1.8; margin-bottom: 10px; }
  .doc-section ol, .doc-section ul { padding-left: 20px; margin-bottom: 10px; }
  .doc-section li { font-size: 14px; color: #a8b3cf; line-height: 1.9; }
  .doc-section li strong { color: var(--text); }
  .doc-code { display: inline-block; background: #0a0c15; border: 1px solid var(--border); border-radius: 4px; padding: 2px 8px; font-family: monospace; font-size: 12px; color: var(--green); }
  .doc-table { width: 100%; border-collapse: collapse; margin-bottom: 12px; font-size: 13px; }
  .doc-table th { text-align: left; padding: 8px 12px; background: #0a0c15; color: var(--muted); font-weight: 600; border-bottom: 1px solid var(--border); }
  .doc-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); color: #a8b3cf; vertical-align: top; }
  .doc-table tr:last-child td { border-bottom: none; }
  .doc-table td:first-child { color: var(--text); font-weight: 500; white-space: nowrap; }
  .doc-tip { background: #1a2744; border-left: 3px solid var(--accent); border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 13px; color: #a8b3cf; line-height: 1.7; }
  .doc-warn { background: #2e1f0d; border-left: 3px solid var(--amber); border-radius: 4px; padding: 10px 14px; margin-bottom: 12px; font-size: 13px; color: #a8b3cf; line-height: 1.7; }
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
  <button onclick="show('docs', this)">文档</button>
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

  <!-- 区块①：AI 模型 -->
  <div class="card">
    <h2>AI 模型</h2>
    <div class="form-group">
      <label class="form-label">服务商</label>
      <select id="cfg-provider" class="form-select" onchange="onProviderChange()">
        <option value="openrouter">OpenRouter（推荐，支持所有主流模型）</option>
        <option value="anthropic">Anthropic（Claude 官方）</option>
        <option value="openai">OpenAI（GPT 系列）</option>
        <option value="deepseek">DeepSeek</option>
        <option value="gemini">Google Gemini</option>
        <option value="zhipu">智谱 AI</option>
        <option value="dashscope">阿里云百炼（DashScope）</option>
        <option value="siliconflow">硅基流动（SiliconFlow）</option>
        <option value="volcengine">火山引擎</option>
        <option value="moonshot">Moonshot（月之暗面）</option>
        <option value="groq">Groq</option>
        <option value="custom">自定义（OpenAI 兼容接口）</option>
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">API Key</label>
      <div class="input-eye">
        <input id="cfg-apikey" type="password" class="form-input" placeholder="粘贴你的 API Key">
        <button class="eye-btn" onclick="toggleEye('cfg-apikey', this)" title="显示/隐藏">👁</button>
      </div>
    </div>
    <div class="form-group" id="custom-base-group" style="display:none">
      <label class="form-label">API Base URL <span class="form-hint">自定义接口地址</span></label>
      <input id="cfg-apibase" type="text" class="form-input" placeholder="https://api.example.com/v1">
    </div>
    <div class="form-group">
      <label class="form-label">模型 <span class="form-hint">格式：provider/model-name</span></label>
      <input id="cfg-model" type="text" class="form-input" placeholder="anthropic/claude-opus-4-5">
    </div>
  </div>

  <!-- 区块②：聊天渠道 -->
  <div class="card">
    <h2>聊天渠道</h2>
    <p style="font-size:12px;color:var(--muted);margin-bottom:16px">启用开关后填写对应凭据，保存即生效。</p>

    <!-- Telegram -->
    <div class="channel-block" id="ch-telegram">
      <div class="channel-header" onclick="toggleChannel('telegram')">
        <span class="channel-icon">✈️</span>
        <span class="channel-name">Telegram</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-telegram-enabled" onchange="onChannelToggle('telegram', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-telegram-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-telegram-body" style="display:none">
        <div class="form-group">
          <label class="form-label">Bot Token <span class="form-hint">向 @BotFather 获取</span></label>
          <div class="input-eye">
            <input id="ch-telegram-token" type="password" class="form-input" placeholder="123456:ABC-DEF...">
            <button class="eye-btn" onclick="toggleEye('ch-telegram-token', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">允许的用户 ID <span class="form-hint">逗号分隔，留空拒绝所有人，填 * 允许所有人</span></label>
          <input id="ch-telegram-allow" type="text" class="form-input" placeholder="123456789, 987654321">
        </div>
      </div>
    </div>

    <!-- Discord -->
    <div class="channel-block" id="ch-discord">
      <div class="channel-header" onclick="toggleChannel('discord')">
        <span class="channel-icon">🎮</span>
        <span class="channel-name">Discord</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-discord-enabled" onchange="onChannelToggle('discord', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-discord-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-discord-body" style="display:none">
        <div class="form-group">
          <label class="form-label">Bot Token</label>
          <div class="input-eye">
            <input id="ch-discord-token" type="password" class="form-input" placeholder="你的 Discord Bot Token">
            <button class="eye-btn" onclick="toggleEye('ch-discord-token', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">允许的用户 ID <span class="form-hint">逗号分隔</span></label>
          <input id="ch-discord-allow" type="text" class="form-input" placeholder="123456789">
        </div>
      </div>
    </div>

    <!-- Slack -->
    <div class="channel-block" id="ch-slack">
      <div class="channel-header" onclick="toggleChannel('slack')">
        <span class="channel-icon">💬</span>
        <span class="channel-name">Slack</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-slack-enabled" onchange="onChannelToggle('slack', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-slack-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-slack-body" style="display:none">
        <div class="form-group">
          <label class="form-label">Bot Token <span class="form-hint">xoxb- 开头</span></label>
          <div class="input-eye">
            <input id="ch-slack-token" type="password" class="form-input" placeholder="xoxb-...">
            <button class="eye-btn" onclick="toggleEye('ch-slack-token', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">App-Level Token <span class="form-hint">xapp- 开头</span></label>
          <div class="input-eye">
            <input id="ch-slack-apptoken" type="password" class="form-input" placeholder="xapp-...">
            <button class="eye-btn" onclick="toggleEye('ch-slack-apptoken', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Feishu -->
    <div class="channel-block" id="ch-feishu">
      <div class="channel-header" onclick="toggleChannel('feishu')">
        <span class="channel-icon">🪶</span>
        <span class="channel-name">飞书 (Feishu)</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-feishu-enabled" onchange="onChannelToggle('feishu', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-feishu-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-feishu-body" style="display:none">
        <div class="form-group">
          <label class="form-label">App ID</label>
          <input id="ch-feishu-appid" type="text" class="form-input" placeholder="cli_...">
        </div>
        <div class="form-group">
          <label class="form-label">App Secret</label>
          <div class="input-eye">
            <input id="ch-feishu-secret" type="password" class="form-input" placeholder="App Secret">
            <button class="eye-btn" onclick="toggleEye('ch-feishu-secret', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Email -->
    <div class="channel-block" id="ch-email">
      <div class="channel-header" onclick="toggleChannel('email')">
        <span class="channel-icon">📧</span>
        <span class="channel-name">邮件 (Email)</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-email-enabled" onchange="onChannelToggle('email', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-email-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-email-body" style="display:none">
        <div class="form-group">
          <label class="form-label">IMAP 服务器</label>
          <input id="ch-email-imap" type="text" class="form-input" placeholder="imap.gmail.com">
        </div>
        <div class="form-group">
          <label class="form-label">SMTP 服务器</label>
          <input id="ch-email-smtp" type="text" class="form-input" placeholder="smtp.gmail.com">
        </div>
        <div class="form-group">
          <label class="form-label">邮箱地址</label>
          <input id="ch-email-addr" type="text" class="form-input" placeholder="you@gmail.com">
        </div>
        <div class="form-group">
          <label class="form-label">密码 / 授权码</label>
          <div class="input-eye">
            <input id="ch-email-pass" type="password" class="form-input" placeholder="应用专用密码">
            <button class="eye-btn" onclick="toggleEye('ch-email-pass', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
      </div>
    </div>

  </div>

  <!-- 区块③：高级设置 -->
  <div class="card">
    <div class="channel-header" onclick="toggleAdvanced()" style="cursor:pointer;margin-bottom:0">
      <span style="font-size:15px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.05em">高级设置</span>
      <span class="channel-arrow" id="adv-arrow">▶</span>
    </div>
    <div id="adv-body" style="display:none;margin-top:16px">
      <div class="form-group">
        <label class="form-label">工作区路径</label>
        <input id="cfg-workspace" type="text" class="form-input" placeholder="~/.pgflow/workspace">
      </div>
      <div class="form-group">
        <label class="form-label">网络代理 <span class="form-hint">留空不使用代理</span></label>
        <input id="cfg-proxy" type="text" class="form-input" placeholder="http://127.0.0.1:7890">
      </div>
      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;gap:10px">
          <label class="toggle">
            <input type="checkbox" id="cfg-exec-enable" checked>
            <span class="toggle-slider"></span>
          </label>
          允许执行终端命令
        </label>
      </div>
    </div>
  </div>

  <!-- 保存按钮 -->
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px">
    <button class="btn btn-primary" onclick="saveFormConfig()">💾 保存配置</button>
    <button class="btn btn-muted" onclick="loadFormConfig()">↺ 重新加载</button>
    <span class="save-msg" id="save-msg"></span>
  </div>

  <!-- 高级：原始 JSON 编辑（折叠） -->
  <div class="card">
    <div class="channel-header" onclick="toggleRawJson()" style="cursor:pointer;margin-bottom:0">
      <span style="font-size:13px;color:var(--muted)">🛠 高级：查看 / 编辑原始 JSON</span>
      <span class="channel-arrow" id="raw-arrow">▶</span>
    </div>
    <div id="raw-body" style="display:none;margin-top:16px">
      <p style="font-size:12px;color:var(--muted);margin-bottom:12px">直接修改 JSON 会覆盖上方表单的所有设置，请谨慎操作。</p>
      <textarea id="config-editor" spellcheck="false" style="width:100%;min-height:280px;background:#0a0c15;border:1px solid var(--border);border-radius:8px;padding:16px;font-size:12px;font-family:monospace;color:#a8b3cf;line-height:1.6;resize:vertical;outline:none"></textarea>
      <div style="display:flex;gap:8px;margin-top:12px;align-items:center">
        <button class="btn btn-primary" onclick="saveRawJson()">💾 保存 JSON</button>
        <button class="btn btn-muted" onclick="loadRawJson()">↺ 重新加载</button>
        <span class="save-msg" id="raw-save-msg"></span>
      </div>
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

<!-- DOCS TAB -->
<div id="tab-docs" class="tab">

  <!-- 平台导航 -->
  <div style="display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap">
    <button class="btn btn-primary" onclick="scrollToDoc('doc-win')">🪟 Windows</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-mac')">🍎 macOS</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-linux')">🐧 Linux 桌面</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-vps')">☁️ VPS 服务器</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-telegram')">✈️ 连接 Telegram</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-providers')">🤖 AI 服务商</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-workspace')">📁 工作区文件</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-faq')">❓ 常见问题</button>
  </div>

  <div class="card">

    <!-- ── Windows ── -->
    <div class="doc-section" id="doc-win">
      <h3>🪟 Windows 使用说明</h3>
      <p>Windows 是 PgFlow 的主要支持平台，提供完整的图形化体验，无需任何命令行操作。</p>

      <p><strong>安装步骤</strong></p>
      <ol>
        <li>下载最新版 <span class="doc-code">pgflow-windows.zip</span>，解压到任意位置（如桌面）</li>
        <li>解压后得到 <span class="doc-code">pgflow/</span> 文件夹，<strong>不要移动或删除其中的 <span class="doc-code">_internal/</span> 子文件夹</strong>，否则程序无法启动</li>
        <li>双击 <span class="doc-code">pgflow.exe</span>，系统托盘右下角会出现 🌊 图标，浏览器自动打开管理面板</li>
      </ol>

      <p><strong>首次配置</strong></p>
      <ol>
        <li>面板顶部点击「配置」，填写 AI 服务商和 API Key，开启 Telegram 渠道并填写 Bot Token</li>
        <li>点击「保存配置」</li>
        <li>右键托盘图标 → <strong>重启服务</strong>，配置生效</li>
        <li>向 Telegram Bot 发送消息测试</li>
      </ol>

      <p><strong>日常使用</strong></p>
      <table class="doc-table">
        <thead><tr><th>操作</th><th>方法</th></tr></thead>
        <tbody>
          <tr><td>启动 PgFlow</td><td>双击 pgflow.exe，或开机自启后自动运行</td></tr>
          <tr><td>开机自启</td><td>右键托盘图标 → 开机自启（打勾启用）</td></tr>
          <tr><td>修改配置</td><td>面板「配置」Tab 修改 → 保存 → 右键托盘重启服务</td></tr>
          <tr><td>查看日志</td><td>右键托盘图标 → 查看日志</td></tr>
          <tr><td>退出程序</td><td>右键托盘图标 → 退出</td></tr>
        </tbody>
      </table>
      <div class="doc-warn">⚠️ 部分杀毒软件（如 Windows Defender）可能误报 pgflow.exe 为威胁。这是 PyInstaller 打包程序的常见误报，并非病毒。请将 <span class="doc-code">pgflow/</span> 文件夹添加到杀毒软件的排除列表即可。</div>
    </div>

    <!-- ── macOS ── -->
    <div class="doc-section" id="doc-mac">
      <h3>🍎 macOS 使用说明</h3>
      <p>macOS 版本通过命令行启动，面板功能与 Windows 完全一致，可在浏览器中完成所有配置。</p>

      <p><strong>安装步骤</strong></p>
      <ol>
        <li>确认已安装 Python 3.11 或更高版本。打开终端，运行：<br>
          <span class="doc-code">python3 --version</span><br>
          如果未安装，前往 <span class="doc-code">python.org</span> 下载安装
        </li>
        <li>下载源码包并解压，或通过终端克隆：<br>
          <span class="doc-code">git clone https://github.com/leoyangx/PgFlow.git</span>
        </li>
        <li>进入项目目录，安装依赖：<br>
          <span class="doc-code">cd PgFlow && pip3 install -e .</span>
        </li>
      </ol>

      <p><strong>启动方式</strong></p>
      <ol>
        <li>打开终端，运行以下命令启动网关（保持终端窗口开启）：<br>
          <span class="doc-code">pgflow gateway</span>
        </li>
        <li>另开一个终端窗口，打开管理面板：<br>
          <span class="doc-code">pgflow dashboard</span><br>
          或直接在浏览器访问 <span class="doc-code">http://localhost:18791</span>
        </li>
        <li>在面板「配置」Tab 完成 API Key 和渠道配置，保存后重新运行 <span class="doc-code">pgflow gateway</span></li>
      </ol>

      <p><strong>开机自启（可选）</strong></p>
      <p>在终端运行以下命令，创建 macOS 启动项：</p>
      <ol>
        <li>找到 pgflow 的完整路径：<span class="doc-code">which pgflow</span></li>
        <li>创建文件 <span class="doc-code">~/Library/LaunchAgents/ai.pgflow.gateway.plist</span>，内容参考项目文档</li>
        <li>运行 <span class="doc-code">launchctl load ~/Library/LaunchAgents/ai.pgflow.gateway.plist</span> 启用</li>
      </ol>
      <div class="doc-warn">⚠️ 首次运行时 macOS Gatekeeper 可能阻止程序。前往「系统设置 → 隐私与安全性」，点击「仍要打开」即可。</div>
    </div>

    <!-- ── Linux 桌面 ── -->
    <div class="doc-section" id="doc-linux">
      <h3>🐧 Linux 桌面使用说明</h3>
      <p>适用于 Ubuntu、Debian、Fedora 等带桌面环境的 Linux 系统。操作方式与 macOS 类似。</p>

      <p><strong>安装步骤</strong></p>
      <ol>
        <li>确认 Python 版本 ≥ 3.11：<span class="doc-code">python3 --version</span><br>
          Ubuntu 22.04 及以上已自带，旧版本需通过 <span class="doc-code">deadsnakes</span> PPA 安装
        </li>
        <li>克隆项目并安装：<br>
          <span class="doc-code">git clone https://github.com/leoyangx/PgFlow.git</span><br>
          <span class="doc-code">cd PgFlow && pip3 install -e .</span>
        </li>
      </ol>

      <p><strong>启动方式</strong></p>
      <ol>
        <li>启动网关（后台运行）：<br>
          <span class="doc-code">pgflow gateway &</span>
        </li>
        <li>浏览器访问面板：<span class="doc-code">http://localhost:18791</span></li>
        <li>在面板完成配置后，停止网关重新启动使配置生效：<br>
          <span class="doc-code">pkill -f "pgflow gateway" && pgflow gateway &</span>
        </li>
      </ol>

      <p><strong>开机自启（systemd）</strong></p>
      <ol>
        <li>创建服务文件 <span class="doc-code">/etc/systemd/system/pgflow.service</span>（需要 sudo）</li>
        <li>填写服务配置后运行：<br>
          <span class="doc-code">sudo systemctl enable pgflow && sudo systemctl start pgflow</span>
        </li>
      </ol>
      <div class="doc-tip">💡 GNOME 桌面默认不显示系统托盘，安装扩展 <span class="doc-code">gnome-shell-extension-appindicator</span> 可解决此问题。不使用托盘时，直接用命令行管理网关即可。</div>
    </div>

    <!-- ── VPS 服务器 ── -->
    <div class="doc-section" id="doc-vps">
      <h3>☁️ VPS 服务器使用说明</h3>
      <p>在无图形界面的云服务器（如阿里云、腾讯云、AWS）上运行 PgFlow，让 AI 助手 24 小时不间断在线，即使本地电脑关机也能正常响应。</p>

      <p><strong>系统要求</strong></p>
      <ul>
        <li>操作系统：Ubuntu 22.04 / Debian 11 或更高（推荐）</li>
        <li>Python 3.11+</li>
        <li>内存：512MB 以上（推荐 1GB）</li>
        <li>不需要图形界面，纯命令行操作</li>
      </ul>

      <p><strong>安装步骤</strong></p>
      <ol>
        <li>SSH 连接到服务器，安装 Python 和 git：<br>
          <span class="doc-code">sudo apt update && sudo apt install -y python3.11 python3-pip git</span>
        </li>
        <li>克隆项目并安装依赖：<br>
          <span class="doc-code">git clone https://github.com/leoyangx/PgFlow.git && cd PgFlow</span><br>
          <span class="doc-code">pip3 install -e .</span>
        </li>
        <li>首次配置（通过命令行向导）：<br>
          <span class="doc-code">pgflow onboard --wizard</span><br>
          按提示填写 API Key 和 Telegram Token
        </li>
      </ol>

      <p><strong>后台持久运行（推荐用 screen 或 tmux）</strong></p>
      <ol>
        <li>安装 screen：<span class="doc-code">sudo apt install -y screen</span></li>
        <li>创建后台会话：<span class="doc-code">screen -S pgflow</span></li>
        <li>启动网关：<span class="doc-code">pgflow gateway</span></li>
        <li>按 <span class="doc-code">Ctrl+A</span> 然后 <span class="doc-code">D</span> 将会话挂到后台，SSH 断开后网关继续运行</li>
        <li>下次 SSH 登录后，用 <span class="doc-code">screen -r pgflow</span> 重新连接查看状态</li>
      </ol>

      <p><strong>开机自启（systemd 服务）</strong></p>
      <ol>
        <li>创建服务文件：<br>
          <span class="doc-code">sudo nano /etc/systemd/system/pgflow.service</span>
        </li>
        <li>填入以下内容（将 <span class="doc-code">YOUR_USER</span> 替换为你的用户名）：
          <pre style="margin:8px 0;font-size:12px">[Unit]
Description=PgFlow Gateway
After=network.target

[Service]
Type=simple
User=YOUR_USER
ExecStart=/usr/local/bin/pgflow gateway
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target</pre>
        </li>
        <li>启用并启动：<br>
          <span class="doc-code">sudo systemctl daemon-reload</span><br>
          <span class="doc-code">sudo systemctl enable pgflow</span><br>
          <span class="doc-code">sudo systemctl start pgflow</span>
        </li>
        <li>查看运行状态：<span class="doc-code">sudo systemctl status pgflow</span></li>
      </ol>

      <p><strong>远程访问管理面板</strong></p>
      <p>VPS 上的面板默认只监听本地（127.0.0.1:18791），有两种方式远程访问：</p>
      <ul>
        <li><strong>SSH 端口转发（推荐，更安全）：</strong><br>
          本地终端运行：<span class="doc-code">ssh -L 18791:127.0.0.1:18791 user@你的服务器IP</span><br>
          然后本地浏览器访问 <span class="doc-code">http://localhost:18791</span>
        </li>
        <li><strong>修改配置开放端口（不推荐，有安全风险）：</strong><br>
          在配置中将 gateway host 改为 <span class="doc-code">0.0.0.0</span> 并在防火墙放行 18791 端口
        </li>
      </ul>
      <div class="doc-warn">⚠️ 不建议将管理面板直接暴露到公网，面板目前没有登录验证，任何人都可以访问和修改配置。使用 SSH 端口转发是最安全的远程访问方式。</div>
    </div>

    <!-- ── Telegram ── -->
    <div class="doc-section" id="doc-telegram">
      <h3>✈️ 连接 Telegram</h3>
      <ol>
        <li>在 Telegram 搜索 <span class="doc-code">@BotFather</span>，发送 <span class="doc-code">/newbot</span></li>
        <li>按提示输入 Bot 名称，BotFather 返回 Token，格式类似 <span class="doc-code">123456:ABC-DEF1234...</span></li>
        <li>搜索 <span class="doc-code">@userinfobot</span>，发送任意消息，获取你自己的用户 ID（纯数字）</li>
        <li>在「配置」→「聊天渠道」→「Telegram」中填入 Token 和用户 ID，开启开关并保存</li>
        <li>重启网关后，向 Bot 发送 <span class="doc-code">/start</span> 测试</li>
      </ol>
      <div class="doc-tip">💡 <strong>allowFrom（允许的用户 ID）</strong>：填入你自己的 ID 确保只有你能使用；留空则拒绝所有人；填 <span class="doc-code">*</span> 允许所有人（不推荐）</div>
    </div>

    <!-- ── AI 服务商 ── -->
    <div class="doc-section" id="doc-providers">
      <h3>🤖 推荐的 AI 服务商</h3>
      <table class="doc-table">
        <thead><tr><th>服务商</th><th>特点</th><th>注册地址</th></tr></thead>
        <tbody>
          <tr><td>OpenRouter</td><td>聚合平台，一个 Key 用所有模型，按量计费，新用户有免费额度</td><td>openrouter.ai</td></tr>
          <tr><td>Anthropic</td><td>Claude 官方，能力最强，需海外信用卡</td><td>console.anthropic.com</td></tr>
          <tr><td>DeepSeek</td><td>国内直连，中文极强，价格极低，推荐国内用户</td><td>platform.deepseek.com</td></tr>
          <tr><td>硅基流动</td><td>国内聚合平台，支持 DeepSeek/Qwen 等，有免费额度</td><td>siliconflow.cn</td></tr>
          <tr><td>智谱 AI</td><td>GLM 系列，国内直连，注册即送免费额度</td><td>open.bigmodel.cn</td></tr>
          <tr><td>阿里云百炼</td><td>Qwen 系列，国内稳定，企业级支持</td><td>bailian.aliyun.com</td></tr>
        </tbody>
      </table>
      <div class="doc-tip">💡 模型名称格式：OpenRouter 用 <span class="doc-code">anthropic/claude-opus-4-5</span>，DeepSeek 直连用 <span class="doc-code">deepseek-chat</span>，硅基流动用 <span class="doc-code">deepseek-ai/DeepSeek-V3</span></div>
    </div>

    <!-- ── 工作区文件 ── -->
    <div class="doc-section" id="doc-workspace">
      <h3>📁 工作区文件说明</h3>
      <p>工作区默认在 <span class="doc-code">~/.pgflow/workspace/</span>，直接用文本编辑器修改这些文件即可自定义 AI 行为，<strong>无需重启</strong>，下次对话自动生效：</p>
      <table class="doc-table">
        <thead><tr><th>文件</th><th>作用</th><th>示例内容</th></tr></thead>
        <tbody>
          <tr><td>SOUL.md</td><td>AI 人格设定</td><td>你叫小助手，说话简洁友好，始终用中文回复</td></tr>
          <tr><td>USER.md</td><td>你的个人信息</td><td>我是一名设计师，常用 Mac，偏好简洁的回答</td></tr>
          <tr><td>MEMORY.md</td><td>AI 的长期记忆，自动维护</td><td>AI 会自动更新，无需手动编辑</td></tr>
          <tr><td>HEARTBEAT.md</td><td>定时任务</td><td>每天早上 9 点发送天气和日程提醒</td></tr>
          <tr><td>skills/</td><td>技能包目录</td><td>每个子文件夹放一个 SKILL.md 即可扩展功能</td></tr>
        </tbody>
      </table>
    </div>

    <!-- ── 常见问题 ── -->
    <div class="doc-section" id="doc-faq">
      <h3>❓ 常见问题</h3>
      <div class="doc-tip"><strong>Q：Bot 没有响应怎么办？</strong><br>
        1. 面板「状态」Tab 确认网关显示「运行中」<br>
        2. 检查 API Key 是否正确且账户有余额<br>
        3. 检查 Telegram Token 是否正确，allowFrom 是否包含你的用户 ID<br>
        4. 查看日志（Windows：右键托盘→查看日志；其他系统：查看终端输出）
      </div>
      <div class="doc-tip"><strong>Q：修改配置后不生效？</strong><br>
        保存配置后必须重启网关才能生效。Windows 右键托盘→重启服务；其他系统停止再重新运行 <span class="doc-code">pgflow gateway</span>。
      </div>
      <div class="doc-tip"><strong>Q：如何让 AI 说中文 / 改变回复风格？</strong><br>
        编辑工作区的 <span class="doc-code">SOUL.md</span>，写入你希望的风格描述，例如「始终用中文回复，语气简洁」，下次对话自动生效。
      </div>
      <div class="doc-tip"><strong>Q：Windows 杀毒软件误报？</strong><br>
        将 <span class="doc-code">pgflow/</span> 文件夹添加到杀毒软件排除列表即可，这是 PyInstaller 程序的常见误报。
      </div>
      <div class="doc-tip"><strong>Q：如何更新到新版本？</strong><br>
        Windows：下载新的 zip 包解压覆盖旧文件夹，保留原有的配置（配置存储在 <span class="doc-code">~/.pgflow/</span>，不在程序文件夹内，不会丢失）。<br>
        其他系统：进入项目目录运行 <span class="doc-code">git pull && pip3 install -e .</span>
      </div>
    </div>

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

function scrollToDoc(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({behavior: 'smooth', block: 'start'});
}

function show(name, btn) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
  if (name === 'status') loadStatus();
  if (name === 'skills') loadSkills();
  if (name === 'config') loadFormConfig();
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

// ── Config Form ─────────────────────────────────────────────────────────────

// 渠道展开/收起
function toggleChannel(name) {
  const body  = document.getElementById('ch-' + name + '-body');
  const arrow = document.getElementById('ch-' + name + '-arrow');
  const open  = body.style.display === 'none';
  body.style.display  = open ? 'block' : 'none';
  arrow.classList.toggle('open', open);
}

// 启用渠道时自动展开
function onChannelToggle(name, checked) {
  const body  = document.getElementById('ch-' + name + '-body');
  const arrow = document.getElementById('ch-' + name + '-arrow');
  if (checked) {
    body.style.display = 'block';
    arrow.classList.add('open');
  }
}

// 切换 API Key 显示
function toggleEye(id, btn) {
  const inp = document.getElementById(id);
  inp.type = inp.type === 'password' ? 'text' : 'password';
  btn.textContent = inp.type === 'password' ? '👁' : '🙈';
}

// 自定义接口时显示 Base URL 输入框
function onProviderChange() {
  const v = document.getElementById('cfg-provider').value;
  document.getElementById('custom-base-group').style.display = v === 'custom' ? 'block' : 'none';
}

// 高级设置折叠
function toggleAdvanced() {
  const body  = document.getElementById('adv-body');
  const arrow = document.getElementById('adv-arrow');
  const open  = body.style.display === 'none';
  body.style.display = open ? 'block' : 'none';
  arrow.classList.toggle('open', open);
}

// 原始 JSON 折叠
function toggleRawJson() {
  const body  = document.getElementById('raw-body');
  const arrow = document.getElementById('raw-arrow');
  const open  = body.style.display === 'none';
  body.style.display = open ? 'block' : 'none';
  arrow.classList.toggle('open', open);
  if (open) loadRawJson();
}

// 把 allowFrom 数组转成逗号字符串
function allowToStr(arr) {
  if (!arr || arr.length === 0) return '';
  return arr.join(', ');
}
// 把逗号字符串转回数组
function strToAllow(s) {
  return s.split(',').map(x => x.trim()).filter(Boolean);
}

// 从 config JSON 填充表单
function fillForm(cfg) {
  // ① AI 模型
  const providers = cfg.providers || {};
  const agentDef  = (cfg.agents || {}).defaults || {};

  // 判断当前使用的 provider
  const providerNames = ['openrouter','anthropic','openai','deepseek','gemini',
    'zhipu','dashscope','siliconflow','volcengine','moonshot','groq'];
  let activeProvider = 'custom';
  let activeApiKey   = '';
  let activeApiBase  = '';
  for (const name of providerNames) {
    const p = providers[name] || {};
    if (p.apiKey) { activeProvider = name; activeApiKey = p.apiKey; activeApiBase = p.apiBase || ''; break; }
  }
  if (activeProvider === 'custom') {
    const p = providers.custom || {};
    activeApiKey  = p.apiKey  || '';
    activeApiBase = p.apiBase || '';
  }

  const sel = document.getElementById('cfg-provider');
  for (const opt of sel.options) { if (opt.value === activeProvider) { sel.value = activeProvider; break; } }
  document.getElementById('cfg-apikey').value   = activeApiKey;
  document.getElementById('cfg-apibase').value  = activeApiBase;
  document.getElementById('cfg-model').value    = agentDef.model || '';
  document.getElementById('custom-base-group').style.display = activeProvider === 'custom' ? 'block' : 'none';

  // ② 渠道
  const channels = cfg.channels || {};
  const chMap = {
    telegram: { enabled: 'ch-telegram-enabled', token: 'ch-telegram-token', allow: 'ch-telegram-allow' },
    discord:  { enabled: 'ch-discord-enabled',  token: 'ch-discord-token',  allow: 'ch-discord-allow'  },
    slack:    { enabled: 'ch-slack-enabled',     token: 'ch-slack-token'  },
    feishu:   { enabled: 'ch-feishu-enabled'   },
    email:    { enabled: 'ch-email-enabled'    },
  };
  // telegram
  { const c = channels.telegram || {};
    document.getElementById('ch-telegram-enabled').checked = !!c.enabled;
    document.getElementById('ch-telegram-token').value     = c.token || '';
    document.getElementById('ch-telegram-allow').value     = allowToStr(c.allowFrom); }
  // discord
  { const c = channels.discord || {};
    document.getElementById('ch-discord-enabled').checked = !!c.enabled;
    document.getElementById('ch-discord-token').value     = c.token || '';
    document.getElementById('ch-discord-allow').value     = allowToStr(c.allowFrom); }
  // slack
  { const c = channels.slack || {};
    document.getElementById('ch-slack-enabled').checked   = !!c.enabled;
    document.getElementById('ch-slack-token').value       = c.botToken || c.token || '';
    document.getElementById('ch-slack-apptoken').value    = c.appToken || ''; }
  // feishu
  { const c = channels.feishu || {};
    document.getElementById('ch-feishu-enabled').checked  = !!c.enabled;
    document.getElementById('ch-feishu-appid').value      = c.appId || '';
    document.getElementById('ch-feishu-secret').value     = c.appSecret || ''; }
  // email
  { const c = channels.email || {};
    document.getElementById('ch-email-enabled').checked   = !!c.enabled;
    document.getElementById('ch-email-imap').value        = c.imapHost || '';
    document.getElementById('ch-email-smtp').value        = c.smtpHost || '';
    document.getElementById('ch-email-addr').value        = c.email || c.address || '';
    document.getElementById('ch-email-pass').value        = c.password || ''; }

  // ③ 高级
  const tools = cfg.tools || {};
  document.getElementById('cfg-workspace').value      = agentDef.workspace || '';
  document.getElementById('cfg-proxy').value          = (tools.web || {}).proxy || '';
  document.getElementById('cfg-exec-enable').checked  = (tools.exec || {}).enable !== false;
}

// 从表单收集，合并回原始 cfg 对象（保留未展示的字段）
function collectForm(cfg) {
  cfg = JSON.parse(JSON.stringify(cfg)); // deep clone

  // ① AI 模型
  const provider = document.getElementById('cfg-provider').value;
  const apiKey   = document.getElementById('cfg-apikey').value.trim();
  const apiBase  = document.getElementById('cfg-apibase').value.trim();
  const model    = document.getElementById('cfg-model').value.trim();

  if (!cfg.providers) cfg.providers = {};
  // 清除其他 provider 的 apiKey（避免多个同时生效产生歧义），保留 apiBase
  const knownProviders = ['openrouter','anthropic','openai','deepseek','gemini',
    'zhipu','dashscope','siliconflow','volcengine','moonshot','groq','custom'];
  for (const name of knownProviders) {
    if (cfg.providers[name] && cfg.providers[name].apiKey && name !== provider) {
      // 只置空 apiKey，保留其他字段
      cfg.providers[name].apiKey = '';
    }
  }
  if (!cfg.providers[provider]) cfg.providers[provider] = {};
  cfg.providers[provider].apiKey = apiKey;
  if (provider === 'custom' && apiBase) cfg.providers[provider].apiBase = apiBase;

  if (!cfg.agents) cfg.agents = {};
  if (!cfg.agents.defaults) cfg.agents.defaults = {};
  if (model) cfg.agents.defaults.model = model;

  // ② 渠道
  if (!cfg.channels) cfg.channels = {};
  // telegram
  { const enabled = document.getElementById('ch-telegram-enabled').checked;
    const token   = document.getElementById('ch-telegram-token').value.trim();
    const allow   = strToAllow(document.getElementById('ch-telegram-allow').value);
    if (!cfg.channels.telegram) cfg.channels.telegram = {};
    cfg.channels.telegram.enabled   = enabled;
    if (token) cfg.channels.telegram.token     = token;
    cfg.channels.telegram.allowFrom = allow; }
  // discord
  { const enabled = document.getElementById('ch-discord-enabled').checked;
    const token   = document.getElementById('ch-discord-token').value.trim();
    const allow   = strToAllow(document.getElementById('ch-discord-allow').value);
    if (!cfg.channels.discord) cfg.channels.discord = {};
    cfg.channels.discord.enabled   = enabled;
    if (token) cfg.channels.discord.token     = token;
    cfg.channels.discord.allowFrom = allow; }
  // slack
  { const enabled  = document.getElementById('ch-slack-enabled').checked;
    const token    = document.getElementById('ch-slack-token').value.trim();
    const appToken = document.getElementById('ch-slack-apptoken').value.trim();
    if (!cfg.channels.slack) cfg.channels.slack = {};
    cfg.channels.slack.enabled = enabled;
    if (token)    cfg.channels.slack.botToken = token;
    if (appToken) cfg.channels.slack.appToken = appToken; }
  // feishu
  { const enabled = document.getElementById('ch-feishu-enabled').checked;
    const appId   = document.getElementById('ch-feishu-appid').value.trim();
    const secret  = document.getElementById('ch-feishu-secret').value.trim();
    if (!cfg.channels.feishu) cfg.channels.feishu = {};
    cfg.channels.feishu.enabled = enabled;
    if (appId)  cfg.channels.feishu.appId     = appId;
    if (secret) cfg.channels.feishu.appSecret = secret; }
  // email
  { const enabled = document.getElementById('ch-email-enabled').checked;
    const imap    = document.getElementById('ch-email-imap').value.trim();
    const smtp    = document.getElementById('ch-email-smtp').value.trim();
    const addr    = document.getElementById('ch-email-addr').value.trim();
    const pass    = document.getElementById('ch-email-pass').value.trim();
    if (!cfg.channels.email) cfg.channels.email = {};
    cfg.channels.email.enabled = enabled;
    if (imap) cfg.channels.email.imapHost = imap;
    if (smtp) cfg.channels.email.smtpHost = smtp;
    if (addr) cfg.channels.email.email    = addr;
    if (pass) cfg.channels.email.password = pass; }

  // ③ 高级
  const workspace = document.getElementById('cfg-workspace').value.trim();
  const proxy     = document.getElementById('cfg-proxy').value.trim();
  const execEn    = document.getElementById('cfg-exec-enable').checked;
  if (workspace) cfg.agents.defaults.workspace = workspace;
  if (!cfg.tools) cfg.tools = {};
  if (!cfg.tools.web) cfg.tools.web = {};
  cfg.tools.web.proxy = proxy || null;
  if (!cfg.tools.exec) cfg.tools.exec = {};
  cfg.tools.exec.enable = execEn;

  return cfg;
}

let _rawCfg = {};  // 最近一次从服务端读取的完整 cfg 对象

async function loadFormConfig() {
  const msg = document.getElementById('save-msg');
  msg.textContent = '';
  try {
    const d = await api('/api/config/raw');
    _rawCfg = d.raw ? JSON.parse(d.raw) : {};
    fillForm(_rawCfg);
  } catch(e) {
    msg.className = 'save-msg err';
    msg.textContent = '❌ 读取配置失败';
  }
}

async function saveFormConfig() {
  const msg = document.getElementById('save-msg');
  msg.textContent = '';
  try {
    const merged = collectForm(_rawCfg);
    const raw    = JSON.stringify(merged, null, 2);
    const r = await api('/api/config/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({raw}),
    });
    if (r.ok) {
      _rawCfg = merged;
      msg.className = 'save-msg ok';
      msg.textContent = '✓ 已保存';
      setTimeout(() => { msg.textContent = ''; }, 3000);
    } else {
      msg.className = 'save-msg err';
      msg.textContent = '❌ ' + (r.error || '保存失败');
    }
  } catch(e) {
    msg.className = 'save-msg err';
    msg.textContent = '❌ ' + e.message;
  }
}

// ── Raw JSON editor ─────────────────────────────────────────────────────────
async function loadRawJson() {
  const ta = document.getElementById('config-editor');
  try {
    const d = await api('/api/config/raw');
    ta.value = d.raw || '';
  } catch(e) {
    ta.value = '读取失败';
  }
}

async function saveRawJson() {
  const ta  = document.getElementById('config-editor');
  const msg = document.getElementById('raw-save-msg');
  msg.textContent = '';
  try { JSON.parse(ta.value); } catch(e) {
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
      _rawCfg = JSON.parse(ta.value);
      fillForm(_rawCfg);
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
    """Detect a running gateway process by scanning running processes.

    Looks for any pgflow.exe (or pgflow) process whose command line
    contains the word 'gateway'. Works regardless of how it was started.
    """
    import sys
    import subprocess
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-WmiObject Win32_Process | Where-Object { "
                 "$_.Name -like 'pgflow*' -and $_.CommandLine -like '*gateway*' "
                 "} | Measure-Object | Select-Object -ExpandProperty Count"],
                capture_output=True, text=True, timeout=3,
                creationflags=0x08000000,
            )
            count = result.stdout.strip()
            return count.isdigit() and int(count) > 0
        else:
            result = subprocess.run(
                ["pgrep", "-f", "pgflow.*gateway"],
                capture_output=True, timeout=2,
            )
            return result.returncode == 0
    except Exception:
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
