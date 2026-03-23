#!/usr/bin/env python3
"""RSS Feed Listener - Polls RSS feeds and collects project/article data.

Usage:
    python main.py                  # One-time poll of all feeds
    python main.py --listen         # Continuous polling (every 10 min)
    python main.py --listen -i 5    # Continuous polling (every 5 min)
    python main.py --init-config    # Generate default feeds.json
    python main.py --show           # Display stored entries
"""

import argparse
import json
import logging
import sys

from rss_listener.config import load_feeds, save_default_config
from rss_listener.listener import run_once, run_scheduled
from rss_listener.storage import load_entries


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def show_entries():
    """Print stored feed entries in a readable format."""
    entries = load_entries()
    if not entries:
        print("No entries stored yet. Run a poll first.")
        return

    print(f"\n{'='*70}")
    print(f" Stored Feed Entries ({len(entries)} total)")
    print(f"{'='*70}\n")

    for i, entry in enumerate(entries, 1):
        print(f"  [{i}] {entry['title']}")
        print(f"      Source:    {entry.get('feed_source', 'N/A')}")
        print(f"      Author:   {entry.get('author', 'N/A')}")
        print(f"      Link:     {entry.get('link', 'N/A')}")
        print(f"      Date:     {entry.get('published', 'N/A')}")
        if entry.get("tags"):
            print(f"      Tags:     {', '.join(entry['tags'])}")
        if entry.get("summary"):
            summary = entry["summary"][:120]
            print(f"      Summary:  {summary}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="RSS Feed Listener - Collect data from RSS feeds"
    )
    parser.add_argument(
        "--listen",
        action="store_true",
        help="Run in continuous listening mode",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=10,
        help="Polling interval in minutes (default: 10)",
    )
    parser.add_argument(
        "--init-config",
        action="store_true",
        help="Generate default feeds.json config file",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display all stored entries",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.init_config:
        save_default_config()
        print("Created feeds.json with default feeds. Edit it to customize.")
        return

    if args.show:
        show_entries()
        return

    feed_urls = load_feeds()

    if args.listen:
        print(f"Listening to {len(feed_urls)} feeds every {args.interval} min...")
        print("Press Ctrl+C to stop.\n")
        run_scheduled(feed_urls, args.interval)
    else:
        print(f"Polling {len(feed_urls)} feeds (one-time)...\n")
        new_count = run_once(feed_urls)
        print(f"\nDone. {new_count} new entries collected.")
        print("Run with --show to view entries, or --listen for continuous mode.")


if __name__ == "__main__":
    main()
