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

_HTML = r"""<!DOCTYPE html>
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

  <!-- 已连接渠道 -->
  <div class="card">
    <h2>已启用渠道</h2>
    <div id="channel-status-rows"><div class="empty">加载中…</div></div>
  </div>

  <div class="card">
    <h2>工作区</h2>
    <div id="workspace-rows"><div class="empty">加载中…</div></div>
  </div>

  <!-- 版本信息 -->
  <div class="card" id="version-card">
    <h2>版本信息</h2>
    <div class="row">
      <label>当前版本</label>
      <span id="ver-current"><span class="badge gray">检测中…</span></span>
    </div>
    <div class="row">
      <label>最新版本</label>
      <span id="ver-latest"><span class="badge gray">检测中…</span></span>
    </div>
    <div id="ver-update-row" class="row" style="display:none">
      <label>新版提示</label>
      <a id="ver-update-link" href="#" target="_blank" class="btn btn-green" style="text-decoration:none;font-size:13px">⬇ 下载新版本</a>
    </div>
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
        <option value="openrouter">OpenRouter（推荐，支持 Claude/GPT/Gemini 等所有模型）</option>
        <option value="deepseek">DeepSeek（国内直连，价格极低）</option>
        <option value="siliconflow">硅基流动 SiliconFlow（国内，有免费额度）</option>
        <option value="zhipu">智谱 AI（GLM 系列，国内直连）</option>
        <option value="dashscope">阿里云百炼 DashScope（Qwen 系列）</option>
        <option value="moonshot">Moonshot 月之暗面</option>
        <option value="volcengine">火山引擎（豆包）</option>
        <option value="anthropic">Anthropic（Claude 官方）</option>
        <option value="openai">OpenAI（GPT 系列）</option>
        <option value="gemini">Google Gemini</option>
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
    <div class="form-group" id="apibase-group" style="display:none">
      <label class="form-label">API Base URL <span class="form-hint" id="apibase-hint"></span></label>
      <input id="cfg-apibase" type="text" class="form-input" placeholder="https://api.example.com/v1">
    </div>
    <div class="form-group">
      <label class="form-label">模型名称 <span class="form-hint">只填模型名，例如 deepseek-chat，不要填 URL</span></label>
      <input id="cfg-model" type="text" class="form-input" placeholder="选择服务商后自动填入推荐模型">
      <div id="model-hint" style="font-size:11px;color:var(--muted);margin-top:4px"></div>
    </div>
  </div>

  <!-- 区块②：聊天渠道 -->
  <div class="card">
    <h2>聊天渠道</h2>
    <p style="font-size:12px;color:var(--muted);margin-bottom:16px">启用开关后填写对应凭据，保存并重启服务即生效。</p>

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
        <div class="doc-tip" style="margin-bottom:12px">向 <strong>@BotFather</strong> 发送 /newbot 创建机器人，获取 Token。向 <strong>@userinfobot</strong> 获取你的用户 ID。</div>
        <div class="form-group">
          <label class="form-label">Bot Token <span class="form-hint">向 @BotFather 获取</span></label>
          <div class="input-eye">
            <input id="ch-telegram-token" type="password" class="form-input" placeholder="123456:ABC-DEF...">
            <button class="eye-btn" onclick="toggleEye('ch-telegram-token', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">允许的用户 ID <span class="form-hint">逗号分隔；留空拒绝所有人；填 * 允许所有人</span></label>
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
        <div class="doc-tip" style="margin-bottom:12px">在 Discord 开发者平台创建应用，启用 <strong>Message Content Intent</strong> 权限，复制 Bot Token。</div>
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

    <!-- 飞书 -->
    <div class="channel-block" id="ch-feishu">
      <div class="channel-header" onclick="toggleChannel('feishu')">
        <span class="channel-icon">🪶</span>
        <span class="channel-name">飞书 Feishu</span>
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

    <!-- 钉钉 -->
    <div class="channel-block" id="ch-dingtalk">
      <div class="channel-header" onclick="toggleChannel('dingtalk')">
        <span class="channel-icon">📎</span>
        <span class="channel-name">钉钉 DingTalk</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-dingtalk-enabled" onchange="onChannelToggle('dingtalk', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-dingtalk-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-dingtalk-body" style="display:none">
        <div class="doc-tip" style="margin-bottom:12px">在钉钉开放平台创建企业内部应用，获取 Client ID 和 Client Secret。</div>
        <div class="form-group">
          <label class="form-label">Client ID <span class="form-hint">即 App Key</span></label>
          <input id="ch-dingtalk-clientid" type="text" class="form-input" placeholder="ding...">
        </div>
        <div class="form-group">
          <label class="form-label">Client Secret <span class="form-hint">即 App Secret</span></label>
          <div class="input-eye">
            <input id="ch-dingtalk-secret" type="password" class="form-input" placeholder="Client Secret">
            <button class="eye-btn" onclick="toggleEye('ch-dingtalk-secret', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
      </div>
    </div>

    <!-- QQ -->
    <div class="channel-block" id="ch-qq">
      <div class="channel-header" onclick="toggleChannel('qq')">
        <span class="channel-icon">🐧</span>
        <span class="channel-name">QQ</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-qq-enabled" onchange="onChannelToggle('qq', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-qq-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-qq-body" style="display:none">
        <div class="doc-tip" style="margin-bottom:12px">在 QQ 开放平台注册机器人，获取 App ID 和 App Secret。</div>
        <div class="form-group">
          <label class="form-label">App ID</label>
          <input id="ch-qq-appid" type="text" class="form-input" placeholder="你的 QQ App ID">
        </div>
        <div class="form-group">
          <label class="form-label">App Secret</label>
          <div class="input-eye">
            <input id="ch-qq-secret" type="password" class="form-input" placeholder="你的 QQ App Secret">
            <button class="eye-btn" onclick="toggleEye('ch-qq-secret', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 企业微信 -->
    <div class="channel-block" id="ch-wecom">
      <div class="channel-header" onclick="toggleChannel('wecom')">
        <span class="channel-icon">💼</span>
        <span class="channel-name">企业微信 Wecom</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-wecom-enabled" onchange="onChannelToggle('wecom', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-wecom-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-wecom-body" style="display:none">
        <div class="form-group">
          <label class="form-label">Corp ID <span class="form-hint">企业 ID</span></label>
          <input id="ch-wecom-corpid" type="text" class="form-input" placeholder="ww...">
        </div>
        <div class="form-group">
          <label class="form-label">Corp Secret</label>
          <div class="input-eye">
            <input id="ch-wecom-secret" type="password" class="form-input" placeholder="Corp Secret">
            <button class="eye-btn" onclick="toggleEye('ch-wecom-secret', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Agent ID</label>
          <input id="ch-wecom-agentid" type="text" class="form-input" placeholder="1000001">
        </div>
      </div>
    </div>

    <!-- Matrix -->
    <div class="channel-block" id="ch-matrix">
      <div class="channel-header" onclick="toggleChannel('matrix')">
        <span class="channel-icon">🔷</span>
        <span class="channel-name">Matrix</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-matrix-enabled" onchange="onChannelToggle('matrix', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-matrix-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-matrix-body" style="display:none">
        <div class="form-group">
          <label class="form-label">Homeserver URL</label>
          <input id="ch-matrix-homeserver" type="text" class="form-input" placeholder="https://matrix.org">
        </div>
        <div class="form-group">
          <label class="form-label">Access Token</label>
          <div class="input-eye">
            <input id="ch-matrix-token" type="password" class="form-input" placeholder="syt_...">
            <button class="eye-btn" onclick="toggleEye('ch-matrix-token', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
      </div>
    </div>

    <!-- WhatsApp -->
    <div class="channel-block" id="ch-whatsapp">
      <div class="channel-header" onclick="toggleChannel('whatsapp')">
        <span class="channel-icon">📱</span>
        <span class="channel-name">WhatsApp</span>
        <label class="toggle" onclick="event.stopPropagation()" title="启用/禁用">
          <input type="checkbox" id="ch-whatsapp-enabled" onchange="onChannelToggle('whatsapp', this.checked)">
          <span class="toggle-slider"></span>
        </label>
        <span class="channel-arrow" id="ch-whatsapp-arrow">▶</span>
      </div>
      <div class="channel-body" id="ch-whatsapp-body" style="display:none">
        <div class="doc-warn" style="margin-bottom:12px">⚠️ WhatsApp 渠道需要安装 Node.js 并运行桥接服务，详见文档「WhatsApp」章节。</div>
        <div class="form-group">
          <label class="form-label">Bridge URL <span class="form-hint">本地桥接服务地址</span></label>
          <input id="ch-whatsapp-url" type="text" class="form-input" placeholder="http://localhost:3000">
        </div>
      </div>
    </div>

    <!-- 邮件 -->
    <div class="channel-block" id="ch-email">
      <div class="channel-header" onclick="toggleChannel('email')">
        <span class="channel-icon">📧</span>
        <span class="channel-name">邮件 Email</span>
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
        <div class="doc-tip" style="margin-bottom:12px">在 Discord 开发者平台创建应用，启用 <strong>Message Content Intent</strong> 权限，复制 Bot Token。</div>
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

    <!-- 飞书 -->
    <div class="channel-block" id="ch-feishu">
      <div class="channel-header" onclick="toggleChannel('feishu')">
        <span class="channel-icon">🪶</span>
        <span class="channel-name">飞书 Feishu</span>
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

    <!-- 邮件 -->
    <div class="channel-block" id="ch-email">
      <div class="channel-header" onclick="toggleChannel('email')">
        <span class="channel-icon">📧</span>
        <span class="channel-name">邮件 Email</span>
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
      <div style="display:flex;align-items:center;gap:10px">
        <label style="display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted);font-weight:400;text-transform:none;letter-spacing:0">
          <label class="toggle">
            <input type="checkbox" id="log-auto-refresh" onchange="onLogAutoRefresh(this.checked)">
            <span class="toggle-slider"></span>
          </label>
          自动刷新
        </label>
        <button class="btn btn-muted" onclick="loadLogs()">↺ 刷新</button>
        <button class="btn btn-muted" onclick="scrollLogsToBottom()">⬇ 跳到底部</button>
      </div>
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
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-linux')">🐧 Linux</button>
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
      <p>Windows 版本提供完整的图形化体验，无需安装 Python，无需命令行，解压即用。</p>

      <p><strong>第一步：解压安装包</strong></p>
      <ol>
        <li>解压收到的 <span class="doc-code">pgflow-windows.zip</span>，得到 <span class="doc-code">pgflow/</span> 文件夹</li>
        <li>将整个 <span class="doc-code">pgflow/</span> 文件夹放到你想要的位置（如 D 盘根目录或桌面）</li>
        <li><strong>注意：</strong>文件夹内的 <span class="doc-code">_internal/</span> 子文件夹必须和 <span class="doc-code">pgflow.exe</span> 放在同一目录，不能单独移动 exe 文件</li>
      </ol>

      <p><strong>第二步：首次启动</strong></p>
      <ol>
        <li>双击 <span class="doc-code">pgflow.exe</span>，右下角任务栏会出现 🌊 图标，浏览器自动打开此管理面板</li>
        <li>如果弹出 Windows 安全提示「Windows 已保护你的电脑」，点击「更多信息」→「仍要运行」</li>
        <li>如果杀毒软件拦截，请将 <span class="doc-code">pgflow/</span> 文件夹加入白名单（排除列表），详见下方常见问题</li>
      </ol>

      <p><strong>第三步：完成配置</strong></p>
      <ol>
        <li>点击面板顶部「配置」Tab</li>
        <li>选择 AI 服务商，填写 API Key，保存</li>
        <li>展开「Telegram」渠道，填写 Bot Token 和你的用户 ID，开启开关，保存</li>
        <li>右键托盘图标 → <strong>重启服务</strong></li>
        <li>向 Telegram Bot 发送任意消息，验证是否正常响应</li>
      </ol>

      <p><strong>日常使用</strong></p>
      <table class="doc-table">
        <thead><tr><th>需求</th><th>操作</th></tr></thead>
        <tbody>
          <tr><td>开机自动启动</td><td>右键托盘图标 → 开机自启（打勾即启用，无需任何命令）</td></tr>
          <tr><td>修改配置</td><td>面板「配置」Tab 修改保存 → 右键托盘 → 重启服务</td></tr>
          <tr><td>查看运行日志</td><td>右键托盘图标 → 查看日志</td></tr>
          <tr><td>完全退出程序</td><td>右键托盘图标 → 退出</td></tr>
        </tbody>
      </table>
      <div class="doc-warn">⚠️ <strong>重要：</strong>修改配置保存后，必须右键托盘 → 重启服务，新配置才会生效。仅点保存不会自动重启。</div>
    </div>

    <!-- ── macOS ── -->
    <div class="doc-section" id="doc-mac">
      <h3>🍎 macOS 使用说明</h3>
      <p>macOS 版本以 <span class="doc-code">.dmg</span> 安装包形式分发，安装后通过系统托盘管理，体验与 Windows 基本一致。</p>

      <p><strong>第一步：安装</strong></p>
      <ol>
        <li>打开收到的 <span class="doc-code">PgFlow-macOS.dmg</span> 文件</li>
        <li>将 <span class="doc-code">PgFlow</span> 图标拖拽到「应用程序」文件夹</li>
        <li>在「应用程序」中找到 PgFlow，右键点击 → <strong>打开</strong>（首次必须右键打开，否则 macOS 会拒绝运行）</li>
        <li>弹出安全提示时，点击「打开」确认</li>
      </ol>

      <p><strong>第二步：完成配置</strong></p>
      <ol>
        <li>启动后浏览器自动打开管理面板，或访问 <span class="doc-code">http://localhost:18791</span></li>
        <li>点击「配置」Tab，填写 API Key 和 Telegram Bot Token，保存</li>
        <li>点击顶部菜单栏的 🌊 图标 → <strong>重启服务</strong></li>
        <li>向 Telegram Bot 发消息测试</li>
      </ol>

      <p><strong>日常使用</strong></p>
      <table class="doc-table">
        <thead><tr><th>需求</th><th>操作</th></tr></thead>
        <tbody>
          <tr><td>开机自动启动</td><td>菜单栏 🌊 图标 → 开机自启（打勾启用）</td></tr>
          <tr><td>打开管理面板</td><td>菜单栏 🌊 图标 → 打开管理面板</td></tr>
          <tr><td>修改配置后生效</td><td>保存配置 → 菜单栏 🌊 → 重启服务</td></tr>
          <tr><td>退出程序</td><td>菜单栏 🌊 图标 → 退出</td></tr>
        </tbody>
      </table>
      <div class="doc-tip">💡 macOS 14（Sonoma）及以上系统，首次运行时系统设置 → 隐私与安全性 → 底部会出现「仍要打开」按钮，点击即可。</div>
      <div class="doc-warn">⚠️ 当前 macOS 版暂不支持「开机自启」功能，此功能将在后续版本中提供。</div>
    </div>

    <!-- ── Linux ── -->
    <div class="doc-section" id="doc-linux">
      <h3>🐧 Linux 桌面使用说明</h3>
      <p>Linux 版本以压缩包形式分发，解压后直接运行可执行文件，通过浏览器访问管理面板完成所有配置。</p>

      <p><strong>第一步：解压安装</strong></p>
      <ol>
        <li>解压收到的 <span class="doc-code">pgflow-linux.tar.gz</span>：<br>
          <span class="doc-code">tar -xzf pgflow-linux.tar.gz</span>
        </li>
        <li>进入解压后的文件夹：<span class="doc-code">cd pgflow</span></li>
        <li>给可执行文件添加运行权限：<span class="doc-code">chmod +x pgflow</span></li>
      </ol>

      <p><strong>第二步：启动程序</strong></p>
      <ol>
        <li>在终端运行（保持窗口开启）：<span class="doc-code">./pgflow gateway</span></li>
        <li>浏览器访问管理面板：<span class="doc-code">http://localhost:18791</span></li>
        <li>在面板「配置」Tab 填写 API Key 和 Telegram Bot Token，保存</li>
        <li>在终端按 <span class="doc-code">Ctrl+C</span> 停止网关，再次运行 <span class="doc-code">./pgflow gateway</span> 使配置生效</li>
      </ol>

      <p><strong>后台持久运行（推荐）</strong></p>
      <ol>
        <li>安装 screen 工具：<span class="doc-code">sudo apt install screen</span></li>
        <li>创建后台会话：<span class="doc-code">screen -S pgflow</span></li>
        <li>启动网关：<span class="doc-code">./pgflow gateway</span></li>
        <li>按 <span class="doc-code">Ctrl+A</span> 再按 <span class="doc-code">D</span>，将程序放到后台，关闭终端窗口也不会停止</li>
        <li>下次查看状态：<span class="doc-code">screen -r pgflow</span></li>
      </ol>
      <div class="doc-tip">💡 GNOME 桌面默认不显示系统托盘区域，但管理面板（浏览器页面）功能完整，所有配置均可在面板中完成。</div>
      <div class="doc-warn">⚠️ 当前 Linux 版暂不支持图形托盘和开机自启，请使用上方后台运行方式长期运行。</div>
    </div>

    <!-- ── VPS 服务器 ── -->
    <div class="doc-section" id="doc-vps">
      <h3>☁️ VPS 服务器使用说明</h3>
      <p>将 PgFlow 部署到云服务器（如阿里云、腾讯云、AWS）后，即使本地电脑关机，AI 助手也能 24 小时在线响应。适合希望稳定运行、不依赖个人电脑的用户。</p>

      <p><strong>系统要求</strong></p>
      <ul>
        <li>操作系统：Ubuntu 22.04 / Debian 12（推荐）或其他 Linux 发行版</li>
        <li>内存：512MB 以上（推荐 1GB）</li>
        <li>需要有公网访问权限（能连接 Telegram、AI 服务商 API）</li>
      </ul>

      <p><strong>第一步：一键安装</strong></p>
      <p>SSH 登录服务器后，运行以下命令自动安装：</p>
      <div class="doc-code" style="display:block;padding:12px 16px;margin:8px 0;font-size:13px">bash &lt;(curl -fsSL https://raw.githubusercontent.com/leoyangx/PgFlow/main/install.sh)</div>
      <p style="font-size:12px;color:var(--muted)">安装脚本会自动安装 Python 依赖并完成配置。如果安装脚本还未发布，请联系我们获取安装包。</p>

      <p><strong>第二步：完成配置</strong></p>
      <ol>
        <li>安装完成后，运行配置向导：<span class="doc-code">pgflow onboard --wizard</span></li>
        <li>按提示依次填写：AI 服务商 API Key → Telegram Bot Token → 你的 Telegram 用户 ID</li>
        <li>配置完成后启动网关：<span class="doc-code">pgflow gateway</span></li>
      </ol>

      <p><strong>第三步：后台持久运行</strong></p>
      <ol>
        <li>使用 screen 保持后台运行（断开 SSH 也不停止）：<br>
          <span class="doc-code">screen -S pgflow</span> → 运行 <span class="doc-code">pgflow gateway</span> → 按 <span class="doc-code">Ctrl+A</span> 再按 <span class="doc-code">D</span>
        </li>
        <li>或设置为系统服务开机自启（推荐生产环境）：<br>
          <span class="doc-code">pgflow service install && pgflow service start</span>
        </li>
      </ol>

      <p><strong>远程访问管理面板</strong></p>
      <p>管理面板只监听本地地址，需要通过 SSH 隧道安全访问：</p>
      <ol>
        <li>在<strong>本地电脑</strong>打开终端，运行：<br>
          <span class="doc-code">ssh -L 18791:127.0.0.1:18791 root@你的服务器IP</span>
        </li>
        <li>保持该终端窗口开启，然后在浏览器访问：<span class="doc-code">http://localhost:18791</span></li>
      </ol>
      <div class="doc-warn">⚠️ 请勿将管理面板端口（18791）直接开放到公网，面板暂无登录验证，任何人都可访问。始终通过 SSH 隧道方式访问。</div>
    </div>

    <!-- ── Telegram ── -->
    <div class="doc-section" id="doc-telegram">
      <h3>✈️ 如何获取 Telegram Bot Token</h3>
      <ol>
        <li>打开 Telegram，搜索 <span class="doc-code">@BotFather</span>，点击进入并发送 <span class="doc-code">/newbot</span></li>
        <li>BotFather 会问你 Bot 的名字（显示名称，如「我的助手」）和用户名（必须以 bot 结尾，如 <span class="doc-code">myassistant_bot</span>）</li>
        <li>创建成功后，BotFather 会发给你一串 Token，格式类似：<br>
          <span class="doc-code">123456789:AABBccDDeeFFggHH...</span><br>
          <strong>复制这串 Token，填入配置页面的「Bot Token」栏</strong>
        </li>
        <li>获取你自己的 Telegram 用户 ID：搜索 <span class="doc-code">@userinfobot</span>，发送 <span class="doc-code">/start</span>，它会回复你的 ID（纯数字）</li>
        <li>将用户 ID 填入配置页的「允许的用户 ID」栏，保存后重启服务</li>
        <li>找到你刚创建的 Bot，发送 <span class="doc-code">/start</span> 开始使用</li>
      </ol>
      <div class="doc-tip">💡 「允许的用户 ID」决定谁可以和你的 Bot 对话：填入自己的 ID 表示只有你能用；如果你想分享给家人或朋友，把他们的 ID 也加进来（逗号分隔）</div>
    </div>

    <!-- ── AI 服务商 ── -->
    <div class="doc-section" id="doc-providers">
      <h3>🤖 推荐的 AI 服务商</h3>
      <p>PgFlow 需要接入 AI 大模型才能工作，你需要在以下任意一家服务商注册并获取 API Key：</p>
      <table class="doc-table">
        <thead><tr><th>服务商</th><th>推荐理由</th><th>适合人群</th><th>注册地址</th></tr></thead>
        <tbody>
          <tr><td>OpenRouter</td><td>一个 Key 用所有模型（Claude、GPT-4、Gemini 等），按量付费，新用户有免费额度</td><td>想尝试多种模型的用户</td><td>openrouter.ai</td></tr>
          <tr><td>DeepSeek</td><td>国内直连无需翻墙，中文理解极强，价格极低（约 OpenAI 的 1/10）</td><td>国内用户首选</td><td>platform.deepseek.com</td></tr>
          <tr><td>硅基流动</td><td>国内平台，支持 DeepSeek、Qwen 等多种模型，有免费额度</td><td>想免费试用的国内用户</td><td>siliconflow.cn</td></tr>
          <tr><td>智谱 AI</td><td>GLM 系列模型，国内直连，注册即送免费额度</td><td>国内用户</td><td>open.bigmodel.cn</td></tr>
          <tr><td>Anthropic</td><td>Claude 官方，效果最强，需要海外信用卡</td><td>有海外支付能力的用户</td><td>console.anthropic.com</td></tr>
        </tbody>
      </table>
      <div class="doc-tip">💡 <strong>推荐新用户选择 DeepSeek 或硅基流动</strong>：国内直连、价格低、注册简单，API Key 申请后几分钟即可开始使用。</div>
      <div class="doc-tip">💡 <strong>模型名称填写参考：</strong><br>
        · DeepSeek 直连：<span class="doc-code">deepseek-chat</span><br>
        · 硅基流动 DeepSeek：<span class="doc-code">deepseek-ai/DeepSeek-V3</span><br>
        · OpenRouter Claude：<span class="doc-code">anthropic/claude-opus-4-5</span>
      </div>
    </div>

    <!-- ── 工作区文件 ── -->
    <div class="doc-section" id="doc-workspace">
      <h3>📁 自定义你的 AI 助手</h3>
      <p>PgFlow 将你的个人配置保存在 <span class="doc-code">~/.pgflow/workspace/</span> 目录下（Windows 对应 <span class="doc-code">C:\Users\你的用户名\.pgflow\workspace\</span>）。用任意文本编辑器修改以下文件，即可定制 AI 的行为，<strong>无需重启，下次对话自动生效</strong>：</p>
      <table class="doc-table">
        <thead><tr><th>文件</th><th>作用</th><th>示例</th></tr></thead>
        <tbody>
          <tr><td>SOUL.md</td><td>定义 AI 的名字、性格和说话风格</td><td>你叫小智，说话简洁友好，始终用中文回复，称呼用户为「主人」</td></tr>
          <tr><td>USER.md</td><td>告诉 AI 关于你的信息，让它更懂你</td><td>我叫张三，是一名设计师，常用 Mac，喜欢简洁的回答</td></tr>
          <tr><td>MEMORY.md</td><td>AI 的跨对话记忆，由 AI 自动维护</td><td>无需手动编辑，AI 会自动记录重要信息</td></tr>
          <tr><td>HEARTBEAT.md</td><td>设定 AI 定时主动发消息给你</td><td>每天早上 8 点发送今日天气和待办事项提醒</td></tr>
        </tbody>
      </table>
      <div class="doc-tip">💡 <strong>最简单的个性化方式</strong>：打开 SOUL.md，在第一行写上「你叫XXX，始终用中文回复」，保存后 AI 立刻改变称呼和语言。</div>
    </div>

    <!-- ── 常见问题 ── -->
    <div class="doc-section" id="doc-faq">
      <h3>❓ 常见问题</h3>
      <div class="doc-tip"><strong>Q：发消息给 Bot 没有任何回应？</strong><br>
        1. 面板「状态」Tab 确认网关显示绿色「运行中」<br>
        2. 检查 API Key 是否正确且账户有余额<br>
        3. 确认「允许的用户 ID」中包含你的 Telegram 用户 ID<br>
        4. 检查 Bot Token 是否完整复制，中间没有空格<br>
        5. Windows：右键托盘 → 查看日志，查看具体报错
      </div>
      <div class="doc-tip"><strong>Q：改了配置但 Bot 行为没变化？</strong><br>
        保存配置后必须重启网关才生效。Windows：右键托盘 → 重启服务。其他系统：停止后重新运行 pgflow gateway。
      </div>
      <div class="doc-tip"><strong>Q：Windows 提示「Windows 已保护你的电脑」？</strong><br>
        这是 Windows SmartScreen 对未签名程序的提示，并非病毒。点击「更多信息」→「仍要运行」即可。如果杀毒软件拦截，将 pgflow 文件夹加入排除列表。
      </div>
      <div class="doc-tip"><strong>Q：macOS 提示「无法打开，因为无法验证开发者」？</strong><br>
        首次运行时，<strong>必须右键点击图标 → 打开</strong>，而不是双击。之后就可以正常双击启动了。
      </div>
      <div class="doc-tip"><strong>Q：如何升级到新版本？</strong><br>
        Windows / macOS：下载新版安装包，解压或安装覆盖旧版。你的所有配置和记忆保存在 <span class="doc-code">~/.pgflow/</span> 目录，升级不会丢失。<br>
        VPS：重新运行安装脚本，会自动升级到最新版。
      </div>
      <div class="doc-tip"><strong>Q：如何让 AI 说中文？</strong><br>
        打开工作区的 <span class="doc-code">SOUL.md</span> 文件，加入一行「始终使用中文回复用户」，保存即可，无需重启。
      </div>
      <div class="doc-tip"><strong>Q：在哪里找到工作区文件夹？</strong><br>
        Windows：在文件资源管理器地址栏输入 <span class="doc-code">%USERPROFILE%\.pgflow\workspace</span> 回车即可打开。<br>
        macOS / Linux：打开终端，输入 <span class="doc-code">open ~/.pgflow/workspace</span>（macOS）或 <span class="doc-code">xdg-open ~/.pgflow/workspace</span>（Linux）。
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
    row('当前版本', `<code>${d.version}</code>`);

  // Also refresh gateway + version + channel status
  loadGatewayStatus();
  loadVersionInfo();
  loadChannelStatus(d);

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

// ── Channel Status ───────────────────────────────────────────────────────────
function loadChannelStatus(d) {
  const el = document.getElementById('channel-status-rows');
  const CHANNEL_LABELS = {
    telegram: '✈️ Telegram', discord: '🎮 Discord', slack: '💬 Slack',
    feishu: '🪶 飞书', dingtalk: '📎 钉钉', qq: '🐧 QQ',
    wecom: '💼 企业微信', matrix: '🔷 Matrix', whatsapp: '📱 WhatsApp',
    email: '📧 邮件',
  };
  const channels = d.channels_enabled || {};
  const entries = Object.entries(CHANNEL_LABELS);
  const enabled = entries.filter(([k]) => channels[k]);
  const disabled = entries.filter(([k]) => !channels[k]);

  if (enabled.length === 0) {
    el.innerHTML = '<div class="empty">未启用任何渠道 — 前往「配置」Tab 添加</div>';
    return;
  }
  el.innerHTML =
    enabled.map(([, label]) =>
      `<div class="row"><label>${label}</label><span class="badge green">已启用</span></div>`
    ).join('') +
    disabled.map(([, label]) =>
      `<div class="row"><label>${label}</label><span class="badge gray">未启用</span></div>`
    ).join('');
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

// ── Version Check ───────────────────────────────────────────────────────────
async function loadVersionInfo() {
  try {
    const d = await api('/api/version');
    const elCurrent = document.getElementById('ver-current');
    const elLatest  = document.getElementById('ver-latest');
    const elRow     = document.getElementById('ver-update-row');
    const elLink    = document.getElementById('ver-update-link');

    elCurrent.innerHTML = `<code>v${d.current}</code>`;

    if (!d.latest) {
      elLatest.innerHTML = `<span class="badge gray">无法获取（请检查网络）</span>`;
    } else if (d.update_available) {
      elLatest.innerHTML = `<span class="badge amber">v${d.latest} 有新版本</span>`;
      elLink.href = d.release_url;
      elLink.textContent = `⬇ 下载 v${d.latest}`;
      elRow.style.display = 'flex';
    } else {
      elLatest.innerHTML = `<span class="badge green">v${d.latest} 已是最新</span>`;
      elRow.style.display = 'none';
    }
  } catch(e) {
    const elLatest = document.getElementById('ver-latest');
    if (elLatest) elLatest.innerHTML = `<span class="badge gray">检测失败</span>`;
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

// 服务商预设：apiBase + 默认模型
const PROVIDER_PRESETS = {
  openrouter:   { base: '',                                  model: 'anthropic/claude-opus-4-5',  needBase: false },
  deepseek:     { base: 'https://api.deepseek.com/v1',       model: 'deepseek-chat',              needBase: true  },
  siliconflow:  { base: 'https://api.siliconflow.cn/v1',     model: 'deepseek-ai/DeepSeek-V3',    needBase: true  },
  zhipu:        { base: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-flash',             needBase: true  },
  dashscope:    { base: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus', needBase: true  },
  moonshot:     { base: 'https://api.moonshot.cn/v1',        model: 'moonshot-v1-8k',             needBase: true  },
  volcengine:   { base: 'https://ark.cn-beijing.volces.com/api/v3', model: 'doubao-pro-32k',      needBase: true  },
  anthropic:    { base: '',                                  model: 'claude-opus-4-5',             needBase: false },
  openai:       { base: '',                                  model: 'gpt-4o',                     needBase: false },
  gemini:       { base: '',                                  model: 'gemini/gemini-2.0-flash',    needBase: false },
  groq:         { base: '',                                  model: 'groq/llama-3.3-70b-versatile', needBase: false },
  custom:       { base: '',                                  model: '',                           needBase: true  },
};

// 自定义接口时显示 Base URL 输入框
function onProviderChange() {
  const v = document.getElementById('cfg-provider').value;
  const preset = PROVIDER_PRESETS[v] || {};
  const baseGroup = document.getElementById('apibase-group');
  const baseHint  = document.getElementById('apibase-hint');
  const baseInput = document.getElementById('cfg-apibase');
  const modelInput = document.getElementById('cfg-model');
  const modelHint  = document.getElementById('model-hint');

  if (preset.needBase) {
    baseGroup.style.display = 'block';
    baseHint.textContent = v === 'custom' ? '自定义接口地址' : '已预填，可按需修改';
    if (!baseInput.value && preset.base) baseInput.value = preset.base;
  } else {
    baseGroup.style.display = 'none';
  }

  // 仅在模型为空或为旧预设时自动填入
  if (preset.model && !modelInput.value) {
    modelInput.value = preset.model;
  }
  modelHint.textContent = preset.model ? `推荐模型：${preset.model}` : '';
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
  // 触发服务商切换逻辑（显示/隐藏 apiBase，填推荐模型提示）
  onProviderChange();

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
  // dingtalk
  { const c = channels.dingtalk || {};
    document.getElementById('ch-dingtalk-enabled').checked   = !!c.enabled;
    document.getElementById('ch-dingtalk-clientid').value    = c.clientId || '';
    document.getElementById('ch-dingtalk-secret').value      = c.clientSecret || ''; }
  // qq
  { const c = channels.qq || {};
    document.getElementById('ch-qq-enabled').checked  = !!c.enabled;
    document.getElementById('ch-qq-appid').value      = c.appId || '';
    document.getElementById('ch-qq-secret').value     = c.appSecret || ''; }
  // wecom
  { const c = channels.wecom || {};
    document.getElementById('ch-wecom-enabled').checked   = !!c.enabled;
    document.getElementById('ch-wecom-corpid').value      = c.corpId || '';
    document.getElementById('ch-wecom-secret').value      = c.corpSecret || '';
    document.getElementById('ch-wecom-agentid').value     = c.agentId || ''; }
  // matrix
  { const c = channels.matrix || {};
    document.getElementById('ch-matrix-enabled').checked     = !!c.enabled;
    document.getElementById('ch-matrix-homeserver').value    = c.homeserver || '';
    document.getElementById('ch-matrix-token').value         = c.accessToken || ''; }
  // whatsapp
  { const c = channels.whatsapp || {};
    document.getElementById('ch-whatsapp-enabled').checked  = !!c.enabled;
    document.getElementById('ch-whatsapp-url').value        = c.bridgeUrl || ''; }
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
      cfg.providers[name].apiKey = '';
    }
  }
  if (!cfg.providers[provider]) cfg.providers[provider] = {};
  cfg.providers[provider].apiKey = apiKey;
  // 保存 apiBase（国内服务商直连必须有）
  const preset = PROVIDER_PRESETS[provider] || {};
  if (preset.needBase) {
    cfg.providers[provider].apiBase = apiBase || preset.base || '';
  } else {
    delete cfg.providers[provider].apiBase;
  }

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
  // dingtalk
  { const enabled   = document.getElementById('ch-dingtalk-enabled').checked;
    const clientId  = document.getElementById('ch-dingtalk-clientid').value.trim();
    const secret    = document.getElementById('ch-dingtalk-secret').value.trim();
    if (!cfg.channels.dingtalk) cfg.channels.dingtalk = {};
    cfg.channels.dingtalk.enabled = enabled;
    if (clientId) cfg.channels.dingtalk.clientId     = clientId;
    if (secret)   cfg.channels.dingtalk.clientSecret = secret; }
  // qq
  { const enabled = document.getElementById('ch-qq-enabled').checked;
    const appId   = document.getElementById('ch-qq-appid').value.trim();
    const secret  = document.getElementById('ch-qq-secret').value.trim();
    if (!cfg.channels.qq) cfg.channels.qq = {};
    cfg.channels.qq.enabled = enabled;
    if (appId)  cfg.channels.qq.appId     = appId;
    if (secret) cfg.channels.qq.appSecret = secret; }
  // wecom
  { const enabled  = document.getElementById('ch-wecom-enabled').checked;
    const corpId   = document.getElementById('ch-wecom-corpid').value.trim();
    const secret   = document.getElementById('ch-wecom-secret').value.trim();
    const agentId  = document.getElementById('ch-wecom-agentid').value.trim();
    if (!cfg.channels.wecom) cfg.channels.wecom = {};
    cfg.channels.wecom.enabled = enabled;
    if (corpId)  cfg.channels.wecom.corpId     = corpId;
    if (secret)  cfg.channels.wecom.corpSecret = secret;
    if (agentId) cfg.channels.wecom.agentId    = agentId; }
  // matrix
  { const enabled    = document.getElementById('ch-matrix-enabled').checked;
    const homeserver = document.getElementById('ch-matrix-homeserver').value.trim();
    const token      = document.getElementById('ch-matrix-token').value.trim();
    if (!cfg.channels.matrix) cfg.channels.matrix = {};
    cfg.channels.matrix.enabled = enabled;
    if (homeserver) cfg.channels.matrix.homeserver   = homeserver;
    if (token)      cfg.channels.matrix.accessToken  = token; }
  // whatsapp
  { const enabled = document.getElementById('ch-whatsapp-enabled').checked;
    const url     = document.getElementById('ch-whatsapp-url').value.trim();
    if (!cfg.channels.whatsapp) cfg.channels.whatsapp = {};
    cfg.channels.whatsapp.enabled = enabled;
    if (url) cfg.channels.whatsapp.bridgeUrl = url; }
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
let _logAutoRefreshTimer = null;

async function loadLogs() {
  const d = await api('/api/logs');
  const el = document.getElementById('log-content');
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
  el.textContent = d.logs || '（暂无日志）';
  // 仅当用户本来就在底部时才自动滚动，避免打断手动滚动查看
  if (atBottom) el.scrollTop = el.scrollHeight;
}

function scrollLogsToBottom() {
  const el = document.getElementById('log-content');
  el.scrollTop = el.scrollHeight;
}

function onLogAutoRefresh(enabled) {
  if (_logAutoRefreshTimer) { clearInterval(_logAutoRefreshTimer); _logAutoRefreshTimer = null; }
  if (enabled) {
    loadLogs();
    _logAutoRefreshTimer = setInterval(loadLogs, 3000);
  }
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

# Cached results to avoid blocking the single-threaded HTTP server
_gateway_cache: dict = {"running": False, "ts": 0.0}
_version_cache: dict = {"data": None, "ts": 0.0}
_GATEWAY_CACHE_TTL = 10.0   # seconds
_VERSION_CACHE_TTL = 300.0  # 5 minutes


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
    Result is cached for _GATEWAY_CACHE_TTL seconds to avoid blocking.
    """
    import sys
    import subprocess
    import time

    now = time.monotonic()
    if now - _gateway_cache["ts"] < _GATEWAY_CACHE_TTL:
        return _gateway_cache["running"]

    def _refresh():
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
                running = count.isdigit() and int(count) > 0
            else:
                result = subprocess.run(
                    ["pgrep", "-f", "pgflow.*gateway"],
                    capture_output=True, timeout=2,
                )
                running = result.returncode == 0
        except Exception:
            running = False
        _gateway_cache["running"] = running
        _gateway_cache["ts"] = time.monotonic()

    # Run refresh in background thread so the HTTP handler returns immediately
    # Use the cached (possibly stale) value in the meantime
    t = threading.Thread(target=_refresh, daemon=True)
    t.start()

    # If cache is brand new (first call), wait briefly for the result
    if _gateway_cache["ts"] == 0.0:
        t.join(timeout=4)

    return _gateway_cache["running"]


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
            # 渠道启用状态
            channels_cfg = cfg.model_dump(mode="json", by_alias=True).get("channels", {})
            status["channels_enabled"] = {
                k: bool(v.get("enabled")) for k, v in channels_cfg.items()
            }
        except Exception:
            pass

    return status


