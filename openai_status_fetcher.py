import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

FEED_URL = "https://status.openai.com/feed.rss"
POLL_INTERVAL = 30  # seconds

last_seen_timestamp = None
cached_etag = None


def clean_summary(html_summary):
    soup = BeautifulSoup(html_summary, "html.parser")

    status_text = None
    for tag in soup.find_all("b"):
        if "Status:" in tag.text:
            status_text = tag.text.replace("Status:", "").strip()

    components = [li.text.strip() for li in soup.find_all("li")]

    for tag in soup.find_all(["b", "ul"]):
        tag.decompose()

    message = soup.get_text(separator=" ").strip()

    return status_text, message, components


async def fetch_feed(session):
    global cached_etag

    headers = {}
    if cached_etag:
        headers["If-None-Match"] = cached_etag

    async with session.get(FEED_URL, headers=headers) as response:
        if response.status == 304:
            return None

        if response.status != 200:
            print("Error fetching feed:", response.status)
            return None

        cached_etag = response.headers.get("ETag")
        return await response.text()


def get_latest_entry(feed):
    if not feed.entries:
        return None

    # Get entry with newest published timestamp
    return max(
        feed.entries,
        key=lambda e: e.published_parsed if e.published_parsed else (0,)
    )


async def monitor():
    global last_seen_timestamp

    async with aiohttp.ClientSession() as session:

        # -------- Warm Start --------
        xml = await fetch_feed(session)
        if xml:
            feed = feedparser.parse(xml)
            latest = get_latest_entry(feed)

            if latest and latest.published_parsed:
                last_seen_timestamp = datetime(*latest.published_parsed[:6])

        print("Monitoring OpenAI status...")

        # -------- Monitoring Loop --------
        while True:
            xml = await fetch_feed(session)

            if xml:
                feed = feedparser.parse(xml)
                latest = get_latest_entry(feed)

                if latest and latest.published_parsed:
                    latest_time = datetime(*latest.published_parsed[:6])

                    if last_seen_timestamp is None or latest_time > last_seen_timestamp:
                        last_seen_timestamp = latest_time

                        status, message, components = clean_summary(latest.summary)

                        print("-" * 70)
                        print(f"[{latest_time.strftime('%Y-%m-%d %H:%M:%S')}]")
                        print(f"Product: {latest.title}")
                        print(f"Current Status: {status}")
                        print(f"Message: {message}")

                        if components:
                            print("Affected Components:")
                            for comp in components:
                                print(f" - {comp}")

                        print("-" * 70)

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(monitor())
