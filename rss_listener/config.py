"""Feed configuration - list of RSS feeds to monitor."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_FEEDS = [
    # GitHub Trending (unofficial RSS via mshibanami)
    "https://rsshub.app/github/trending/daily/all",
    # Hacker News best stories
    "https://hnrss.org/best",
    # Dev.to top articles
    "https://dev.to/feed",
    # Python Package Index new releases
    "https://pypi.org/rss/updates.xml",
    # GitHub blog
    "https://github.blog/feed/",
]

CONFIG_FILE = Path(__file__).resolve().parent.parent / "feeds.json"


def load_feeds():
    """Load feed URLs from feeds.json, falling back to defaults."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        urls = data.get("feeds", [])
        if urls:
            logger.info("Loaded %d feeds from %s", len(urls), CONFIG_FILE)
            return urls

    logger.info("Using %d default feeds", len(DEFAULT_FEEDS))
    return DEFAULT_FEEDS


def save_default_config():
    """Write the default feed config to feeds.json."""
    data = {"feeds": DEFAULT_FEEDS}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Wrote default config to %s", CONFIG_FILE)
