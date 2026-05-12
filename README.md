# Telegram Bot Ovasenka

A multi-model AI assistant Telegram bot powered by multiple LLM providers with internet search capabilities.

## Features

- **Direct Messages** - Chat with the bot in private messages
- **Group Support** - Use the bot in group chats (mention or reply to trigger)
- **Inline Mode** - Use the bot inline from any chat
- **Multi-Model Support** - Switch between different LLM providers
- **Internet Search** - Automatic web search when queries need real-time information
- **Conversation History** - Maintains context across messages

## Supported Models

| Model | Provider | Capabilities |
|-------|----------|-------------|
| DeepSeek V4 | Fireworks | Chat, Tool Use |
| Kimi K2.6 | Fireworks | Chat, Tool Use |
| GLM 5.1 | Fireworks | Chat, Tool Use |
| Qwen 3.6 Plus | Fireworks | Chat, Tool Use |
| Gemini Flash | Google | Chat, Tool Use |

## Setup

### Prerequisites

- Python 3.11+
- Telegram Bot Token (from @BotFather)
- API keys for LLM providers

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/telegrambotovasenka.git
   cd telegrambotovasenka
   ```

2. Create a `.env` file with your API keys:
   ```env
   BOT_TOKEN=your_telegram_bot_token
   FIREWORKS_API_KEY=your_fireworks_key
   GEMINI_API_KEYS=key1,key2,key3,key4,key5,key6
   TAVILY_API_KEY=your_tavily_key
   FIRECRAWL_API_KEY=your_firecrawl_key
   SERPAPI_KEY=your_serpapi_key
   DEFAULT_MODEL=gemini-flash
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the bot:
   ```bash
   python run.py
   ```

## Docker Deployment

Build and run with Docker:

```bash
docker build -t telegram-bot .
docker run -d --name telegram-bot telegram-bot
```

Or mount your `.env` file at runtime:

```bash
docker run -d --name telegram-bot --env-file .env telegram-bot
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see a welcome message |
| `/help` | Show available commands and usage |
| `/model` | Select which AI model to use |
| `/clear` | Clear conversation history |
| `/search` | Perform a web search |

## Architecture

```
bot/
  config.py          - Configuration and environment loading
  models.py          - Data models (ModelInfo, Message, ChatRequest/Response)
  state.py           - In-memory user state management
  main.py            - Bot initialization and startup
  keyboards.py       - Telegram keyboard builders
  tools.py           - Tool definitions for function calling
  handlers/
    dm.py            - Direct message handlers
    group.py         - Group chat handlers
    inline.py        - Inline query handlers
  providers/
    __init__.py      - Base provider interface
    gemini.py        - Google Gemini provider with key rotation
    fireworks.py     - Fireworks AI provider
    router.py        - Routes requests to the appropriate provider
  search/
    detector.py      - Heuristic search need detection
    manager.py       - Search orchestration
    tavily.py        - Tavily search integration
    firecrawl.py     - Firecrawl web scraping
    serpapi.py       - SerpAPI search integration
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot API token from @BotFather | Yes |
| `FIREWORKS_API_KEY` | Fireworks AI API key | Yes |
| `GEMINI_API_KEYS` | Comma-separated list of Google Gemini API keys (supports rotation) | Yes |
| `TAVILY_API_KEY` | Tavily search API key | No |
| `FIRECRAWL_API_KEY` | Firecrawl API key for web scraping | No |
| `SERPAPI_KEY` | SerpAPI key for search results | No |
| `DEFAULT_MODEL` | Default model ID to use (default: `gemini-flash`) | No |

## Running Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```
