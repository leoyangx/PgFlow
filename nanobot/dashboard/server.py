"""PgFlow local management dashboard — runs on http://localhost:18791"""

from __future__ import annotations

import json
import os
import sys
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
      <button id="ver-update-btn" class="btn btn-green" onclick="startUpdate()" style="font-size:13px">⬇ 一键更新</button>
    </div>
    <div id="ver-update-progress" style="display:none;margin-top:12px">
      <div style="background:#0a0c15;border-radius:6px;height:8px;overflow:hidden;margin-bottom:8px">
        <div id="ver-progress-bar" style="height:100%;width:0%;background:var(--green);transition:width .3s"></div>
      </div>
      <div id="ver-progress-msg" style="font-size:12px;color:var(--muted)"></div>
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
        <option value="aihubmix">AiHubMix（国内网关，无需代理）</option>
        <option value="deepseek">DeepSeek（国内直连，价格极低）</option>
        <option value="siliconflow">硅基流动 SiliconFlow（国内，有免费额度）</option>
        <option value="zhipu">智谱 AI（GLM 系列，国内直连）</option>
        <option value="dashscope">阿里云百炼 DashScope（Qwen 系列）</option>
        <option value="moonshot">Moonshot 月之暗面</option>
        <option value="minimax">MiniMax（海螺 AI）</option>
        <option value="volcengine">火山引擎（豆包）</option>
        <option value="anthropic">Anthropic（Claude 官方）</option>
        <option value="openai">OpenAI（GPT 系列）</option>
        <option value="gemini">Google Gemini</option>
        <option value="mistral">Mistral AI</option>
        <option value="stepfun">阶跃星辰 Step Fun（国内直连）</option>
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
        <div class="form-group">
          <label class="form-label">Verification Token <span class="form-hint">Webhook 验证 Token，可选</span></label>
          <div class="input-eye">
            <input id="ch-feishu-verify-token" type="password" class="form-input" placeholder="留空则不验证签名">
            <button class="eye-btn" onclick="toggleEye('ch-feishu-verify-token', this)" title="显示/隐藏">👁</button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">允许的用户/群组 <span class="form-hint">逗号分隔的 open_id；留空允许所有人</span></label>
          <input id="ch-feishu-allow" type="text" class="form-input" placeholder="ou_xxx, ou_yyy">
        </div>
        <div class="form-group">
          <label class="form-label" style="display:flex;align-items:center;gap:10px">
            <label class="toggle">
              <input type="checkbox" id="ch-feishu-streaming" checked>
              <span class="toggle-slider"></span>
            </label>
            启用流式卡片 <span class="form-hint" style="font-weight:400">使用 CardKit 实时打字效果（需飞书企业版）</span>
          </label>
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
          <label class="form-label">IMAP 端口 <span class="form-hint">默认 993（SSL）</span></label>
          <input id="ch-email-imap-port" type="number" class="form-input" placeholder="993" min="1" max="65535">
        </div>
        <div class="form-group">
          <label class="form-label">SMTP 服务器</label>
          <input id="ch-email-smtp" type="text" class="form-input" placeholder="smtp.gmail.com">
        </div>
        <div class="form-group">
          <label class="form-label">SMTP 端口 <span class="form-hint">默认 465（SSL）或 587（STARTTLS）</span></label>
          <input id="ch-email-smtp-port" type="number" class="form-input" placeholder="465" min="1" max="65535">
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
        <div class="form-group">
          <label class="form-label">允许发件人 <span class="form-hint">逗号分隔邮箱地址；留空允许所有人</span></label>
          <input id="ch-email-allow" type="text" class="form-input" placeholder="boss@company.com, friend@gmail.com">
        </div>
        <div class="form-group">
          <label class="form-label" style="display:flex;align-items:center;gap:10px">
            <label class="toggle">
              <input type="checkbox" id="ch-email-verify-dkim" checked>
              <span class="toggle-slider"></span>
            </label>
            验证 DKIM 签名 <span class="form-hint" style="font-weight:400">拒绝 DKIM 验证失败的邮件（防伪造）</span>
          </label>
        </div>
        <div class="form-group">
          <label class="form-label" style="display:flex;align-items:center;gap:10px">
            <label class="toggle">
              <input type="checkbox" id="ch-email-verify-spf" checked>
              <span class="toggle-slider"></span>
            </label>
            验证 SPF 记录 <span class="form-hint" style="font-weight:400">拒绝 SPF 验证失败的邮件（防伪造）</span>
          </label>
        </div>
      </div>
    </div>

  </div>

  <!-- 区块②b：MCP 服务器 -->
  <div class="card">
    <h2>
      MCP 服务器
      <button class="btn btn-green" onclick="addMcpServer()" style="font-size:12px">＋ 添加</button>
    </h2>
    <p style="font-size:12px;color:var(--muted);margin-bottom:16px">连接外部 MCP 工具服务器（stdio 命令或 HTTP/SSE 端点），保存后重启网关生效。</p>
    <div id="mcp-server-list"></div>
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
        <label class="form-label">时区 <span class="form-hint">IANA 时区名，如 Asia/Shanghai，留空使用系统时区</span></label>
        <input id="cfg-timezone" type="text" class="form-input" placeholder="Asia/Shanghai">
      </div>
      <div class="form-group">
        <label class="form-label">最大输出 Token <span class="form-hint">单次回复最多 token 数，默认 8192</span></label>
        <input id="cfg-max-tokens" type="number" class="form-input" placeholder="8192" min="256" max="131072">
      </div>
      <div class="form-group">
        <label class="form-label">上下文窗口 Token <span class="form-hint">触发摘要压缩的上下文大小，默认 65536</span></label>
        <input id="cfg-context-window" type="number" class="form-input" placeholder="65536" min="4096" max="1000000">
      </div>
      <div class="form-group">
        <label class="form-label">最大工具循环次数 <span class="form-hint">单次对话最多调用工具的轮次，默认 40</span></label>
        <input id="cfg-max-iterations" type="number" class="form-input" placeholder="40" min="1" max="200">
      </div>
      <div class="form-group">
        <label class="form-label">推理强度 <span class="form-hint">启用思维链（Claude/Deepseek 思考模式），留空不启用</span></label>
        <select id="cfg-reasoning-effort" class="form-select">
          <option value="">不启用（默认）</option>
          <option value="low">low — 低强度（快速）</option>
          <option value="medium">medium — 中等强度</option>
          <option value="high">high — 高强度（最慢）</option>
        </select>
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
      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;gap:10px">
          <label class="toggle">
            <input type="checkbox" id="cfg-send-progress" checked>
            <span class="toggle-slider"></span>
          </label>
          流式推送思考过程 <span class="form-hint" style="font-weight:400">边思考边发送进度消息</span>
        </label>
      </div>
      <div class="form-group">
        <label class="form-label" style="display:flex;align-items:center;gap:10px">
          <label class="toggle">
            <input type="checkbox" id="cfg-send-tool-hints">
            <span class="toggle-slider"></span>
          </label>
          推送工具调用提示 <span class="form-hint" style="font-weight:400">发送"正在读取文件…"等提示消息</span>
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
    <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">
      <button class="btn btn-muted" id="log-filter-all" onclick="setLogFilter('all')" style="font-size:12px;padding:4px 10px">全部</button>
      <button class="btn" id="log-filter-ERROR" onclick="setLogFilter('ERROR')" style="font-size:12px;padding:4px 10px;background:#5c1a1a;color:var(--red)">ERROR</button>
      <button class="btn" id="log-filter-WARNING" onclick="setLogFilter('WARNING')" style="font-size:12px;padding:4px 10px;background:#2e1f0d;color:var(--amber)">WARNING</button>
      <button class="btn" id="log-filter-INFO" onclick="setLogFilter('INFO')" style="font-size:12px;padding:4px 10px;background:#1a2744;color:var(--accent)">INFO</button>
      <button class="btn btn-muted" id="log-filter-DEBUG" onclick="setLogFilter('DEBUG')" style="font-size:12px;padding:4px 10px">DEBUG</button>
    </div>
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
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-telegram')">✈️ Telegram</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-discord')">🎮 Discord</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-feishu')">🪶 飞书</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-dingtalk')">📎 钉钉</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-qq')">🐧 QQ</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-wecom')">💼 企业微信</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-email')">📧 邮件</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-providers')">🤖 AI 服务商</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-workspace')">📁 工作区文件</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-faq')">❓ 常见问题</button>
    <button class="btn btn-muted"   onclick="scrollToDoc('doc-multiagent')">🤖 多 Agent</button>
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
        <li>如果杀毒软件拦截，请将 <span class="doc-code">pgflow/</span> 文件夹加入白名单（排除列表）</li>
      </ol>

      <p><strong>第三步：完成配置</strong></p>
      <ol>
        <li>点击面板顶部「配置」Tab</li>
        <li>选择 AI 服务商，填写 API Key，保存</li>
        <li>展开「Telegram」渠道，填写 Bot Token 和你的用户 ID，开启开关，保存</li>
        <li>右键托盘图标 → <strong>开启网关</strong>（网关未运行时）或 <strong>重启网关</strong>（网关已运行时）</li>
        <li>向 Telegram Bot 发送任意消息，验证是否正常响应</li>
      </ol>

      <p><strong>日常使用</strong></p>
      <table class="doc-table">
        <thead><tr><th>需求</th><th>操作</th></tr></thead>
        <tbody>
          <tr><td>开机自动启动</td><td>右键托盘图标 → 开机自启（打勾即启用，无需任何命令）</td></tr>
          <tr><td>修改配置</td><td>面板「配置」Tab 修改保存 → 右键托盘 → 重启网关</td></tr>
          <tr><td>查看运行日志</td><td>右键托盘图标 → 查看日志，或面板「日志」Tab</td></tr>
          <tr><td>完全退出程序</td><td>右键托盘图标 → 退出</td></tr>
        </tbody>
      </table>
      <div class="doc-warn">⚠️ <strong>重要：</strong>修改配置保存后，必须右键托盘 → 重启网关，新配置才会生效。仅点保存不会自动重启。</div>
    </div>

    <!-- ── macOS ── -->
    <div class="doc-section" id="doc-mac">
      <h3>🍎 macOS 使用说明</h3>
      <p>macOS 版本以 <span class="doc-code">.dmg</span> 安装包形式分发，安装后通过系统菜单栏管理，体验与 Windows 基本一致。</p>

      <p><strong>第一步：安装</strong></p>
      <ol>
        <li>打开收到的 <span class="doc-code">PgFlow-macOS.dmg</span> 文件</li>
        <li>将 <span class="doc-code">PgFlow</span> 图标拖拽到「应用程序」文件夹</li>
        <li>在「应用程序」中找到 PgFlow，<strong>右键点击 → 打开</strong>（首次必须右键打开，否则 macOS 会拒绝运行）</li>
        <li>弹出安全提示时，点击「打开」确认</li>
      </ol>

      <p><strong>第二步：完成配置</strong></p>
      <ol>
        <li>启动后浏览器自动打开管理面板，或访问 <span class="doc-code">http://localhost:18791</span></li>
        <li>点击「配置」Tab，填写 API Key 和 Telegram Bot Token，保存</li>
        <li>点击顶部菜单栏的 🌊 图标 → <strong>开启网关</strong></li>
        <li>向 Telegram Bot 发消息测试</li>
      </ol>

      <p><strong>日常使用</strong></p>
      <table class="doc-table">
        <thead><tr><th>需求</th><th>操作</th></tr></thead>
        <tbody>
          <tr><td>开机自动启动</td><td>菜单栏 🌊 图标 → 开机自启（打勾启用）</td></tr>
          <tr><td>打开管理面板</td><td>菜单栏 🌊 图标 → 打开管理面板</td></tr>
          <tr><td>修改配置后生效</td><td>保存配置 → 菜单栏 🌊 → 重启网关</td></tr>
          <tr><td>退出程序</td><td>菜单栏 🌊 图标 → 退出</td></tr>
        </tbody>
      </table>
      <div class="doc-tip">💡 macOS 14（Sonoma）及以上系统，首次运行时系统设置 → 隐私与安全性 → 底部会出现「仍要打开」按钮，点击即可。</div>
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
    </div>

    <!-- ── VPS 服务器 ── -->
    <div class="doc-section" id="doc-vps">
      <h3>☁️ VPS 服务器使用说明</h3>
      <p>将 PgFlow 部署到云服务器（如阿里云、腾讯云、AWS）后，即使本地电脑关机，AI 助手也能 24 小时在线响应。</p>

      <p><strong>系统要求</strong></p>
      <ul>
        <li>操作系统：Ubuntu 22.04 / Debian 12（推荐）或其他 Linux 发行版</li>
        <li>内存：512MB 以上（推荐 1GB）</li>
        <li>需要有公网访问权限（能连接 Telegram、AI 服务商 API）</li>
      </ul>

      <p><strong>第一步：一键安装</strong></p>
      <p>SSH 登录服务器后，运行以下命令自动安装：</p>
      <div class="doc-code" style="display:block;padding:12px 16px;margin:8px 0;font-size:13px">bash &lt;(curl -fsSL https://raw.githubusercontent.com/leoyangx/PgFlow/main/install.sh)</div>

      <p><strong>第二步：后台持久运行</strong></p>
      <ol>
        <li>使用 screen 保持后台运行（断开 SSH 也不停止）：<br>
          <span class="doc-code">screen -S pgflow</span> → 运行 <span class="doc-code">pgflow gateway</span> → 按 <span class="doc-code">Ctrl+A</span> 再按 <span class="doc-code">D</span>
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
      <div class="doc-warn">⚠️ 请勿将管理面板端口（18791）直接开放到公网，面板暂无登录验证。始终通过 SSH 隧道方式访问。</div>
    </div>

    <!-- ── Telegram ── -->
    <div class="doc-section" id="doc-telegram">
      <h3>✈️ Telegram 渠道接入教程</h3>
      <div class="doc-tip">💡 Telegram 是最推荐的渠道，稳定、快速、支持多端同步，国内需要科学上网。</div>

      <p><strong>第一步：创建 Telegram Bot</strong></p>
      <ol>
        <li>打开 Telegram，搜索 <span class="doc-code">@BotFather</span>，点击进入并发送 <span class="doc-code">/newbot</span></li>
        <li>BotFather 会问你 Bot 的<strong>显示名称</strong>（如「我的 AI 助手」）和<strong>用户名</strong>（必须以 bot 结尾，如 <span class="doc-code">myai_bot</span>）</li>
        <li>创建成功后，BotFather 会发给你一串 Token，格式类似：<br>
          <span class="doc-code">123456789:AABBccDDeeFFggHH...</span><br>
          <strong>复制这串 Token，稍后填入配置</strong>
        </li>
      </ol>

      <p><strong>第二步：获取你的 Telegram 用户 ID</strong></p>
      <ol>
        <li>在 Telegram 搜索 <span class="doc-code">@userinfobot</span></li>
        <li>发送 <span class="doc-code">/start</span>，它会回复你的 ID（纯数字，如 <span class="doc-code">123456789</span>）</li>
        <li>复制这个纯数字 ID</li>
      </ol>

      <p><strong>第三步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「Telegram」渠道</li>
        <li>将 Bot Token 粘贴到「Bot Token」输入框</li>
        <li>将你的用户 ID 填入「允许的用户 ID」（多人用逗号分隔）</li>
        <li>开启渠道开关，点击「💾 保存配置」</li>
        <li>右键托盘 → 重启网关（或首次启动网关）</li>
      </ol>

      <p><strong>第四步：测试连接</strong></p>
      <ol>
        <li>在 Telegram 搜索你创建的 Bot 用户名，点击 Start</li>
        <li>发送任意消息，如「你好」</li>
        <li>Bot 应在数秒内回复，如未响应请查看「日志」Tab 排查错误</li>
      </ol>

      <div class="doc-tip">💡 <strong>允许的用户 ID 说明：</strong>填入自己的 ID 表示只有你能用；如果想分享给家人朋友，把他们的 ID 也加进来（逗号分隔）；填 <span class="doc-code">*</span> 表示允许所有人（不推荐，除非你的机器人是公开服务）。</div>
    </div>

    <!-- ── Discord ── -->
    <div class="doc-section" id="doc-discord">
      <h3>🎮 Discord 渠道接入教程</h3>
      <div class="doc-tip">💡 Discord 适合游戏社区和技术社区场景，国内使用需要科学上网。</div>

      <p><strong>第一步：创建 Discord 应用和 Bot</strong></p>
      <ol>
        <li>访问 <span class="doc-code">discord.com/developers/applications</span>，登录后点击「New Application」</li>
        <li>填写应用名称，点击「Create」</li>
        <li>进入「Bot」选项卡，点击「Add Bot」→「Yes, do it!」</li>
        <li>在 Bot 页面，点击「Reset Token」获取 Bot Token，<strong>复制并保存</strong>（只显示一次）</li>
      </ol>

      <p><strong>第二步：开启消息权限</strong></p>
      <ol>
        <li>在 Bot 页面，找到「Privileged Gateway Intents」部分</li>
        <li>开启 <strong>Message Content Intent</strong>（必须，否则 Bot 收不到消息内容）</li>
        <li>点击「Save Changes」</li>
      </ol>

      <p><strong>第三步：邀请 Bot 到服务器</strong></p>
      <ol>
        <li>进入「OAuth2」→「URL Generator」</li>
        <li>Scopes 勾选 <span class="doc-code">bot</span>，Bot Permissions 勾选：<br>
          Send Messages、Read Message History、View Channels</li>
        <li>复制生成的链接，在浏览器打开，选择你的服务器，点击「授权」</li>
      </ol>

      <p><strong>第四步：获取你的用户 ID</strong></p>
      <ol>
        <li>在 Discord 中，进入「用户设置」→「高级」，开启「开发者模式」</li>
        <li>右键点击你的头像 → 「复制 ID」，即为你的用户 ID</li>
      </ol>

      <p><strong>第五步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「Discord」渠道</li>
        <li>填入 Bot Token 和你的用户 ID，开启开关，保存并重启网关</li>
      </ol>
    </div>

    <!-- ── 飞书 ── -->
    <div class="doc-section" id="doc-feishu">
      <h3>🪶 飞书 Feishu 渠道接入教程</h3>
      <div class="doc-tip">💡 飞书是国内企业最常用的协作工具之一，PgFlow 支持消息接收和流式卡片推送。</div>

      <p><strong>第一步：创建飞书应用</strong></p>
      <ol>
        <li>访问 <span class="doc-code">open.feishu.cn</span>，使用管理员账号登录</li>
        <li>点击「创建企业自建应用」，填写应用名称和描述</li>
        <li>创建完成后，进入应用管理页面，在「凭证与基础信息」中找到：
          <ul>
            <li><strong>App ID</strong>（格式 <span class="doc-code">cli_xxx</span>）</li>
            <li><strong>App Secret</strong>（点击复制）</li>
          </ul>
        </li>
      </ol>

      <p><strong>第二步：配置权限</strong></p>
      <ol>
        <li>在应用管理页面，进入「权限管理」</li>
        <li>申请以下权限：
          <ul>
            <li>im:message:receive_v1（接收消息）</li>
            <li>im:message（发送消息）</li>
          </ul>
        </li>
        <li>点击「申请权限」并等待管理员审批（企业版即时生效）</li>
      </ol>

      <p><strong>第三步：配置事件订阅（消息接收）</strong></p>
      <ol>
        <li>进入「事件与回调」→「事件订阅」</li>
        <li>填写请求地址（即 PgFlow 的 Webhook 地址）：<br>
          <span class="doc-code">http://你的服务器IP:18790/feishu</span></li>
        <li>订阅「接收消息」事件（<span class="doc-code">im.message.receive_v1</span>）</li>
      </ol>

      <p><strong>第四步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「飞书 Feishu」渠道</li>
        <li>填入 App ID 和 App Secret</li>
        <li>如设置了 Verification Token，填入「Verification Token」栏</li>
        <li>「允许的用户/群组」填入你自己的 open_id（可从飞书开放平台的「用户信息」获取）</li>
        <li>流式卡片需要企业版飞书，个人版可关闭该选项</li>
        <li>开启开关，保存并重启网关</li>
      </ol>

      <div class="doc-tip">💡 <strong>获取 open_id：</strong>在飞书开放平台「开发者工具」→「用户 ID 查询」中输入飞书邮箱即可获取 open_id。</div>
    </div>

    <!-- ── 钉钉 ── -->
    <div class="doc-section" id="doc-dingtalk">
      <h3>📎 钉钉 DingTalk 渠道接入教程</h3>
      <div class="doc-tip">💡 钉钉适合已在钉钉办公的企业用户，通过企业内部应用机器人实现。</div>

      <p><strong>第一步：创建钉钉企业内部应用</strong></p>
      <ol>
        <li>访问 <span class="doc-code">open.dingtalk.com</span>，使用管理员账号登录</li>
        <li>进入「应用开发」→「企业内部开发」→「创建应用」</li>
        <li>选择「机器人」类型，填写应用名称</li>
        <li>创建完成后，在「基础信息」中找到：
          <ul>
            <li><strong>Client ID</strong>（即 AppKey）</li>
            <li><strong>Client Secret</strong>（即 AppSecret）</li>
          </ul>
        </li>
      </ol>

      <p><strong>第二步：配置机器人消息接收</strong></p>
      <ol>
        <li>在应用管理页面，进入「消息推送」→「机器人」</li>
        <li>开启机器人功能，配置消息接收地址：<br>
          <span class="doc-code">http://你的服务器IP:18790/dingtalk</span></li>
        <li>申请权限：智能机器人发送消息（qyapi.chat.users.message.send_v2）</li>
      </ol>

      <p><strong>第三步：发布应用</strong></p>
      <ol>
        <li>完成权限申请后，点击「发布」，将应用发布到企业内部</li>
        <li>通知组织成员安装该应用（或通过管理员统一安装）</li>
      </ol>

      <p><strong>第四步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「钉钉 DingTalk」渠道</li>
        <li>填入 Client ID 和 Client Secret，开启开关，保存并重启网关</li>
      </ol>
    </div>

    <!-- ── QQ ── -->
    <div class="doc-section" id="doc-qq">
      <h3>🐧 QQ 渠道接入教程</h3>
      <div class="doc-tip">💡 QQ 渠道通过 QQ 开放平台官方机器人 API 实现，支持个人用户和群组消息。</div>

      <p><strong>第一步：注册 QQ 机器人</strong></p>
      <ol>
        <li>访问 <span class="doc-code">bot.q.qq.com</span>，使用 QQ 账号登录</li>
        <li>点击「立即创建」，选择「频道机器人」或「群聊机器人」</li>
        <li>填写机器人名称、头像和简介，提交审核</li>
        <li>审核通过后（通常 1-3 个工作日），进入「开发设置」获取：
          <ul>
            <li><strong>AppID</strong></li>
            <li><strong>AppSecret</strong>（点击「Token」→「生成」）</li>
          </ul>
        </li>
      </ol>

      <p><strong>第二步：配置 Webhook</strong></p>
      <ol>
        <li>在「开发设置」→「回调地址」中填写：<br>
          <span class="doc-code">http://你的服务器IP:18790/qq</span></li>
        <li>配置要订阅的事件类型（消息接收相关）</li>
      </ol>

      <p><strong>第三步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「QQ」渠道</li>
        <li>填入 App ID 和 App Secret，开启开关，保存并重启网关</li>
      </ol>

      <div class="doc-warn">⚠️ QQ 机器人目前仅支持频道消息和群消息，需要用户主动添加机器人或邀请进群。</div>
    </div>

    <!-- ── 企业微信 ── -->
    <div class="doc-section" id="doc-wecom">
      <h3>💼 企业微信 Wecom 渠道接入教程</h3>
      <div class="doc-tip">💡 企业微信适合中小企业内部使用，员工无需额外注册，直接使用企业账号对话。</div>

      <p><strong>第一步：创建企业应用</strong></p>
      <ol>
        <li>访问 <span class="doc-code">work.weixin.qq.com</span>，使用管理员账号登录后台</li>
        <li>进入「应用管理」→「应用」→「创建应用」</li>
        <li>选择「自建」，填写应用名称、图标和可见范围</li>
        <li>创建完成后，在应用详情中获取：
          <ul>
            <li><strong>AgentId</strong>（应用 ID，数字格式）</li>
            <li><strong>Secret</strong>（点击「查看」获取 Corp Secret）</li>
          </ul>
        </li>
        <li>在「我的企业」→「企业信息」中获取 <strong>企业 ID（Corp ID）</strong>，格式以 <span class="doc-code">ww</span> 开头</li>
      </ol>

      <p><strong>第二步：配置消息接收（可选，如需主动接收用户消息）</strong></p>
      <ol>
        <li>在应用详情中，进入「接收消息」→「设置 API 接收消息」</li>
        <li>填写 URL：<span class="doc-code">http://你的服务器IP:18790/wecom</span></li>
        <li>填写 Token 和 EncodingAESKey，在 PgFlow 配置中同步填写</li>
      </ol>

      <p><strong>第三步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「企业微信 Wecom」渠道</li>
        <li>填入 Corp ID、Corp Secret 和 Agent ID，开启开关，保存并重启网关</li>
      </ol>
    </div>

    <!-- ── 邮件 ── -->
    <div class="doc-section" id="doc-email">
      <h3>📧 邮件渠道接入教程</h3>
      <div class="doc-tip">💡 邮件渠道无需第三方平台，只需一个支持 IMAP/SMTP 的邮箱即可。适合需要邮件指令触发 AI 任务的场景。</div>

      <p><strong>工作原理</strong></p>
      <p>PgFlow 通过 IMAP 定期轮询收件箱，读取新邮件作为指令，通过 SMTP 发送 AI 回复。建议使用专用邮箱，避免与个人邮件混淆。</p>

      <p><strong>第一步：准备邮箱（以 Gmail 为例）</strong></p>
      <ol>
        <li>建议新建一个专用 Gmail 账户（如 <span class="doc-code">myai@gmail.com</span>）</li>
        <li>进入 Gmail 设置 → 「转发和 POP/IMAP」→ 开启 IMAP</li>
        <li>访问 Google 账户 → 安全性 → 两步验证，开启后再创建「应用专用密码」</li>
        <li>在「应用专用密码」中选择「邮件」和「Windows 计算机」，生成 16 位密码</li>
        <li><strong>复制这个 16 位密码</strong>（注意：这不是你的 Gmail 登录密码）</li>
      </ol>

      <p><strong>常见邮件服务商配置</strong></p>
      <table class="doc-table">
        <thead><tr><th>服务商</th><th>IMAP 服务器</th><th>IMAP 端口</th><th>SMTP 服务器</th><th>SMTP 端口</th></tr></thead>
        <tbody>
          <tr><td>Gmail</td><td>imap.gmail.com</td><td>993</td><td>smtp.gmail.com</td><td>465</td></tr>
          <tr><td>QQ 邮箱</td><td>imap.qq.com</td><td>993</td><td>smtp.qq.com</td><td>465</td></tr>
          <tr><td>163 邮箱</td><td>imap.163.com</td><td>993</td><td>smtp.163.com</td><td>465</td></tr>
          <tr><td>Outlook</td><td>outlook.office365.com</td><td>993</td><td>smtp.office365.com</td><td>587</td></tr>
        </tbody>
      </table>

      <p><strong>第二步：获取 QQ 邮箱授权码（国内用户）</strong></p>
      <ol>
        <li>登录 QQ 邮箱，进入「设置」→「账户」</li>
        <li>找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」</li>
        <li>开启「IMAP/SMTP 服务」，点击「生成授权码」</li>
        <li>按提示发送短信验证，获取 16 位授权码</li>
      </ol>

      <p><strong>第三步：在 PgFlow 填写配置</strong></p>
      <ol>
        <li>在面板「配置」Tab，展开「邮件 Email」渠道</li>
        <li>填入 IMAP/SMTP 服务器地址和端口</li>
        <li>邮箱地址填你的邮件账号，密码/授权码填应用专用密码或授权码</li>
        <li>「允许发件人」填入你自己的邮箱地址，确保只有你能触发 AI（留空则所有人都能发邮件给 AI）</li>
        <li>建议保持 DKIM/SPF 验证开启，防止垃圾邮件和伪造邮件触发 AI</li>
        <li>开启开关，保存并重启网关</li>
      </ol>

      <div class="doc-tip">💡 <strong>使用方式：</strong>向绑定的邮箱发送一封邮件，邮件正文即为指令，PgFlow 会处理后以邮件回复你。建议在「允许发件人」中只填自己的邮箱。</div>
      <div class="doc-warn">⚠️ 邮件渠道有延迟（取决于轮询间隔，默认 1 分钟），不适合实时对话场景，适合批处理任务指令。</div>
    </div>

    <!-- ── AI 服务商 ── -->
    <div class="doc-section" id="doc-providers">
      <h3>🤖 推荐的 AI 服务商</h3>
      <p>PgFlow 需要接入 AI 大模型才能工作，你需要在以下任意一家服务商注册并获取 API Key：</p>
      <table class="doc-table">
        <thead><tr><th>服务商</th><th>推荐理由</th><th>适合人群</th><th>注册地址</th></tr></thead>
        <tbody>
          <tr><td>OpenRouter</td><td>一个 Key 用所有模型（Claude、GPT-4、Gemini 等），按量付费，新用户有免费额度</td><td>想尝试多种模型的用户</td><td>openrouter.ai</td></tr>
          <tr><td>AiHubMix</td><td>国内无需代理可访问，支持 Claude/GPT 等全系列模型</td><td>国内用户不想配代理</td><td>aihubmix.com</td></tr>
          <tr><td>DeepSeek</td><td>国内直连无需翻墙，中文理解极强，价格极低（约 OpenAI 的 1/10）</td><td>国内用户首选</td><td>platform.deepseek.com</td></tr>
          <tr><td>硅基流动</td><td>国内平台，支持 DeepSeek、Qwen 等多种模型，有免费额度</td><td>想免费试用的国内用户</td><td>siliconflow.cn</td></tr>
          <tr><td>智谱 AI</td><td>GLM 系列模型，国内直连，注册即送免费额度</td><td>国内用户</td><td>open.bigmodel.cn</td></tr>
          <tr><td>Anthropic</td><td>Claude 官方，效果最强，需要海外信用卡</td><td>有海外支付能力的用户</td><td>console.anthropic.com</td></tr>
        </tbody>
      </table>
      <div class="doc-tip">💡 <strong>推荐新用户选择 AiHubMix 或 DeepSeek</strong>：国内直连、价格低、注册简单。AiHubMix 还支持 Claude 等所有主流模型。</div>
      <div class="doc-tip">💡 <strong>模型名称填写参考：</strong><br>
        · DeepSeek 直连：<span class="doc-code">deepseek-chat</span><br>
        · 硅基流动 DeepSeek：<span class="doc-code">deepseek-ai/DeepSeek-V3</span><br>
        · AiHubMix Claude：<span class="doc-code">claude-opus-4-5</span><br>
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

    <!-- ── 多 Agent ── -->
    <div class="doc-section" id="doc-multiagent">
      <h3>🤖 多 Agent 配置教程</h3>
      <div class="doc-tip">💡 PgFlow 原生支持子 Agent（SubAgent）协同工作，通过手动编辑 <span class="doc-code">config.json</span> 实现灵活的多 Agent 架构，无需修改代码。</div>

      <p><strong>多 Agent 的三种使用场景</strong></p>
      <table class="doc-table">
        <thead><tr><th>场景</th><th>说明</th><th>实现方式</th></tr></thead>
        <tbody>
          <tr><td>不同渠道用不同模型</td><td>Telegram 用 Claude，飞书用 DeepSeek（降低成本）</td><td>多网关实例</td></tr>
          <tr><td>主从协作</td><td>规划 Agent 分解任务，执行 Agent 跑代码</td><td>SubAgent + SKILL.md</td></tr>
          <tr><td>独立人格隔离</td><td>工作 Agent 和生活 Agent 有各自的记忆和性格</td><td>多 workspace</td></tr>
        </tbody>
      </table>

      <p><strong>方案一：不同渠道绑定不同模型（多网关实例）</strong></p>
      <p>在不同端口运行多个网关实例，每个实例配置不同的模型和渠道。</p>
      <p><strong>第一步：准备多份配置文件</strong></p>
      <ol>
        <li>复制默认配置：<span class="doc-code">cp ~/.pgflow/config.json ~/.pgflow/config-work.json</span></li>
        <li>编辑 <span class="doc-code">config-work.json</span>，修改模型、渠道、端口：</li>
      </ol>
      <pre style="font-size:12px;margin-bottom:12px">{
  "providers": {
    "anthropic": { "apiKey": "sk-ant-xxx" }
  },
  "agents": {
    "defaults": {
      "model": "claude-opus-4-5",
      "workspace": "~/.pgflow/workspace-work"
    }
  },
  "gateway": { "port": 18791 },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "WORK_BOT_TOKEN",
      "allowFrom": ["YOUR_USER_ID"]
    }
  }
}</pre>
      <p><strong>第二步：使用不同配置启动多个网关</strong></p>
      <ol>
        <li>第一个网关（默认配置）：<span class="doc-code">pgflow gateway</span></li>
        <li>第二个网关（指定配置文件）：<span class="doc-code">PGFLOW_CONFIG=~/.pgflow/config-work.json pgflow gateway</span></li>
        <li>或通过环境变量指定配置路径：<span class="doc-code">NANOBOT_CONFIG_PATH=~/.pgflow/config-work.json pgflow gateway</span></li>
      </ol>
      <div class="doc-tip">💡 每个网关实例独立运行，拥有各自的会话、记忆和工具权限。通过为每个实例配置不同的 <span class="doc-code">workspace</span> 路径，实现完全隔离的记忆空间。</div>

      <p><strong>方案二：通过 SKILL.md 实现 SubAgent 协作</strong></p>
      <p>PgFlow 内置 SubAgent 机制，主 Agent 可以在处理复杂任务时自动派生子 Agent 并行处理子任务。通过编写 SKILL.md 可以明确指导主 Agent 何时启用 SubAgent。</p>
      <p><strong>在 SOUL.md 中配置主 Agent 策略：</strong></p>
      <pre style="font-size:12px;margin-bottom:12px"># SOUL.md
