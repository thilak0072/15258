import httpx
import asyncio

# Your access token (replace with your actual token)
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJyYWp0aGlsYWs0ODRAZ21haWwuY29tIiwiZXhwIjoxNzUyMjExNTU0LCJpYXQiOjE3NTIyMTA2NTQsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiI3ODY2NjczZS1jNGViLTRiODktODhjNi1jMWQxYjU2NTEyMjciLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJ0aGlsYWtyYWogaiIsInN1YiI6IjkzNzQzMjI1LTAyYzktNDNiMi05ZTQwLTIxYjk2NjZhMGM4MSJ9LCJlbWFpbCI6InJhanRoaWxhazQ4NEBnbWFpbC5jb20iLCJuYW1lIjoidGhpbGFrcmFqIGoiLCJyb2xsTm8iOiIxNTI1OCIsImFjY2Vzc0NvZGUiOiJDV2JxZ0siLCJjbGllbnRJRCI6IjkzNzQzMjI1LTAyYzktNDNiMi05ZTQwLTIxYjk2NjZhMGM4MSIsImNsaWVudFNlY3JldCI6IkF6TXBjZmpIcUR3Z0tDeHMifQ.a6ReLrH7qB6Xhpt-HvPOcASHCo56MgS_7W5N4LEQSOE"

LOGGING_API_URL = "http://20.244.56.144/evaluation-service/logs"

async def log(stack: str, level: str, package: str, message: str):
    headers = {
        "Authorization": f"{ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    json_data = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(LOGGING_API_URL, headers=headers, json=json_data)
        if response.status_code == 200:
            print(f"[LOG] Sent: {level.upper()} - {package} - {message}")
        else:
            print(f"[LOG ERROR] Failed to send log: {response.status_code} - {response.text}")

# Optional synchronous wrapper if you want to call log() in sync code:
def log_sync(stack: str, level: str, package: str, message: str):
    asyncio.run(log(stack, level, package, message))
