# 🤖 Telegram AI Bot

A **modular, production-minded AI Telegram bot** designed to run on Android via **Termux** — no server, no domain, no SSL needed.

Supports **OpenAI (GPT-4o)**, **Anthropic (Claude)**, and **Google Gemini** as swappable AI backends.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 💬 Multi-turn chat | Per-user conversation history with sliding window |
| 🔁 Hot-swap providers | `/provider anthropic` switches live, no restart |
| 🔌 Extensible | Add a new AI provider in ~30 lines |
| 🛡️ Rate limiting | Per-user throttle to prevent spam |
| 📋 Rotating logs | File + stdout logging, auto-rotates at 5 MB |
| 📱 Termux-native | Runs on Android, no root required |
| 🔒 Secret-safe | All keys in `.env` only — never in source code |

---

## 📋 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | Full usage guide |
| `/reset` | Clear your conversation history |
| `/status` | Show active provider, model, history count |
| `/provider <n>` | Switch provider: `openai` / `anthropic` / `gemini` |
| `/about` | Project information |

---

## 📁 Project Structure

```
telegram-ai-bot/
├── main.py                     ← Entry point (run this)
├── requirements.txt
├── .env.example                ← Copy to .env and fill in your keys
├── .gitignore
│
├── config/
│   └── settings.py             ← All env vars loaded here (never hardcoded)
│
├── bot/
│   ├── app.py                  ← Telegram Application builder
│   ├── handlers.py             ← All command + message handlers
│   └── middleware.py           ← Rate limiting + update logging
│
├── backend/
│   └── ai_service.py           ← Conversation history, routing, error wrapping
│
├── services/
│   ├── base_provider.py        ← Abstract interface (Message, AIResponse, ProviderError)
│   ├── ai_router.py            ← Provider registry + singleton factory
│   ├── openai_provider.py      ← OpenAI / compatible (Groq, Together, Ollama…)
│   ├── anthropic_provider.py   ← Anthropic Claude
│   └── gemini_provider.py      ← Google Gemini
│
└── utils/
    ├── logger.py               ← Rotating file + stdout logger
    └── helpers.py              ← Rate limiter, message splitter, truncate
```

---

## 🚀 Termux Setup (Android)

### Step 1 — Install Termux
Download from [F-Droid](https://f-droid.org/packages/com.termux/) (**not** the Play Store version — it's outdated).

### Step 2 — Install system packages
```bash
pkg update && pkg upgrade -y
pkg install python git -y
pip install --upgrade pip
```

### Step 3 — Clone the project
```bash
git clone https://github.com/YOUR_USERNAME/telegram-ai-bot.git
cd telegram-ai-bot
```

### Step 4 — Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Configure your environment
```bash
cp .env.example .env
nano .env
```

Fill in at minimum:
- `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
- The API key for your chosen provider (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY`)
- `AI_PROVIDER` — set to `openai`, `anthropic`, or `gemini`

### Step 6 — Run
```bash
python main.py
```

---

## 🔑 API Key Reference

| Key | Where to get it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Message [@BotFather](https://t.me/BotFather) → `/newbot` |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |
| `GEMINI_API_KEY` | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `TELEGRAM_API_ID/HASH` | [my.telegram.org](https://my.telegram.org) — only needed for MTProto |

---

## 🔌 Adding a New AI Provider

1. Create `services/myprovider_provider.py`:

```python
from services.base_provider import BaseAIProvider, AIResponse, Message, ProviderError

class MyProvider(BaseAIProvider):
    @property
    def name(self) -> str:
        return "myprovider"

    async def complete(self, messages, system_prompt=None, max_tokens=1024, temperature=0.7) -> AIResponse:
        # Call your API here using httpx
        ...
        return AIResponse(text=reply, provider=self.name, model="my-model")
```

2. Register it in `services/ai_router.py`:

```python
from .myprovider_provider import MyProvider
registry["myprovider"] = MyProvider
```

3. Add any keys to `.env.example` and `config/settings.py`.

4. Set `AI_PROVIDER=myprovider` in `.env`.

---

## ⚙️ Process Management

```bash
# Run in foreground
python main.py

# Run in background (survives Termux close)
nohup python main.py > logs/nohup.log 2>&1 &

# View live logs
tail -f logs/bot.log

# Stop the background process
kill $(pgrep -f main.py)

# Check if it's running
pgrep -a python
```

---

## 🔒 Security Notes

- ✅ All secrets live in `.env` only
- ✅ `.env` is in `.gitignore` and will never be committed
- ✅ `.env.example` contains only placeholder values — safe to commit
- ✅ No secrets are hardcoded anywhere in the source
- ⚠️ Do not share your `.env` file or paste it publicly

---

## 🧩 Compatible OpenAI-format Endpoints

Set `OPENAI_BASE_URL` and `OPENAI_API_KEY` in `.env` to point at any compatible API:

| Provider | Base URL |
|---|---|
| Groq | `https://api.groq.com/openai/v1` |
| Together AI | `https://api.together.xyz/v1` |
| Ollama (local) | `http://localhost:11434/v1` |
| LM Studio | `http://localhost:1234/v1` |

---

## 📄 License

MIT — use freely, modify as needed.