你是一个任务协调助手。遇到复杂任务时，主动拆解为子任务：
- 信息收集类任务：派生搜索 SubAgent 并行处理
- 代码执行类任务：派生执行 SubAgent 隔离运行
- 长文档处理：派生摘要 SubAgent 分段处理

每次派生 SubAgent 前，告知用户你的分工计划。</pre>
      <p><strong>在 workspace/skills/ 下创建专用技能 Agent：</strong></p>
      <ol>
        <li>创建目录：<span class="doc-code">mkdir -p ~/.pgflow/workspace/skills/researcher</span></li>
        <li>创建 SKILL.md：<span class="doc-code">~/.pgflow/workspace/skills/researcher/SKILL.md</span></li>
      </ol>
      <pre style="font-size:12px;margin-bottom:12px"># Researcher Skill
当用户需要深入研究某个话题时，启用此技能。
作为研究专员，我会：
1. 分解研究问题为多个搜索查询
2. 并行执行网络搜索
3. 综合多个来源，给出有依据的分析报告</pre>

      <p><strong>方案三：多 Workspace 实现人格隔离</strong></p>
      <p>通过为不同用途配置独立的 workspace，实现完全隔离的 AI 人格和记忆。</p>
      <ol>
        <li>创建工作专用工作区：<span class="doc-code">mkdir -p ~/.pgflow/workspace-work</span></li>
        <li>在该工作区创建独立的 SOUL.md：
          <pre style="font-size:12px;margin-top:8px"># ~/.pgflow/workspace-work/SOUL.md
