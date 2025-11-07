# bot_app.py
# Bot Framework aiohttp bot:
# - echo default
# - /help
# - /recommend <userId> [k]  -> calls FastAPI (or falls back) and shows Hero Card carousel

import os
from typing import List

from aiohttp import web, ClientSession, ClientTimeout

from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    ActivityHandler,
    MessageFactory,
    CardFactory,
)
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes,
)

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
PORT = int(os.environ.get("PORT", "3978"))

RECOMMENDER_API_URL = os.environ.get("RECOMMENDER_API_URL", "http://127.0.0.1:8000/recommend")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
async def fetch_recs(user_id: str, k: int) -> List[int]:
    """
    Call recommender API; if unavailable, return deterministic fallback.
    """
    try:
        timeout = ClientTimeout(total=3)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(RECOMMENDER_API_URL, params={"user": user_id, "k": k}) as r:
                if r.status == 200:
                    data = await r.json()
                    # accept list or {"items": [...] }
                    items = data.get("items", data) if isinstance(data, dict) else data
                    recs = [int(x) for x in items][:k]
                    if recs:
                        return recs
    except Exception:
        pass
    # fallback if API is down or empty
    base = 100
    return list(range(base + 1, base + 1 + max(1, min(k, 10))))


def build_carousel(item_ids: List[int]):
    """
    Build Hero Card carousel from item IDs (attachments via CardFactory.hero_card).
    """
    atts = []
    for iid in item_ids:
        card = HeroCard(
            title=f"Recommended item #{iid}",
            subtitle="Sample recommendation",
            text="Tap 'View' to open a placeholder link.",
            images=[CardImage(url=f"https://picsum.photos/seed/{iid}/400/220")],
            buttons=[CardAction(type=ActionTypes.open_url, title="View", value=f"https://example.org/items/{iid}")],
        )
        atts.append(CardFactory.hero_card(card))

    if len(atts) == 1:
        return MessageFactory.attachment(atts[0])
    return MessageFactory.carousel(atts)


# ------------------------------------------------------------------
# Bot
# ------------------------------------------------------------------
class RecBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        raw = (turn_context.activity.text or "").strip()
        lo = raw.lower()

        if lo in ("/help", "help"):
            txt = (
                "Commands:\n"
                "• hello — echo\n"
                "• /help — this help\n"
                "• /recommend <userId> [k] — show a carousel (default k=5)\n"
                f"(API: {RECOMMENDER_API_URL})"
            )
            await turn_context.send_activity(txt)
            return

        if lo.startswith("/recommend"):
            parts = raw.split()
            user_id = parts[1] if len(parts) >= 2 else "1"
            try:
                k = int(parts[2]) if len(parts) >= 3 else 5
            except ValueError:
                k = 5
            k = max(1, min(k, 10))
            rec_ids = await fetch_recs(user_id, k)
            reply = build_carousel(rec_ids)
            await turn_context.send_activity(reply)
            return

        # default: echo
        await turn_context.send_activity(f"you said: {raw}")

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for m in members_added:
            if m.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hi! Type `/help` to see what I can do.")


# ------------------------------------------------------------------
# Adapter / server
# ------------------------------------------------------------------
settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)
bot = RecBot()

async def on_error(context: TurnContext, error: Exception):
    print("Bot error:", error)
    try:
        await context.send_activity("Sorry, something went wrong on my side.")
    except Exception:
        pass

adapter.on_turn_error = on_error

async def messages(req: web.Request) -> web.Response:
    if req.method != "POST":
        return web.Response(status=405, text="Method Not Allowed")
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    async def aux(turn_context: TurnContext):
        await bot.on_turn(turn_context)

    try:
        await adapter.process_activity(activity, auth_header, aux)
        return web.Response(status=200, text="OK")
    except Exception as e:
        print("Top-level error:", e)
        return web.Response(status=500, text=str(e))

async def health(req: web.Request) -> web.Response:
    return web.Response(text="Bot is running. POST /api/messages")

def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/healthz", health)
    app.router.add_post("/api/messages", messages)
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=PORT)
