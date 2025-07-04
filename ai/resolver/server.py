cat > resolver/server.py <<'PY'
from fastapi import FastAPI
from pydantic import BaseModel
import httpx, datetime, re, json, os
from transformers import pipeline

MODEL_ID = os.getenv("MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")

clf = pipeline("text-classification", model=MODEL_ID, device_map="auto")
app = FastAPI()

class Req(BaseModel):
    market_id: str
    title: str
    source_url: str

def scrape(url: str) -> str:
    try:
        r = httpx.get(url, timeout=10)
        return re.sub(r'\s+', ' ', r.text)[:20_000]   # truncate
    except Exception as e:
        return f"ERROR fetching {url}: {e}"

@app.post("/resolve")
def resolve(r: Req):
    page = scrape(r.source_url)
    now  = datetime.datetime.utcnow().isoformat() + "Z"
    label = clf(f"TITLE: {r.title}\nPAGE: {page}")[0]
    outcome = "YES" if label["label"] == "POSITIVE" else "NO"
    confidence = label["score"]
    return {
        "market_id": r.market_id,
        "timestamp": now,
        "outcome": outcome,
        "confidence": confidence,
        "evidence": r.source_url
    }

@app.get("/health")
def health(): return {"ok": True}
PY