你是一名专业的工作助手，注重效率和准确性。
始终用正式语气回复，专注于工作任务。
绝不讨论与工作无关的话题。</pre>
        </li>
        <li>在 config.json 中指定该工作区路径：
          <pre style="font-size:12px;margin-top:8px">"agents": {
  "defaults": {
    "workspace": "~/.pgflow/workspace-work"
  }
}</pre>
        </li>
      </ol>
      <div class="doc-tip">💡 <strong>记忆完全独立：</strong>每个 workspace 有自己的 MEMORY.md，不同 Agent 之间的记忆互不干扰。</div>

      <p><strong>进阶：通过 config.json 手动配置多模型策略</strong></p>
      <p>直接编辑 <span class="doc-code">~/.pgflow/config.json</span>（面板「配置」→「查看/编辑原始 JSON」），可以配置多个服务商同时可用：</p>
      <pre style="font-size:12px;margin-bottom:12px">{
  "providers": {
    "anthropic": { "apiKey": "sk-ant-xxx" },
    "deepseek": {
      "apiKey": "sk-xxx",
      "apiBase": "https://api.deepseek.com/v1"
    }
  },
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "provider": "auto",
      "maxToolIterations": 40
    }
  }
}</pre>
      <div class="doc-warn">⚠️ 当前版本的 Dashboard 配置页面每次只保存一个活跃服务商的 API Key，多服务商并存需通过「原始 JSON」编辑器手动维护。</div>
    </div>

    <!-- ── 常见问题 ── -->
    <div class="doc-section" id="doc-faq">
      <h3>❓ 常见问题</h3>
      <div class="doc-tip"><strong>Q：发消息给 Bot 没有任何回应？</strong><br>
        1. 面板「状态」Tab 确认网关显示绿色「运行中」<br>
        2. 检查 API Key 是否正确且账户有余额<br>
        3. 确认「允许的用户 ID」中包含你的用户 ID<br>
        4. 检查 Bot Token 是否完整复制，中间没有空格<br>
        5. 面板「日志」Tab 查看具体报错信息
      </div>
      <div class="doc-tip"><strong>Q：改了配置但 Bot 行为没变化？</strong><br>
        保存配置后必须重启网关才生效。Windows：右键托盘 → 重启网关。其他系统：停止后重新运行 pgflow gateway。
      </div>
      <div class="doc-tip"><strong>Q：Windows 提示「Windows 已保护你的电脑」？</strong><br>
        这是 Windows SmartScreen 对未签名程序的提示，并非病毒。点击「更多信息」→「仍要运行」即可。如果杀毒软件拦截，将 pgflow 文件夹加入排除列表。
      </div>
      <div class="doc-tip"><strong>Q：macOS 提示「无法打开，因为无法验证开发者」？</strong><br>
        首次运行时，<strong>必须右键点击图标 → 打开</strong>，而不是双击。之后就可以正常双击启动了。
      </div>
      <div class="doc-tip"><strong>Q：如何升级到新版本？</strong><br>
        Windows / macOS：面板「状态」Tab 若有新版本提示，点击「⬇ 一键更新」即可自动升级。你的所有配置和记忆保存在 <span class="doc-code">~/.pgflow/</span> 目录，升级不会丢失。<br>
        VPS：重新运行安装脚本，会自动升级到最新版。
      </div>
      <div class="doc-tip"><strong>Q：如何让 AI 说中文？</strong><br>
        打开工作区的 <span class="doc-code">SOUL.md</span> 文件，加入一行「始终使用中文回复用户」，保存即可，无需重启。
      </div>
      <div class="doc-tip"><strong>Q：在哪里找到工作区文件夹？</strong><br>
        Windows：在文件资源管理器地址栏输入 <span class="doc-code">%USERPROFILE%\.pgflow\workspace</span> 回车即可打开。<br>
        macOS / Linux：打开终端，输入 <span class="doc-code">open ~/.pgflow/workspace</span>（macOS）或 <span class="doc-code">xdg-open ~/.pgflow/workspace</span>（Linux）。
      </div>
      <div class="doc-tip"><strong>Q：日志页面显示「日志目录为空」？</strong><br>
        网关启动后才会生成日志文件。确保网关正在运行（状态页显示绿色），然后刷新日志页面。
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
let _updateUrl = '';
let _updatePollTimer = null;

