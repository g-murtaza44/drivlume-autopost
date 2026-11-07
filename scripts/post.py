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
    items = res.get("data", [])
    if not items and mood:
        res = call("GET", "ig_audio", {"audio_type": "music", "user_id": IGID}); items = res.get("data", [])
    if not items:
        print("No audio found", res); sys.exit(1)
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

if __name__ == "__main__":
    post(sys.argv[1])
