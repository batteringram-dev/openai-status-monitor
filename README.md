# 🚦 OpenAI Status Monitor

A lightweight, event-driven Python application that continuously monitors the OpenAI Status RSS feed and prints new incidents in real-time.

This tool is designed to:

- Detect new incidents, outages, or degradations
- Print structured, clean console logs
- Avoid inefficient polling
- Scale to monitor 100+ similar status feeds
- Run as a lightweight production-ready container

---

## ✨ Features

- ✅ Uses official RSS feed
- ✅ Async + non-blocking I/O
- ✅ Efficient conditional requests (ETag support)
- ✅ Warm start (no history spam)
- ✅ Prints only new incidents
- ✅ Cleans HTML into readable output
- ✅ Docker-ready
- ✅ Stateless & restart-safe monitoring behavior

---

## 🧠 How It Works

### On Startup
- Fetches the RSS feed
- Records the most recent incident timestamp
- Does NOT print historical entries

### While Running
- Periodically checks the RSS feed
- Uses `If-None-Match` (ETag) to avoid unnecessary downloads
- Detects if a new incident appears
- Immediately prints structured output

---

## 🖥 Example Output

----------------------------------------------------------------------
[2026-02-23 14:41:34]
Product: Increased ChatGPT error rates
Current Status: Resolved
Message: All impacted services have now fully recovered.
Affected Components:
 - Conversations (Operational)
----------------------------------------------------------------------

---

## Docker Usage

- `docker build -t openai-status-monitor .`
- `docker run --rm -it openai-status-monitor`

---

## Configuration

- You can configure:
- `POLL_INTERVAL` – how often the feed is checked (seconds)
- `FEED_URL` – RSS feed endpoint

- Scaling to multiple providers:
- `FEEDS = {
    "OpenAI": "https://status.openai.com/feed.rss",
    "Stripe": "https://status.stripe.com/rss",
    "AWS": "https://status.aws.amazon.com/rss"
}
`