async function loadVersionInfo() {
  try {
    const d = await api('/api/version');
    const elCurrent = document.getElementById('ver-current');
    const elLatest  = document.getElementById('ver-latest');
    const elRow     = document.getElementById('ver-update-row');

    elCurrent.innerHTML = `<code>v${d.current}</code>`;

    if (!d.latest) {
      elLatest.innerHTML = `<span class="badge gray">无法获取（请检查网络）</span>`;
    } else if (d.update_available) {
      elLatest.innerHTML = `<span class="badge amber">v${d.latest} 有新版本</span>`;
      _updateUrl = d.release_url;
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

async function startUpdate() {
  if (!_updateUrl) return;
  const btn = document.getElementById('ver-update-btn');
  btn.disabled = true;
  btn.textContent = '更新中…';
  document.getElementById('ver-update-progress').style.display = 'block';

  await api('/api/update/start', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url: _updateUrl}),
  });

  // Poll for progress
  _updatePollTimer = setInterval(async () => {
    const s = await api('/api/update/status');
    document.getElementById('ver-progress-bar').style.width = s.progress + '%';
    document.getElementById('ver-progress-msg').textContent = s.message;

    if (s.status === 'done') {
      clearInterval(_updatePollTimer);
      btn.textContent = '✓ 已更新';
      document.getElementById('ver-progress-msg').style.color = 'var(--green)';
    } else if (s.status === 'error') {
      clearInterval(_updatePollTimer);
      btn.disabled = false;
      btn.textContent = '⬇ 一键更新';
      document.getElementById('ver-progress-msg').style.color = 'var(--red)';
    }
  }, 800);
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
  aihubmix:     { base: 'https://aihubmix.com/v1',          model: 'claude-opus-4-5',            needBase: true  },
  deepseek:     { base: 'https://api.deepseek.com/v1',       model: 'deepseek-chat',              needBase: true  },
  siliconflow:  { base: 'https://api.siliconflow.cn/v1',     model: 'deepseek-ai/DeepSeek-V3',    needBase: true  },
  zhipu:        { base: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4-flash',             needBase: true  },
  dashscope:    { base: 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus', needBase: true  },
  moonshot:     { base: 'https://api.moonshot.cn/v1',        model: 'moonshot-v1-8k',             needBase: true  },
  minimax:      { base: 'https://api.minimax.io/v1',         model: 'minimax-text-01',            needBase: true  },
  volcengine:   { base: 'https://ark.cn-beijing.volces.com/api/v3', model: 'doubao-pro-32k',      needBase: true  },
  anthropic:    { base: '',                                  model: 'claude-opus-4-5',             needBase: false },
  openai:       { base: '',                                  model: 'gpt-4o',                     needBase: false },
  gemini:       { base: '',                                  model: 'gemini/gemini-2.0-flash',    needBase: false },
  mistral:      { base: '',                                  model: 'mistral-large-latest',       needBase: false },
  groq:         { base: '',                                  model: 'groq/llama-3.3-70b-versatile', needBase: false },
  stepfun:      { base: 'https://api.stepfun.com/v1',       model: 'step-2-16k',                 needBase: true  },
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
  const providerNames = ['openrouter','aihubmix','anthropic','openai','deepseek','gemini',
    'zhipu','dashscope','siliconflow','volcengine','moonshot','minimax','mistral','groq','stepfun'];
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
    document.getElementById('ch-feishu-secret').value     = c.appSecret || '';
    document.getElementById('ch-feishu-verify-token').value = c.verificationToken || '';
    document.getElementById('ch-feishu-allow').value      = allowToStr(c.allowFrom);
    document.getElementById('ch-feishu-streaming').checked = c.streaming !== false; }
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
    document.getElementById('ch-email-imap-port').value   = c.imapPort || '';
    document.getElementById('ch-email-smtp').value        = c.smtpHost || '';
    document.getElementById('ch-email-smtp-port').value   = c.smtpPort || '';
    document.getElementById('ch-email-addr').value        = c.email || c.address || '';
    document.getElementById('ch-email-pass').value        = c.password || '';
    document.getElementById('ch-email-allow').value       = allowToStr(c.allowFrom);
    document.getElementById('ch-email-verify-dkim').checked = c.verifyDkim !== false;
    document.getElementById('ch-email-verify-spf').checked  = c.verifySpf !== false; }

  // ③ 高级
  const tools = cfg.tools || {};
  document.getElementById('cfg-workspace').value      = agentDef.workspace || '';
  document.getElementById('cfg-timezone').value       = agentDef.timezone || '';
  document.getElementById('cfg-max-tokens').value     = agentDef.maxTokens || agentDef.max_tokens || '';
  document.getElementById('cfg-context-window').value = agentDef.contextWindowTokens || agentDef.context_window_tokens || '';
  document.getElementById('cfg-max-iterations').value = agentDef.maxToolIterations || agentDef.max_tool_iterations || '';
  document.getElementById('cfg-reasoning-effort').value = agentDef.reasoningEffort || agentDef.reasoning_effort || '';
  document.getElementById('cfg-proxy').value          = (tools.web || {}).proxy || '';
  document.getElementById('cfg-exec-enable').checked  = (tools.exec || {}).enable !== false;
  const chanCfg = cfg.channels || {};
  document.getElementById('cfg-send-progress').checked   = chanCfg.sendProgress !== false;
  document.getElementById('cfg-send-tool-hints').checked = !!chanCfg.sendToolHints;
  // MCP servers
  renderMcpList((tools.mcpServers || tools.mcp_servers) || {});
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
  const knownProviders = ['openrouter','aihubmix','anthropic','openai','deepseek','gemini',
    'zhipu','dashscope','siliconflow','volcengine','moonshot','minimax','mistral','groq','stepfun','custom'];
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
    const verifyToken = document.getElementById('ch-feishu-verify-token').value.trim();
    const allow   = strToAllow(document.getElementById('ch-feishu-allow').value);
    const streaming = document.getElementById('ch-feishu-streaming').checked;
    if (!cfg.channels.feishu) cfg.channels.feishu = {};
    cfg.channels.feishu.enabled = enabled;
    if (appId)  cfg.channels.feishu.appId     = appId;
    if (secret) cfg.channels.feishu.appSecret = secret;
    if (verifyToken) cfg.channels.feishu.verificationToken = verifyToken;
    cfg.channels.feishu.allowFrom = allow;
    cfg.channels.feishu.streaming = streaming; }
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
  { const enabled   = document.getElementById('ch-email-enabled').checked;
    const imap      = document.getElementById('ch-email-imap').value.trim();
    const imapPort  = parseInt(document.getElementById('ch-email-imap-port').value) || null;
    const smtp      = document.getElementById('ch-email-smtp').value.trim();
    const smtpPort  = parseInt(document.getElementById('ch-email-smtp-port').value) || null;
    const addr      = document.getElementById('ch-email-addr').value.trim();
    const pass      = document.getElementById('ch-email-pass').value.trim();
    const allow     = strToAllow(document.getElementById('ch-email-allow').value);
    const verifyDkim = document.getElementById('ch-email-verify-dkim').checked;
    const verifySpf  = document.getElementById('ch-email-verify-spf').checked;
    if (!cfg.channels.email) cfg.channels.email = {};
    cfg.channels.email.enabled = enabled;
    if (imap) cfg.channels.email.imapHost = imap;
    if (imapPort) cfg.channels.email.imapPort = imapPort;
    if (smtp) cfg.channels.email.smtpHost = smtp;
    if (smtpPort) cfg.channels.email.smtpPort = smtpPort;
    if (addr) cfg.channels.email.email    = addr;
    if (pass) cfg.channels.email.password = pass;
    cfg.channels.email.allowFrom  = allow;
    cfg.channels.email.verifyDkim = verifyDkim;
    cfg.channels.email.verifySpf  = verifySpf; }

  // ③ 高级
  const workspace    = document.getElementById('cfg-workspace').value.trim();
  const timezone     = document.getElementById('cfg-timezone').value.trim();
  const maxTokens    = parseInt(document.getElementById('cfg-max-tokens').value) || null;
  const ctxWindow    = parseInt(document.getElementById('cfg-context-window').value) || null;
  const maxIter      = parseInt(document.getElementById('cfg-max-iterations').value) || null;
  const reasoningEff = document.getElementById('cfg-reasoning-effort').value || null;
  const proxy        = document.getElementById('cfg-proxy').value.trim();
  const execEn       = document.getElementById('cfg-exec-enable').checked;
  const sendProgress = document.getElementById('cfg-send-progress').checked;
  const sendToolHints = document.getElementById('cfg-send-tool-hints').checked;
  if (workspace) cfg.agents.defaults.workspace = workspace;
  if (timezone)  cfg.agents.defaults.timezone  = timezone;
  else delete cfg.agents.defaults.timezone;
  if (maxTokens) cfg.agents.defaults.maxTokens = maxTokens;
  if (ctxWindow) cfg.agents.defaults.contextWindowTokens = ctxWindow;
  if (maxIter)   cfg.agents.defaults.maxToolIterations = maxIter;
  cfg.agents.defaults.reasoningEffort = reasoningEff;
  if (!cfg.tools) cfg.tools = {};
  if (!cfg.tools.web) cfg.tools.web = {};
  cfg.tools.web.proxy = proxy || null;
  if (!cfg.tools.exec) cfg.tools.exec = {};
  cfg.tools.exec.enable = execEn;
  cfg.channels.sendProgress   = sendProgress;
  cfg.channels.sendToolHints  = sendToolHints;
  // MCP servers
  cfg.tools.mcpServers = collectMcpServers();

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

