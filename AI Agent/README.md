# Beijing Daily Outfit Email Agent

每天早上 8:00（默认 Asia/Shanghai）读取北京天气，生成穿搭建议（含鼓励话语），并通过邮箱发送。

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Configure

```bash
cp .env.example .env
```

编辑 `.env`，填写以下必需项：

### 必需配置

- `RECIPIENT_EMAIL` - 接收邮件的地址
- `SMTP_USER` - SMTP 登录用户名（通常是你的邮箱地址）
- `SMTP_PASSWORD` - SMTP 密码（Gmail 建议使用应用专用密码）
- `SMTP_FROM` - 发件人地址
- `CITY_NAME` - 城市名称（默认：Beijing）

### 可选配置

- `CITY_LAT` / `CITY_LON` - 城市经纬度（填写后可跳过地名解析）
- `LLM_API_KEY` - LLM API 密钥（用于增强穿搭建议）
- `LLM_MODEL` - 模型名称（默认：gpt-4o-mini）
- `LLM_BASE_URL` - API 基础 URL（第三方服务需要）

### Gmail 配置说明

1. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
2. 启用两步验证
3. 生成应用专用密码
4. 将生成的 16 位密码填入 `SMTP_PASSWORD`

**⚠️ 安全提醒**：永远不要将 `.env` 文件提交到版本控制系统！

## 3. Run once (test)

```bash
PYTHONPATH=src python3 -m agent.main
```

## 4. Run as daily scheduler

```bash
PYTHONPATH=src python3 -m agent.scheduler
```

默认每天 `08:00` 发送，可通过 `.env` 中：

- `SCHEDULE_HOUR`
- `SCHEDULE_MINUTE`
- `TIMEZONE`

调整定时。

## 5. Connectivity health check (recommended)

如果你遇到超时，先跑：

```bash
PYTHONPATH=src python3 -m agent.healthcheck
```

它会检测天气 API 和 SMTP 的 DNS/TCP 连通性，能快速定位是网络问题还是配置问题。

单独验证 LLM 是否可用：

```bash
PYTHONPATH=src python3 -m agent.llm_check
```

## 6. Optional: switch different LLM models/providers

Agent 支持 OpenAI 兼容接口，优先读取：

- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_BASE_URL`（可留空，留空即默认 OpenAI 官方地址；第三方通常要带 `/v1`）
- `LLM_STRICT_MODE`（`true` 时模型失败会直接报错，不再静默兜底）

示例（OpenAI 官方）：

```env
LLM_API_KEY=sk-xxx
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=
```

示例（第三方 OpenAI 兼容网关）：

```env
LLM_API_KEY=your_key
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.example.com/v1
```

如果模型调用失败，会自动回退到规则推荐，保证任务不中断。
