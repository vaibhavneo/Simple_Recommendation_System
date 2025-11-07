# train.py
# Creates data/recs.json with simple, deterministic "top items" per user.

import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUT = DATA_DIR / "recs.json"

# Tiny toy "history" (items a user already interacted with)
user_history = {
    "1": [101, 103],   # user 1 saw/liked 101, 103
    "2": [102],        # user 2 saw 102
    "3": [],           # user 3 is new
}

# Global "popular" items (fallback base)
popular = [101, 102, 103, 104, 105, 106, 107]

# Build per-user recommended list = popular items minus ones already seen
user_recs = {}
for uid, seen in user_history.items():
    seen_set = set(seen)
    slate = [iid for iid in popular if iid not in seen_set]
    # keep top 10 to be safe
    user_recs[uid] = slate[:10]

# Also include a default (for unknown users)
user_recs["_default"] = popular[:10]

with OUT.open("w", encoding="utf-8") as f:
    json.dump(user_recs, f, indent=2)

print(f"Wrote {OUT.resolve()}")
