import json
import os
from datetime import datetime

INVITES_FILE = "data/invites.json"

os.makedirs("data", exist_ok=True)

def load_invites():
    if not os.path.exists(INVITES_FILE):
        return []
    with open(INVITES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_invites(invites: list):
    with open(INVITES_FILE, "w", encoding="utf-8") as f:
        json.dump(invites, f, indent=4, ensure_ascii=False)

def add_invite(data: dict):
    invites = load_invites()
    invites.append(data)
    save_invites(invites)

def list_invites():
    return load_invites()
