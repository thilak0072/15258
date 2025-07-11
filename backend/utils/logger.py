import os
import httpx

ACCESS_TOKEN = os.getenv("AUTH_TOKEN", "").strip()

print("[logger] AUTH_TOKEN preview:", ACCESS_TOKEN[:15] + "..." if ACCESS_TOKEN else "None")

async def log(stack, level, package, message):
    if not ACCESS_TOKEN:
        print("[logger] No AUTH_TOKEN set!")
        return
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": message,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("http://20.244.56.144/evaluation-service/logs", json=payload, headers=headers)
        if r.status_code == 200:
            print("[logger] Log sent OK")
        else:
            print(f"[logger] Failed to send log: {r.status_code} - {r.text}")