// ── MCP Servers ──────────────────────────────────────────────────────────────

let _mcpServers = {};  // name → config object

function renderMcpList(servers) {
  _mcpServers = JSON.parse(JSON.stringify(servers || {}));
  const el = document.getElementById('mcp-server-list');
  const names = Object.keys(_mcpServers);
  if (names.length === 0) {
    el.innerHTML = '<div class="empty" style="padding:16px 0">暂未配置 MCP 服务器</div>';
    return;
  }
  el.innerHTML = names.map(name => _renderMcpEntry(name, _mcpServers[name])).join('');
}

function _renderMcpEntry(name, cfg) {
  const type = cfg.type || (cfg.url ? 'sse' : 'stdio');
  const isStdio = type === 'stdio';
  const argsStr = (cfg.args || []).join(' ');
  const envStr = Object.entries(cfg.env || {}).map(([k,v]) => `${k}=${v}`).join('\n');
  const headersStr = Object.entries(cfg.headers || {}).map(([k,v]) => `${k}: ${v}`).join('\n');
  const enabledTools = (cfg.enabledTools || cfg.enabled_tools || ['*']).join(', ');
  return `
  <div class="channel-block" id="mcp-block-${name}">
    <div class="channel-header" onclick="toggleMcpEntry('${name}')">
      <span class="channel-icon">🔌</span>
      <span class="channel-name" style="font-family:monospace">${name}</span>
      <span class="badge ${isStdio ? 'gray' : 'amber'}" style="font-size:11px;margin-right:8px">${type}</span>
      <button class="btn btn-red" style="font-size:11px;padding:3px 8px" onclick="event.stopPropagation();deleteMcpServer('${name}')">删除</button>
      <span class="channel-arrow" id="mcp-arrow-${name}">▶</span>
    </div>
    <div class="channel-body" id="mcp-body-${name}" style="display:none">
      <div class="form-group">
        <label class="form-label">类型</label>
        <select id="mcp-type-${name}" class="form-select" onchange="onMcpTypeChange('${name}')">
          <option value="stdio" ${isStdio ? 'selected' : ''}>stdio（本地命令）</option>
          <option value="sse" ${type==='sse' ? 'selected' : ''}>SSE（HTTP 事件流）</option>
          <option value="streamableHttp" ${type==='streamableHttp' ? 'selected' : ''}>StreamableHttp</option>
        </select>
      </div>
      <div id="mcp-stdio-${name}" style="display:${isStdio ? 'block' : 'none'}">
        <div class="form-group">
          <label class="form-label">命令 <span class="form-hint">如 npx、uvx、python</span></label>
          <input id="mcp-cmd-${name}" type="text" class="form-input" placeholder="npx" value="${(cfg.command||'').replace(/"/g,'&quot;')}">
        </div>
        <div class="form-group">
          <label class="form-label">参数 <span class="form-hint">空格分隔，如 -y @modelcontextprotocol/server-filesystem /path</span></label>
          <input id="mcp-args-${name}" type="text" class="form-input" placeholder="-y @modelcontextprotocol/server-xxx" value="${argsStr.replace(/"/g,'&quot;')}">
        </div>
        <div class="form-group">
          <label class="form-label">环境变量 <span class="form-hint">每行一个，格式 KEY=VALUE</span></label>
          <textarea id="mcp-env-${name}" class="form-input" rows="3" placeholder="API_KEY=sk-xxx">${envStr}</textarea>
        </div>
      </div>
      <div id="mcp-http-${name}" style="display:${isStdio ? 'none' : 'block'}">
        <div class="form-group">
          <label class="form-label">URL <span class="form-hint">SSE 或 HTTP 端点地址</span></label>
          <input id="mcp-url-${name}" type="text" class="form-input" placeholder="https://example.com/mcp" value="${(cfg.url||'').replace(/"/g,'&quot;')}">
        </div>
        <div class="form-group">
          <label class="form-label">请求头 <span class="form-hint">每行一个，格式 Key: Value</span></label>
          <textarea id="mcp-headers-${name}" class="form-input" rows="3" placeholder="Authorization: Bearer sk-xxx">${headersStr}</textarea>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">工具超时（秒） <span class="form-hint">默认 30</span></label>
        <input id="mcp-timeout-${name}" type="number" class="form-input" placeholder="30" min="1" max="300" value="${cfg.toolTimeout || cfg.tool_timeout || ''}">
      </div>
      <div class="form-group">
        <label class="form-label">启用的工具 <span class="form-hint">逗号分隔；* 表示全部启用</span></label>
        <input id="mcp-tools-${name}" type="text" class="form-input" placeholder="*" value="${enabledTools}">
      </div>
    </div>
  </div>`;
}

