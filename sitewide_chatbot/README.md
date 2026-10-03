# Sitewide Chatbot Extension

This extension adds a chatbot to all HTML pages on the FITS HCMS dev server
without modifying any existing project file.

## How it works

- `sitecustomize.py` is auto-imported by Python on startup.
- The bootstrap injects `sitewide_chatbot.middleware.SitewideChatbotMiddleware`
  into Django's middleware stack at runtime.
- The middleware:
  - injects the chatbot launcher into HTML responses
  - serves the widget assets from `__fits_chatbot__/assets/*`
  - answers chat requests from `__fits_chatbot__/api/chat`

## OpenRouter configuration

Add these to your environment or `.env`:

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_APP_NAME=FITS HCMS Site Chatbot
OPENROUTER_SITE_URL=http://127.0.0.1:8000
```

If no OpenRouter key is configured, the chatbot still answers from the local
product/page map bundled with this extension.
