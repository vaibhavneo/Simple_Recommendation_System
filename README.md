```markdown
# Recommendation Chatbot (Python · Bot Framework · FastAPI)

A small but powerful **recommendation-system chatbot** you can run locally. It:

- Replies to greetings (`hello`) and `/help`
- Returns top-K recommendations with `/recommend <userId> [k]`
- Renders results as a **Hero Card carousel** in the Bot Framework Emulator
- Can call a **local FastAPI** service for real recommendations (with a local fallback if the API is down)
- Ships with a simple **hybrid recommender** you can tweak (content TF-IDF + item co-occurrence + optional MMR diversity)
---

## 🗂️ Repository Structure

```
.
├─ bot_app.py           # Bot Framework (aiohttp) app: routes + message handling + Hero cards
├─ serve.py             # FastAPI service exposing /recommend (uses recommender.py)
├─ recommender.py       # Hybrid recommender (content + item-item co-occurrence + MMR diversity)
├─ train.py             # (Optional) example script to precompute artifacts/popularity
├─ requirements.txt     # Dependencies
├─ data/
│  ├─ catalog.csv       # Demo catalog (auto-created if missing)
│  └─ interactions.csv  # Demo interactions (auto-created if missing)
└─ README.md

````

> `data/catalog.csv` and `data/interactions.csv` are **auto-seeded** the first time you run if they are missing.

---

## 🚀 Quick Start

### 1) Create & activate a virtual environment

**Conda**
```bash
conda create -y -n bf311 python=3.11
conda activate bf311
````

**venv**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Start the Recommendation API (port **8000**)

```bash
python serve.py
```

* Endpoint: `GET http://127.0.0.1:8000/recommend?user=<id>&k=<k>`
* Test:

```bash
curl "http://127.0.0.1:8000/recommend?user=1&k=3"
```

### 4) Start the Bot (port **3978**)

Open a **second** terminal (keep the API running) and run:

```bash
set PORT=3978
set MicrosoftAppId=
set MicrosoftAppPassword=
python bot_app.py
```

> For local Emulator testing **leave AppId/Password empty**.

### 5) Connect with the Bot Framework Emulator

1. Open **Bot Framework Emulator**
2. **Open Bot** → URL: `http://localhost:3978/api/messages`
3. In Emulator **Settings**, **uncheck** “Use version 1.0 authentication tokens”.

### 6) Try messages

```
hello
/help
/recommend 1
/recommend 1 5
```

If the API is down, the bot still responds using a local deterministic fallback.

---

## 💬 Bot Commands

* `hello` — simple echo + tip
* `/help` — list commands and examples
* `/recommend <userId>` — return top-3
* `/recommend <userId> <k>` — return top-K

  * Edge cases (non-int ID, negative/zero/very large `k`) are handled gracefully (clamped to safe defaults).
  * Unknown users are handled with **popularity backfill** (no errors).

---

## 🧠 Recommender (how it works)

Implemented in **`recommender.py`**:

* **Content-based**: TF-IDF on `title + tags + description` → cosine similarity
* **Collaborative**: item-item **co-occurrence cosine** from implicit interactions
* **Hybrid blend**: `score = α * collaborative + (1-α) * content`
* **Backfill**: global popularity for **cold-start** users
* **MMR diversity** (optional): Maximal Marginal Relevance to reduce near-duplicates

Tunable via `HybridConfig`:

* `alpha` (blend), `mmr_lambda` (diversity), `k_neighbors`, etc.

The first run seeds demo data into `data/` if not present; replace with your own CSVs to customize.

---

## 🖼️ UI: Hero Card Carousel

Each recommendation is shown as a **Hero Card** with:

* Title: `Recommended item #<id>`
* Subtitle/description
* Image (placeholder included; replace with your real URLs)
* **View** button (placeholder link; wire to PDP/landing pages as needed)

---

## 🔧 Customization

* Replace/extend `data/catalog.csv` and `data/interactions.csv` with your data.
* Tweak `HybridConfig` in `recommender.py` (e.g., `alpha`, `mmr_lambda`).
* Use `train.py` to precompute or export artifacts (e.g., popularity tables).
* Map real product images/links when building cards in `bot_app.py`.

---

## 🧪 Testing

**API**

```bash
curl "http://127.0.0.1:8000/recommend?user=1&k=3"
```

**Bot (Emulator)**

```
/recommend 1 3
```

Expect a **3-card carousel** reply.

---

## 🩺 Troubleshooting

* **Emulator shows 400 / cannot connect**

  * Ensure bot is running at `http://localhost:3978/api/messages`.
  * In Emulator Settings, **disable 1.0 auth tokens**.
* **`service_url can not be None`**

  * Use the Emulator to open the bot (don’t POST manually to `/api/messages`).
* **API timeout**

  * Start `serve.py` first. If it’s down, the bot will still reply using fallback IDs.
* **Weird K values**

  * Negative/zero/very large `k` are clamped; you should still get a valid response.

---

## 📦 Requirements

See `requirements.txt`. Core libraries include:

* `botbuilder-core`, `aiohttp`
* `fastapi`, `uvicorn`
* `scikit-learn`, `pandas`, `numpy`

Install with:

```bash
pip install -r requirements.txt
```

---

## 📜 License & Credits

MIT (or your course’s required license).
Thanks to:

* Microsoft **Bot Framework** (Python SDK)
* **FastAPI** & **Uvicorn**
* **Scikit-learn**, **Pandas**, **NumPy**

Helpful Links:

* Bot Framework Emulator: [https://github.com/microsoft/BotFramework-Emulator](https://github.com/microsoft/BotFramework-Emulator)
* FastAPI: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
* BotBuilder (Python): [https://github.com/microsoft/botbuilder-python](https://github.com/microsoft/botbuilder-python)

```
```

