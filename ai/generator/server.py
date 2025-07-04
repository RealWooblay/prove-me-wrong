cat > generator/server.py <<'PY'
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, os, json, re, warnings

MODEL_ID = os.getenv("MODEL_ID", "meta-llama/Meta-Llama-3-8B-Instruct")
DEVICE   = "cuda" if torch.cuda.is_available() else "cpu"

tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32,
    device_map="auto",
    low_cpu_mem_usage=True
)

app = FastAPI()

class Req(BaseModel):
    prompt: str
    tweet_url: str | None = None

SYSTEM = (
    "You are a professional prediction-market creator. "
    "Return **only** valid JSON with keys "
    "title, description, closeTimeISO, outcomes (always ['YES','NO']), "
    "initialProb (0–1)."
)

def _strip(jsonish: str) -> str:
    m = re.search(r'\{.*\}', jsonish, re.S)
    return m.group(0) if m else '{}'

@app.post("/generate")
def gen(r: Req):
    user = f"PROMPT:\n{r.prompt}\nTWEET:{r.tweet_url or 'N/A'}"
    tokens = tok.apply_chat_template(
        [{"role":"system","content":SYSTEM},
         {"role":"user","content":user}],
        return_tensors="pt"
    ).to(DEVICE)
    out = model.generate(tokens, max_new_tokens=384, temperature=0.7)
    js = _strip(tok.decode(out[0], skip_special_tokens=True))
    return json.loads(js)

@app.get("/health")      # ROFL liveness probe
def health():
    return {"ok": True}
PY