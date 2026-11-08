import json, os, sys, time, urllib.parse, urllib.request

G = "https://graph.facebook.com/v27.0"
TOKEN = os.environ["IG_TOKEN"]
IGID = os.environ.get("IG_ID", "17841472809833189")
REPO_RAW = "https://raw.githubusercontent.com/g-murtaza44/drivlume-autopost/main/"

def call(method, path, params):
    params = dict(params, access_token=TOKEN)
    data = urllib.parse.urlencode(params).encode()
    if method == "GET":
        req = urllib.request.Request(f"{G}/{path}?{data.decode()}")
    else:
        req = urllib.request.Request(f"{G}/{path}", data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print("ERROR", path, e.read().decode()); sys.exit(1)

def pick_audio(mood):
    p = {"audio_type": "music", "user_id": IGID}
    if mood: p["search_query"] = mood
    res = call("GET", "ig_audio", p)
    items = res.get("data") or res.get("audio") or []
    if not items and mood:
        res = call("GET", "ig_audio", {"audio_type": "music", "user_id": IGID}); items = res.get("data") or res.get("audio") or []
    if not items:
        print("No audio found", str(res)[:300]); sys.exit(1)
    a = items[0]
    print("Audio:", a.get("title"), "-", a.get("display_artist") or a.get("artist"))
    return a.get("audio_id") or a.get("id")

def post(folder):
    video = REPO_RAW + f"{folder}/reel.mp4"
    caption = open(f"{folder}/caption.txt", encoding="utf-8").read().strip()
    mood = open(f"{folder}/mood.txt").read().strip() if os.path.exists(f"{folder}/mood.txt") else ""
    aid = pick_audio(mood)
    c = call("POST", f"{IGID}/media", {"media_type": "REELS", "video_url": video, "caption": caption,
             "audio_configuration": json.dumps({"audio_id": aid})})
    cid = c["id"]
    for _ in range(40):
        time.sleep(15)
        s = call("GET", cid, {"fields": "status_code,status"})
        print("status:", s.get("status_code"))
        if s.get("status_code") == "FINISHED": break
        if s.get("status_code") == "ERROR": print(s); sys.exit(1)
    p = call("POST", f"{IGID}/media_publish", {"creation_id": cid})
    print("PUBLISHED", p)

from datetime import datetime, timedelta, timezone
PKT = timezone(timedelta(hours=5))
SLOTS = [(9,17),(12,17),(15,17),(18,17),(21,17)]

def log_entries():
    out = []
    if os.path.exists("posted.log"):
        for line in open("posted.log").read().splitlines():
            parts = line.split()
            if not parts: continue
            ts = datetime.fromisoformat(parts[1]) if len(parts) > 1 else None
            out.append((parts[0], ts))
    return out

def is_due():
    now = datetime.now(PKT)
    due = sum(1 for h, m in SLOTS if now >= now.replace(hour=h, minute=m, second=0, microsecond=0))
    ents = [t for _, t in log_entries() if t]
    today = sum(1 for t in ents if t.astimezone(PKT).date() == now.date())
    last = max(ents) if ents else None
    if last and now - last < timedelta(minutes=75):
        print("Last post too recent:", last); return False
    print(f"PKT {now:%H:%M} due={due} posted_today={today}")
    return today < due

def next_folder():
    done = set(f for f, _ in log_entries())
    if not os.path.isdir("posts"): return None
    for f in sorted(os.listdir("posts")):
        path = f"posts/{f}"
        if path not in done and os.path.exists(f"{path}/reel.mp4"): return path
    return None

if __name__ == "__main__":
    manual = len(sys.argv) > 1 and sys.argv[1]
    if not manual and os.environ.get("FORCE") != "1" and not is_due():
        print("Nothing due now."); sys.exit(0)
    folder = sys.argv[1] if manual else next_folder()
    if not folder:
        print("Queue empty, nothing to post."); sys.exit(0)
    post(folder)
    with open("posted.log", "a") as f: f.write(folder + " " + datetime.now(PKT).isoformat(timespec="seconds") + "\n")
    print("Logged", folder)
