"""Simple JSON file storage for feed entries."""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _get_store_path():
    """Return path to the JSON data store."""
    DATA_DIR.mkdir(exist_ok=True)
    return DATA_DIR / "feed_entries.json"


def load_entries():
    """Load all stored entries from disk."""
    path = _get_store_path()
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_entries(entries):
    """Write entries to disk."""
    path = _get_store_path()
    with open(path, "w") as f:
        json.dump(entries, f, indent=2, default=str)
    logger.info("Saved %d entries to %s", len(entries), path)


def add_new_entries(new_entries):
    """Add entries that don't already exist (dedup by link). Returns count of new items."""
    existing = load_entries()
    existing_links = {e["link"] for e in existing}

    added = 0
    for entry in new_entries:
        if entry["link"] and entry["link"] not in existing_links:
            existing.append(entry)
            existing_links.add(entry["link"])
            added += 1

    if added:
        save_entries(existing)
        logger.info("Added %d new entries", added)

    return added
