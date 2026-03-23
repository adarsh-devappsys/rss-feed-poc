"""RSS feed parser - fetches and parses RSS/Atom feeds using stdlib xml."""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

logger = logging.getLogger(__name__)

# Common Atom namespace
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def parse_feed(feed_url):
    """Fetch and parse an RSS/Atom feed, returning a list of entries."""
    logger.info("Fetching feed: %s", feed_url)

    try:
        resp = requests.get(feed_url, timeout=30, headers={"User-Agent": "RSS-Listener/1.0"})
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error("Failed to fetch %s: %s", feed_url, e)
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        logger.error("Failed to parse XML from %s: %s", feed_url, e)
        return []

    # Detect feed type and parse accordingly
    if root.tag == "rss":
        return _parse_rss(root, feed_url)
    if root.tag in (f"{ATOM_NS}feed", "feed"):
        return _parse_atom(root, feed_url)

    logger.warning("Unknown feed format at %s (root tag: %s)", feed_url, root.tag)
    return []


def _parse_rss(root, feed_url):
    """Parse RSS 2.0 feed."""
    channel = root.find("channel")
    if channel is None:
        return []

    feed_title = _text(channel, "title") or feed_url
    entries = []

    for item in channel.findall("item"):
        entries.append({
            "title": _text(item, "title") or "Untitled",
            "link": _text(item, "link") or "",
            "summary": _clean_summary(_text(item, "description") or ""),
            "published": _text(item, "pubDate") or datetime.now().isoformat(),
            "feed_source": feed_title,
            "author": _text(item, "author") or _text(item, "dc:creator") or "Unknown",
            "tags": [cat.text for cat in item.findall("category") if cat.text],
        })

    logger.info("Parsed %d entries from %s", len(entries), feed_url)
    return entries


def _parse_atom(root, feed_url):
    """Parse Atom feed."""
    ns = ATOM_NS if root.tag.startswith("{") else ""
    feed_title = _text(root, f"{ns}title") or feed_url
    entries = []

    for entry in root.findall(f"{ns}entry"):
        link_el = entry.find(f"{ns}link[@rel='alternate']")
        if link_el is None:
            link_el = entry.find(f"{ns}link")
        link = link_el.get("href", "") if link_el is not None else ""

        author_el = entry.find(f"{ns}author/{ns}name")
        author = author_el.text if author_el is not None else "Unknown"

        entries.append({
            "title": _text(entry, f"{ns}title") or "Untitled",
            "link": link,
            "summary": _clean_summary(_text(entry, f"{ns}summary") or _text(entry, f"{ns}content") or ""),
            "published": _text(entry, f"{ns}published") or _text(entry, f"{ns}updated") or datetime.now().isoformat(),
            "feed_source": feed_title,
            "author": author,
            "tags": [cat.get("term", "") for cat in entry.findall(f"{ns}category") if cat.get("term")],
        })

    logger.info("Parsed %d entries from %s", len(entries), feed_url)
    return entries


def _text(parent, tag):
    """Safely get text content of a child element."""
    el = parent.find(tag)
    return el.text.strip() if el is not None and el.text else None


def _clean_summary(summary):
    """Truncate summary to a reasonable length."""
    if len(summary) > 500:
        return summary[:497] + "..."
    return summary