function toggleMcpEntry(name) {
  const body  = document.getElementById('mcp-body-' + name);
  const arrow = document.getElementById('mcp-arrow-' + name);
  const open  = body.style.display === 'none';
  body.style.display = open ? 'block' : 'none';
  arrow.classList.toggle('open', open);
}

function onMcpTypeChange(name) {
  const type = document.getElementById('mcp-type-' + name).value;
  const isStdio = type === 'stdio';
  document.getElementById('mcp-stdio-' + name).style.display = isStdio ? 'block' : 'none';
  document.getElementById('mcp-http-' + name).style.display  = isStdio ? 'none' : 'block';
}

function addMcpServer() {
  const name = prompt('MCP 服务器名称（英文，如 filesystem）:');
  if (!name || !name.trim()) return;
  const safeName = name.trim().replace(/[^a-zA-Z0-9_-]/g, '_');
  if (_mcpServers[safeName]) { alert('已存在同名服务器'); return; }
  _mcpServers[safeName] = { type: 'stdio', command: '', args: [], env: {} };
  const el = document.getElementById('mcp-server-list');
  const tmp = document.createElement('div');
  tmp.innerHTML = _renderMcpEntry(safeName, _mcpServers[safeName]);
  el.appendChild(tmp.firstElementChild);
  // Expand the new entry
  const body  = document.getElementById('mcp-body-' + safeName);
  const arrow = document.getElementById('mcp-arrow-' + safeName);
  if (body) { body.style.display = 'block'; }
  if (arrow) { arrow.classList.add('open'); }
  // Clear empty message
  const empty = el.querySelector('.empty');
  if (empty) empty.remove();
}

