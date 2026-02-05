import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
API_BASE = "https://discord.com/api/v10"

def send_raw_v2(channel_id: int, payload: dict):
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        f"{API_BASE}/channels/{channel_id}/messages",
        headers=headers,
        json=payload
    )

    if not r.ok:
        raise RuntimeError(f"Erro API: {r.status_code} → {r.text}")
