from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
import random, string, os
from dotenv import load_dotenv

from utils.logger import log

load_dotenv()  # Load .env before anything else

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

urls_db, clicks_db = {}, {}

def gen_code():
    while True:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if code not in urls_db:
            return code

class ShortenReq(BaseModel):
    url: HttpUrl
    validity: int = 30
    shortcode: str | None = None

class ShortLinkRes(BaseModel):
    shortLink: str
    expiry: str

@app.post("/shorturls", response_model=ShortLinkRes, status_code=201)
async def create(data: ShortenReq):
    await log("backend", "info", "route", f"Create request for {data.url}")
    code = data.shortcode or gen_code()

    if data.shortcode:
        if not code.isalnum() or len(code) > 20:
            await log("backend", "error", "handler", f"Invalid shortcode '{code}'")
            raise HTTPException(400, "Custom shortcode invalid")
        if code in urls_db:
            await log("backend", "error", "handler", f"Duplicate shortcode '{code}'")
            raise HTTPException(400, "Shortcode already exists")

    expiry = datetime.utcnow() + timedelta(minutes=data.validity)
    urls_db[code] = {"url": str(data.url), "created": datetime.utcnow(), "expiry": expiry}
    clicks_db[code] = []
    await log("backend", "info", "route", f"Shortcode '{code}' created")

    return ShortLinkRes(shortLink=f"http://localhost:8000/{code}", expiry=expiry.isoformat())

@app.get("/shorturls/{code}")
async def stats(code: str):
    await log("backend", "info", "route", f"Stats request for {code}")
    if code not in urls_db:
        await log("backend", "warn", "handler", f"Stats not found {code}")
        raise HTTPException(404, "Shortcode not found")

    rec = urls_db[code]
    return {
      "original_url": rec["url"],
      "created_at": rec["created"].isoformat(),
      "expiry": rec["expiry"].isoformat(),
      "total_clicks": len(clicks_db[code]),
      "clicks": clicks_db[code]
    }

@app.get("/{code}")
async def redirect_endpoint(code: str, request: Request):
    await log("backend", "info", "route", f"Redirect request for {code}")
    if code not in urls_db:
        await log("backend", "warn", "handler", f"Redirect not found {code}")
        raise HTTPException(404, "Shortcode not found")

    rec = urls_db[code]
    if datetime.utcnow() > rec["expiry"]:
        await log("backend", "warn", "handler", f"Expired {code}")
        raise HTTPException(410, "Short URL expired")

    clicks_db[code].append({
        "timestamp": datetime.utcnow().isoformat(),
        "referrer": request.headers.get("referer"),
        "geo": request.client.host
    })
    await log("backend", "info", "route", f"Logged click for {code}")
    return RedirectResponse(rec["url"])

@app.get("/test-log")
async def test_log():
    await log("backend", "info", "utils", "Manual test log from /test-log endpoint")
    return {"status": "Log sent"}
