# serve.py
# FastAPI app exposing: GET /recommend?user=<id>&k=<k> -> JSON list of item IDs

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import json

app = FastAPI(title="Simple Recommender API")

RECS_PATH = Path("data/recs.json")
if RECS_PATH.exists():
    with RECS_PATH.open("r", encoding="utf-8") as f:
        RECS = json.load(f)
else:
    RECS = {"_default": [101, 102, 103, 104, 105]}

@app.get("/recommend")
def recommend(user: str = Query(default="1"), k: int = Query(default=5, ge=1, le=10)):
    slate = RECS.get(user) or RECS.get("_default", [])
    return JSONResponse(content=slate[:k])