def _get_gateway() -> dict:
    return {"running": _gateway_running()}


def _get_version_info() -> dict:
    """Return current version and check GitHub for the latest release.
    Result is cached for _VERSION_CACHE_TTL seconds to avoid blocking.
    """
    import time

    now = time.monotonic()
    if _version_cache["data"] is not None and now - _version_cache["ts"] < _VERSION_CACHE_TTL:
        return _version_cache["data"]

    from nanobot import __version__
    import urllib.request
    import json as _json

    result = {
        "current": __version__,
        "latest": None,
        "update_available": False,
        "release_url": "https://github.com/leoyangx/PgFlow/releases/latest",
    }

    def _refresh():
        try:
            req = urllib.request.Request(
                "https://leoyangx.github.io/PgFlow/version.json",
                headers={"User-Agent": "PgFlow-Dashboard"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = _json.loads(resp.read())
            latest_tag = data.get("version", "").lstrip("v")
            result["latest"] = latest_tag
            result["release_url"] = data.get("download_url", result["release_url"])
            if latest_tag and latest_tag != __version__:
                def _parse(v):
                    try:
                        return tuple(int(x) for x in v.split(".")[:3])
                    except Exception:
                        return (0, 0, 0)
                if _parse(latest_tag) > _parse(__version__):
                    result["update_available"] = True
        except Exception:
            pass  # Offline or server unreachable — silent fail
        _version_cache["data"] = result
        _version_cache["ts"] = time.monotonic()

    # Run in background; return stale/empty result immediately if cache exists
    t = threading.Thread(target=_refresh, daemon=True)
    t.start()

    # On first call, wait briefly so we return something useful
    if _version_cache["data"] is None:
        t.join(timeout=6)
        if _version_cache["data"] is not None:
            return _version_cache["data"]

    return _version_cache["data"] if _version_cache["data"] is not None else result


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
        elif path == "/api/version":
            self._send_json(_get_version_info())
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
