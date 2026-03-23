"""Feed listener - polls RSS feeds on a schedule and stores new entries."""

import logging
import signal
import sys
import time

import schedule

from rss_listener.parser import parse_feed
from rss_listener.storage import add_new_entries

logger = logging.getLogger(__name__)

_running = True


def _handle_signal(signum, frame):
    global _running
    logger.info("Received signal %d, shutting down...", signum)
    _running = False


def poll_feeds(feed_urls):
    """Fetch all configured feeds and store new entries."""
    total_new = 0
    for url in feed_urls:
        try:
            entries = parse_feed(url)
            new_count = add_new_entries(entries)
            total_new += new_count
            if new_count:
                logger.info("[+] %d new entries from %s", new_count, url)
        except Exception:
            logger.exception("Error polling feed: %s", url)

    logger.info("Poll complete. %d new entries total.", total_new)
    return total_new


def run_once(feed_urls):
    """Run a single poll of all feeds."""
    return poll_feeds(feed_urls)


def run_scheduled(feed_urls, interval_minutes=10):
    """Poll feeds on a recurring schedule."""
    global _running
    _running = True

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logger.info("Starting scheduled listener (every %d min)", interval_minutes)
    logger.info("Feeds: %s", feed_urls)

    # Run immediately on start
    poll_feeds(feed_urls)

    schedule.every(interval_minutes).minutes.do(poll_feeds, feed_urls)

    while _running:
        schedule.run_pending()
        time.sleep(1)

    logger.info("Listener stopped.")
