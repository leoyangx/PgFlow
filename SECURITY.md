# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in PgFlow, please report it by:

1. **DO NOT** open a public GitHub issue
2. Create a private security advisory on GitHub or contact the maintainers directly
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond to security reports within 48 hours.

## Security Best Practices

### 1. API Key Management

**CRITICAL**: Never commit API keys to version control.

```bash
# Store in config file with restricted permissions
chmod 600 ~/.pgflow/config.json
```

**Recommendations:**
- Store API keys in `~/.pgflow/config.json` with file permissions set to `0600`
- Consider using environment variables for sensitive keys
- Rotate API keys regularly
- Use separate API keys for development and production

### 2. Channel Access Control

**IMPORTANT**: Always configure `allowFrom` lists for production use.

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "YOUR_BOT_TOKEN",
      "allowFrom": ["123456789", "987654321"]
    },
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+1234567890"]
    }
  }
}
```

**Security Notes:**
- An empty `allowFrom` denies all access by default — set `["*"]` to explicitly allow everyone
- Get your Telegram user ID from `@userinfobot`
- Use full phone numbers with country code for WhatsApp
- Review access logs regularly for unauthorized access attempts

### 3. Shell Command Execution

The `exec` tool can execute shell commands. While dangerous command patterns are blocked, you should:

- Review all tool usage in agent logs
- Understand what commands the agent is running
- Use a dedicated user account with limited privileges
- Never run PgFlow as root

**Blocked patterns:**
- `rm -rf /` - Root filesystem deletion
- Fork bombs
- Filesystem formatting (`mkfs.*`)
- Raw disk writes
- Other destructive operations

### 4. File System Access

File operations have path traversal protection, but:

- Run PgFlow with a dedicated user account
- Use filesystem permissions to protect sensitive directories
- Regularly audit file operations in logs

### 5. Network Security

**API Calls:**
- All external API calls use HTTPS by default
- Timeouts are configured to prevent hanging requests

**WhatsApp Bridge:**
- The bridge binds to `127.0.0.1:3001` (localhost only, not accessible from external network)
- Set `bridgeToken` in config to enable shared-secret authentication between Python and Node.js
- Keep authentication data in `~/.pgflow/whatsapp-auth` secure (mode 0700)

### 6. Dependency Security

**Critical**: Keep dependencies updated!

```bash
# Check for vulnerable dependencies
pip install pip-audit
pip-audit
```

For Node.js dependencies (WhatsApp bridge):
```bash
cd bridge
npm audit
npm audit fix
```

### 7. Production Deployment

For production use:

1. **Set Proper Permissions**
   ```bash
   chmod 700 ~/.pgflow
   chmod 600 ~/.pgflow/config.json
   chmod 700 ~/.pgflow/whatsapp-auth
   ```

2. **Use a Dedicated User**
   ```bash
   sudo useradd -m -s /bin/bash pgflow
   sudo -u pgflow pgflow gateway
   ```

3. **Enable Logging**
   ```bash
   tail -f ~/.pgflow/logs/pgflow.log
   ```

4. **Use Rate Limiting**
   - Configure rate limits on your API providers
   - Monitor usage for anomalies
   - Set spending limits on LLM APIs

5. **Regular Updates**
   ```bash
   pip install --upgrade pgflow
   ```

### 8. Data Privacy

- **Logs may contain sensitive information** — secure log files appropriately
- **LLM providers see your prompts** — review their privacy policies
- **Chat history is stored locally** — protect the `~/.pgflow` directory
- **API keys are in plain text** — use OS keyring for production

### 9. Incident Response

If you suspect a security breach:

1. **Immediately revoke compromised API keys**
2. **Review logs for unauthorized access**
   ```bash
   grep "Access denied" ~/.pgflow/logs/pgflow.log
   ```
3. **Check for unexpected file modifications**
4. **Rotate all credentials**
5. **Update to latest version**
6. **Report the incident** to maintainers

## Security Features

### Built-in Security Controls

**Input Validation**
- Path traversal protection on file operations
- Dangerous command pattern detection
- Input length limits on HTTP requests

**Authentication**
- Allow-list based access control — empty `allowFrom` denies all; `["*"]` explicitly allows all

**Resource Protection**
- Command execution timeouts (60s default)
- Output truncation (10KB limit)
- HTTP request timeouts (10-30s)

**Secure Communication**
- HTTPS for all external API calls
- TLS for Telegram API
- WhatsApp bridge: localhost-only binding + optional token auth

## Known Limitations

**Current Security Limitations:**

1. **No Rate Limiting** — Users can send unlimited messages (add your own if needed)
2. **Plain Text Config** — API keys stored in plain text (use keyring for production)
3. **No Session Management** — No automatic session expiry
4. **Limited Command Filtering** — Only blocks obvious dangerous patterns

## Security Checklist

Before deploying PgFlow:

- [ ] API keys stored securely (not in code)
- [ ] Config file permissions set to 0600
- [ ] `allowFrom` lists configured for all channels
- [ ] Running as non-root user
- [ ] File system permissions properly restricted
- [ ] Dependencies updated to latest secure versions
- [ ] Logs monitored for security events
- [ ] Rate limits configured on API providers
- [ ] Security review of custom skills/tools

## License

See LICENSE file for details.
