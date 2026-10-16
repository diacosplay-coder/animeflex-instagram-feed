import os
import requests
import instaloader

INSTAGRAM_USERNAME = "valentin.d.prototyp"
STATE_FILE = "last_post.txt"

webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

if not webhook_url:
    raise RuntimeError("Chýba DISCORD_WEBHOOK_URL.")

loader = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    save_metadata=False,
    compress_json=False,
    quiet=True,
)

print(f"Kontrolujem Instagram @{INSTAGRAM_USERNAME}...")

profile = instaloader.Profile.from_username(
    loader.context,
    INSTAGRAM_USERNAME
)

posts = profile.get_posts()

latest_posts = []

for post in posts:
    latest_posts.append(post)

    if len(latest_posts) >= 10:
        break

if not latest_posts:
    print("Nenašli sa žiadne príspevky.")
    raise SystemExit(0)

latest_post = latest_posts[0]

# Pri úplne prvom spustení si iba zapamätáme aktuálny post.
# Nechceme, aby po zapnutí bota poslal starý príspevok.
if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        file.write(latest_post.shortcode)

    print(
        f"Prvé spustenie. Ukladám aktuálny post "
        f"{latest_post.shortcode} a nič neposielam."
    )
    raise SystemExit(0)

with open(STATE_FILE, "r", encoding="utf-8") as file:
    last_shortcode = file.read().strip()

new_posts = []

for post in latest_posts:
    if post.shortcode == last_shortcode:
        break

    new_posts.append(post)

if not new_posts:
    print("Žiadny nový Instagram post.")
    raise SystemExit(0)

# Posielame od najstaršieho nového postu po najnovší
for post in reversed(new_posts):

    permalink = f"https://www.instagram.com/p/{post.shortcode}/"

    caption = post.caption or ""

    if len(caption) > 3500:
        caption = caption[:3497] + "..."

    embed = {
        "author": {
            "name": f"@{INSTAGRAM_USERNAME}"
        },
        "title": "Nový príspevok na Instagrame",
        "url": permalink,
        "description": caption,
        "image": {
            "url": post.url
        }
    }

    payload = {
        "username": "AnimeFlex Instagram",
        "content": permalink,
        "embeds": [embed]
    }

    response = requests.post(
        webhook_url,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    print(f"Odoslaný nový post: {post.shortcode}")

# Zapamätáme si najnovší post
with open(STATE_FILE, "w", encoding="utf-8") as file:
    file.write(latest_post.shortcode)

print("Hotovo.")
