import os
import requests

TASK_ID = "enterprised_colonnade~instagram-posts"
STATE_FILE = "last_post.txt"

apify_token = os.environ.get("APIFY_API_TOKEN")
webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

if not apify_token:
    raise RuntimeError("Chýba APIFY_API_TOKEN.")

if not webhook_url:
    raise RuntimeError("Chýba DISCORD_WEBHOOK_URL.")

print("Spúšťam Instagram scrape cez Apify...")

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
    print("Apify nevrátil žiadny Instagram post.")
    raise SystemExit(0)

post = items[0]

post_id = str(
    post.get("id")
    or post.get("shortCode")
    or post.get("url")
    or ""
)

if not post_id:
    raise RuntimeError("Instagram post nemá použiteľné ID.")

caption = post.get("caption") or ""
permalink = post.get("url")
shortcode = post.get("shortCode")
image_url = post.get("displayUrl")
username = post.get("ownerUsername") or "valentin.d.prototyp"

if not permalink and shortcode:
    permalink = f"https://www.instagram.com/p/{shortcode}/"

# Discord embed má limit na dĺžku description
if len(caption) > 3800:
    caption = caption[:3797] + "..."

# Prvé spustenie:
# iba si zapamätáme aktuálny post a nič neposielame.
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        file.write(post_id)

    print(f"Prvé spustenie. Ukladám aktuálny post {post_id}.")
    print("Na Discord zatiaľ nič neposielam.")
    raise SystemExit(0)

with open(STATE_FILE, "r", encoding="utf-8") as file:
    previous_post_id = file.read().strip()

if post_id == previous_post_id:
    print("Žiadny nový Instagram post.")
    raise SystemExit(0)

print("Našiel sa nový Instagram post.")

embed = {
    "author": {
        "name": f"@{username}"
    },
    "title": "Nový príspevok na Instagrame",
    "description": caption,
}

if permalink:
    embed["url"] = permalink

if image_url:
    embed["image"] = {
        "url": image_url
    }

payload = {
    "username": "AnimeFlexTV",
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
    file.write(post_id)

print("Nový Instagram post bol odoslaný na Discord.")
