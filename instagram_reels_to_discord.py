import os
import requests

TASK_ID = "enterprised_colonnade~instagram-reels"
STATE_FILE = "last_reel.txt"

apify_token = os.environ.get("APIFY_API_TOKEN")
webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

if not apify_token:
    raise RuntimeError("Chýba APIFY_API_TOKEN.")

if not webhook_url:
    raise RuntimeError("Chýba DISCORD_WEBHOOK_URL.")

print("Spúšťam kontrolu Instagram Reels cez Apify...")

apify_url = (
    f"https://api.apify.com/v2/actor-tasks/"
    f"{TASK_ID}/run-sync-get-dataset-items"
)

response = requests.post(
    apify_url,
    params={"token": apify_token},
    timeout=180,
)

response.raise_for_status()

items = response.json()

if not items:
    print("Apify nevrátil žiadny Reel.")
    raise SystemExit(0)

reel = items[0]

reel_id = str(
    reel.get("id")
    or reel.get("shortCode")
    or reel.get("url")
    or ""
)

if not reel_id:
    raise RuntimeError("Reel nemá použiteľné ID.")

caption = reel.get("caption") or ""
permalink = reel.get("url")
shortcode = reel.get("shortCode")
thumbnail = reel.get("displayUrl")
username = reel.get("ownerUsername") or "valentin.d.prototyp"

if not permalink and shortcode:
    permalink = f"https://www.instagram.com/reel/{shortcode}/"

if len(caption) > 3800:
    caption = caption[:3797] + "..."

# Pri prvom spustení si iba zapamätáme aktuálny Reel.
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        file.write(reel_id)

    print(f"Prvé spustenie. Ukladám aktuálny Reel {reel_id}.")
    print("Na Discord zatiaľ nič neposielam.")
    raise SystemExit(0)

with open(STATE_FILE, "r", encoding="utf-8") as file:
    previous_reel_id = file.read().strip()

if reel_id == previous_reel_id:
    print("Žiadny nový Reel.")
    raise SystemExit(0)

print("Našiel sa nový Instagram Reel.")

embed = {
    "author": {
        "name": f"@{username}"
    },
    "title": "Nový Reel na Instagrame",
    "description": caption,
}

if permalink:
    embed["url"] = permalink

if thumbnail:
    embed["image"] = {
        "url": thumbnail
    }

payload = {
    "username": "AnimeFlex Instagram",
    "embeds": [embed],
}

if permalink:
    payload["content"] = permalink

discord_response = requests.post(
    webhook_url,
    json=payload,
    timeout=30,
)

discord_response.raise_for_status()

with open(STATE_FILE, "w", encoding="utf-8") as file:
    file.write(reel_id)

print("Nový Instagram Reel bol odoslaný na Discord.")
