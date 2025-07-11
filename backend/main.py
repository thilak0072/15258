from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from utils.logger import log  # async logging function
import asyncio
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl, validator
import re
import uuid

app = FastAPI()

# In-memory store for shortened URLs
url_store = {}

# Model for request
class ShortenRequest(BaseModel):
    url: HttpUrl
    validity: int = 30  # default 30 minutes
    shortcode: str | None = None

    @validator("validity")
    def validity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Validity must be positive integer")
        return v

    @validator("shortcode")
    def shortcode_must_be_alphanumeric(cls, v):
        if v and not re.fullmatch(r"[A-Za-z0-9]+", v):
            raise ValueError("Shortcode must be alphanumeric")
        return v


@app.post("/shorturls", status_code=201)
async def create_short_url(req: ShortenRequest):
    await log("backend", "info", "handler", f"Received request to shorten URL: {req.url}")

    # Check shortcode uniqueness or generate new one
    if req.shortcode:
        if req.shortcode in url_store:
            await log("backend", "error", "handler", f"Shortcode collision: {req.shortcode}")
            raise HTTPException(status_code=400, detail="Shortcode already exists")
        shortcode = req.shortcode
    else:
        # generate random shortcode (6 chars)
        shortcode = uuid.uuid4().hex[:6]
        while shortcode in url_store:
            shortcode = uuid.uuid4().hex[:6]

    expiry = datetime.utcnow() + timedelta(minutes=req.validity)

    url_store[shortcode] = {
        "url": str(req.url),
        "created": datetime.utcnow(),
        "expiry": expiry,
        "clicks": [],
    }

    await log("backend", "info", "handler", f"Short URL created: {shortcode} -> {req.url}")

    return {
        "shortLink": f"http://localhost:8000/{shortcode}",
        "expiry": expiry.isoformat() + "Z",
    }


@app.get("/{shortcode}")
async def redirect_short_url(shortcode: str):
    await log("backend", "info", "handler", f"Redirect request for shortcode: {shortcode}")
    record = url_store.get(shortcode)
    if not record:
        await log("backend", "warn", "handler", f"Shortcode not found: {shortcode}")
        raise HTTPException(status_code=404, detail="Shortcode not found")

    if datetime.utcnow() > record["expiry"]:
        await log("backend", "warn", "handler", f"Shortcode expired: {shortcode}")
        raise HTTPException(status_code=410, detail="Shortcode expired")

    # Record click data (minimal example)
    record["clicks"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "referrer": "N/A",  # Could capture from request headers if needed
        "location": "N/A",
    })

    return RedirectResponse(record["url"])


@app.get("/shorturls/{shortcode}")
async def get_short_url_stats(shortcode: str):
    await log("backend", "info", "handler", f"Stats request for shortcode: {shortcode}")
    record = url_store.get(shortcode)
    if not record:
        await log("backend", "warn", "handler", f"Shortcode not found for stats: {shortcode}")
        raise HTTPException(status_code=404, detail="Shortcode not found")

    return {
        "url": record["url"],
        "created": record["created"].isoformat() + "Z",
        "expiry": record["expiry"].isoformat() + "Z",
        "clicks_count": len(record["clicks"]),
        "clicks": record["clicks"],
    }