function deleteMcpServer(name) {
  if (!confirm(`确定删除 MCP 服务器「${name}」？`)) return;
  delete _mcpServers[name];
  const block = document.getElementById('mcp-block-' + name);
  if (block) block.remove();
  const el = document.getElementById('mcp-server-list');
  if (!el.querySelector('.channel-block')) {
    el.innerHTML = '<div class="empty" style="padding:16px 0">暂未配置 MCP 服务器</div>';
  }
}

function _parseEnvText(text) {
  const env = {};
  for (const line of text.split('\n')) {
    const idx = line.indexOf('=');
    if (idx > 0) {
      env[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }
  return env;
}

function _parseHeadersText(text) {
  const h = {};
  for (const line of text.split('\n')) {
    const idx = line.indexOf(':');
    if (idx > 0) {
      h[line.slice(0, idx).trim()] = line.slice(idx + 1).trim();
    }
  }
  return h;
}

function collectMcpServers() {
  const result = {};
  for (const name of Object.keys(_mcpServers)) {
    const type    = (document.getElementById('mcp-type-' + name) || {}).value || 'stdio';
    const isStdio = type === 'stdio';
    const timeout = parseInt((document.getElementById('mcp-timeout-' + name) || {}).value) || null;
    const toolsVal = ((document.getElementById('mcp-tools-' + name) || {}).value || '*').trim();
    const enabledTools = toolsVal.split(',').map(s => s.trim()).filter(Boolean);
    if (isStdio) {
      const cmd     = ((document.getElementById('mcp-cmd-' + name) || {}).value || '').trim();
      const argsRaw = ((document.getElementById('mcp-args-' + name) || {}).value || '').trim();
      const args    = argsRaw ? argsRaw.split(/\s+/) : [];
      const envRaw  = ((document.getElementById('mcp-env-' + name) || {}).value || '');
      result[name] = { type, command: cmd, args, env: _parseEnvText(envRaw),
                       ...(timeout ? {toolTimeout: timeout} : {}), enabledTools };
    } else {
      const url     = ((document.getElementById('mcp-url-' + name) || {}).value || '').trim();
      const hRaw    = ((document.getElementById('mcp-headers-' + name) || {}).value || '');
      result[name] = { type, url, headers: _parseHeadersText(hRaw),
                       ...(timeout ? {toolTimeout: timeout} : {}), enabledTools };
    }
  }
  return result;
}

// ── Logs ───────────────────────────────────────────────────────────────────
let _logAutoRefreshTimer = null;
let _logFilter = 'all';
let _logRawLines = [];

const _LOG_COLORS = {
  ERROR:   'var(--red)',
  WARNING: 'var(--amber)',
  INFO:    'var(--accent)',
  DEBUG:   'var(--muted)',
  SUCCESS: 'var(--green)',
};

function _highlightLogLine(line) {
  for (const [level, color] of Object.entries(_LOG_COLORS)) {
    if (line.includes(level) || line.includes(level.toLowerCase())) {
      return `<span style="color:${color}">${line.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span>`;
    }
  }
  return line.replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function _renderFilteredLogs() {
  const el = document.getElementById('log-content');
  const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
  let lines = _logRawLines;
  if (_logFilter !== 'all') {
    const filterUpper = _logFilter.toUpperCase();
    lines = lines.filter(l => l.toUpperCase().includes(filterUpper));
  }
  if (lines.length === 0) {
    el.innerHTML = `<span style="color:var(--muted)">（无 ${_logFilter} 级别日志）</span>`;
    return;
  }
  el.innerHTML = lines.map(_highlightLogLine).join('\n');
  if (atBottom) el.scrollTop = el.scrollHeight;
}

function setLogFilter(level) {
  _logFilter = level;
  // Update button styles
  const levels = ['all', 'ERROR', 'WARNING', 'INFO', 'DEBUG'];
  for (const l of levels) {
    const btn = document.getElementById('log-filter-' + l);
    if (btn) btn.style.outline = l === level ? '2px solid var(--accent)' : 'none';
  }
  _renderFilteredLogs();
}

async function loadLogs() {
  const d = await api('/api/logs');
  _logRawLines = (d.logs || '（暂无日志）').split('\n');
  _renderFilteredLogs();
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
            # 渠道启用状态 — 直接从原始 JSON 读取，避免 Pydantic extra-fields 转换问题
            try:
                raw_cfg = json.loads(config_path.read_text(encoding="utf-8"))
                raw_channels = raw_cfg.get("channels", {})
                status["channels_enabled"] = {
                    k: bool(v.get("enabled")) if isinstance(v, dict) else False
                    for k, v in raw_channels.items()
                }
            except Exception:
                pass
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
            download_url = data.get("download_url", "")
            result["release_url"] = download_url or result["release_url"]
            if latest_tag and latest_tag != __version__ and download_url:
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
            lines = content.splitlines()[-500:]
        else:
            # Fallback: check ~/.pgflow/tray.log and ~/.pgflow/*.log
            fallbacks = [
                Path.home() / ".pgflow" / "tray.log",
                *sorted((Path.home() / ".pgflow").glob("*.log"),
                        key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True),
            ]
            for fb in fallbacks:
                if fb.exists():
                    content = fb.read_text(encoding="utf-8", errors="replace")
                    lines = content.splitlines()[-500:]
                    break
            else:
                lines = ["（日志目录为空）", f"日志目录：{logs_dir}",
                         "提示：网关运行时会自动创建日志文件"]
    except Exception as e:
        lines = [f"（无法读取日志：{e}）"]
    return {"logs": "\n".join(lines)}


# ---------------------------------------------------------------------------
# Auto-updater
# ---------------------------------------------------------------------------

_update_state: dict = {"status": "idle", "progress": 0, "message": ""}


def _get_update_status() -> dict:
    return dict(_update_state)


def _do_update(download_url: str) -> None:
    """Download zip, extract to temp dir, write updater.bat, then exit.

    The bat script runs after pgflow exits: waits 2 s, replaces _internal/ and
    pgflow.exe (all file locks released), then restarts pgflow.
    """
    import urllib.request
    import zipfile

    def _set(status: str, progress: int, message: str) -> None:
        _update_state["status"] = status
        _update_state["progress"] = progress
        _update_state["message"] = message

    try:
        _set("downloading", 5, "正在下载更新包…")

        # Only supported when running as a frozen exe
        if not getattr(sys, "frozen", False):
            _set("error", 0, "仅打包版本支持自动更新，请手动下载")
            return

        install_dir = Path(sys.executable).parent
        exe_path = Path(sys.executable)

        # Verify download URL is reachable before starting
        try:
            head_req = urllib.request.Request(
                download_url, headers={"User-Agent": "PgFlow-Updater"}, method="HEAD"
            )
            with urllib.request.urlopen(head_req, timeout=10):
                pass
        except Exception as e:
            _set("error", 0, f"更新包不可达，请前往 GitHub Releases 手动下载：{e}")
            return

        # Use a persistent temp dir (not TemporaryDirectory) so bat can access it after exit
        tmp_root = Path.home() / ".pgflow" / "update_tmp"
        if tmp_root.exists():
            import shutil as _shutil
            _shutil.rmtree(tmp_root, ignore_errors=True)
        tmp_root.mkdir(parents=True, exist_ok=True)

        zip_path = tmp_root / "update.zip"

        # Download with progress
        req = urllib.request.Request(
            download_url, headers={"User-Agent": "PgFlow-Updater"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 65536
            with open(zip_path, "wb") as f:
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        pct = 5 + int(downloaded / total * 50)
                        _set("downloading", pct, f"下载中… {downloaded // 1048576} MB / {total // 1048576} MB")

        _set("extracting", 60, "正在解压…")

        extract_dir = tmp_root / "extracted"
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # Find the top-level folder inside zip (e.g. "pgflow/")
        children = list(extract_dir.iterdir())
        src_dir = children[0] if len(children) == 1 and children[0].is_dir() else extract_dir

        src_internal = src_dir / "_internal"
        src_exe = src_dir / "pgflow.exe"

        _set("installing", 80, "正在准备更新脚本…")

        # Write updater.bat — runs after pgflow exits, replaces files, restarts
        bat_path = tmp_root / "updater.bat"
        bat_lines = [
            "@echo off",
            "timeout /t 2 /nobreak >nul",
            # Replace _internal/
        ]
        if src_internal.exists():
            bat_lines += [
                f'rd /S /Q "{install_dir}\\_internal"',
                f'xcopy /E /I /Y /Q "{src_internal}" "{install_dir}\\_internal\\"',
            ]
        if src_exe.exists():
            bat_lines += [
                # Rename running exe aside, copy new one
                f'if exist "{install_dir}\\pgflow.exe.old" del /F /Q "{install_dir}\\pgflow.exe.old"',
                f'move /Y "{install_dir}\\pgflow.exe" "{install_dir}\\pgflow.exe.old"',
                f'copy /Y "{src_exe}" "{install_dir}\\pgflow.exe"',
            ]
        bat_lines += [
            # Clean up temp dir
            f'rd /S /Q "{tmp_root}"',
            # Restart pgflow
            f'start "" "{install_dir}\\pgflow.exe"',
            "exit",
        ]
        bat_path.write_text("\r\n".join(bat_lines), encoding="gbk")

        _set("done", 100, "下载完成，PgFlow 即将退出并自动重启完成更新…")

        # Launch bat detached, then exit this process after a short delay
        import subprocess as _sp
        _sp.Popen(
            ["cmd.exe", "/C", str(bat_path)],
            creationflags=0x00000008,  # DETACHED_PROCESS
            close_fds=True,
        )

        # Give the browser time to receive the 'done' status before we exit
        import time as _time
        _time.sleep(2)
        os.kill(os.getpid(), 9)  # Hard exit — all file handles released immediately

    except Exception as e:
        _update_state["status"] = "error"
        _update_state["progress"] = 0
        _update_state["message"] = f"更新失败：{e}"


def _start_update(download_url: str) -> dict:
    if _update_state["status"] in ("downloading", "extracting", "installing"):
        return {"ok": False, "error": "正在更新中，请稍候"}
    _update_state.update({"status": "idle", "progress": 0, "message": ""})
    threading.Thread(target=_do_update, args=(download_url,), daemon=True).start()
    return {"ok": True}


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
        elif path == "/api/update/status":
            self._send_json(_get_update_status())
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
        elif path == "/api/update/start":
            self._send_json(_start_update(body.get("url", "")))
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
