"""
hash_tracker.py

This file answers one question: "Has the dataset changed since last time?"

It does this by computing a SHA-256 hash -- a unique fingerprint -- of the
file's contents. If the fingerprint matches the last one we saw, nothing
changed, so we skip uploading. If it's different (or this is the first
run), we know we need to upload.

The fingerprint history is stored in a simple local file called
pipeline_state.json -- think of it as the pipeline's memory.
"""

import hashlib
import json
import os
from datetime import datetime, timezone

STATE_FILE = "pipeline_state.json"


def compute_file_hash(filepath):
    """Reads the file in small chunks and produces a unique fingerprint
    (hash) of its exact contents. Same content = same hash, always."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def load_state():
    """Reads our 'memory' file. Returns an empty dict if it doesn't exist yet
    (i.e. this is the very first run)."""
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    """Writes our updated 'memory' back to disk."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def has_changed(dataset_name, filepath):
    """
    The core idempotency check.

    Returns (changed, current_hash):
      changed = True  -> new or modified data, should upload
      changed = False -> identical to last run, should SKIP upload
    """
    current_hash = compute_file_hash(filepath)
    state = load_state()
    last_hash = state.get(dataset_name, {}).get("file_hash")
    return (current_hash != last_hash, current_hash)


def record_upload(dataset_name, file_hash, s3_key):
    """Call this AFTER a successful upload, to remember the new fingerprint
    so next time we can correctly detect 'no change' and skip."""
    state = load_state()
    state[dataset_name] = {
        "file_hash": file_hash,
        "s3_key": s3_key,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    save_state(state)
