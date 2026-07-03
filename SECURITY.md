# Security Policy

## Secret handling

This project talks to several paid APIs (Telegram, Fireworks, Google Gemini, Tavily, SerpAPI, Firecrawl). Their credentials must **never** be committed to the repository.

- All secrets live in a local `.env` file, which is listed in `.gitignore`.
- Use `.env.example` as the template — it contains variable names only, no values.
- The Docker image does **not** bake secrets in; provide them at runtime with `docker run --env-file .env ...`.
- The bot validates required secrets at startup and fails fast with a clear message if any are missing.

## If a key is exposed

If an API key or bot token is ever committed or leaked, treat it as compromised and rotate it **immediately**:

| Credential          | Where to rotate                                                        |
|---------------------|------------------------------------------------------------------------|
| `BOT_TOKEN`         | [@BotFather](https://t.me/BotFather) → `/revoke` → issue a new token    |
| `FIREWORKS_API_KEY` | https://fireworks.ai/account/api-keys                                  |
| `GEMINI_API_KEYS`   | https://aistudio.google.com/apikey                                     |
| `TAVILY_API_KEY`    | https://app.tavily.com                                                 |
| `SERPAPI_KEY`       | https://serpapi.com/manage-api-key                                     |
| `FIRECRAWL_API_KEY` | https://firecrawl.dev/app                                              |

Rotating at the provider is the only thing that actually protects you — removing a key from git history does **not** invalidate the key itself.

## Reporting a vulnerability

If you discover a security issue, please open a private report via GitHub's security advisories, or contact the repository owner directly rather than filing a public issue.
