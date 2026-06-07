"""Post tweets to Bluesky via AT Protocol API."""
import sys, json
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / ".bsky_creds.json"

def get_creds():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_session(handle, app_password):
    import urllib.request
    url = "https://bsky.social/xrpc/com.atproto.server.createSession"
    data = json.dumps({"identifier": handle, "password": app_password}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def post(session, text):
    import urllib.request
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now,
    }
    body = {
        "repo": session["did"],
        "collection": "app.bsky.feed.post",
        "record": record,
    }
    url = "https://bsky.social/xrpc/com.atproto.repo.createRecord"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {session['accessJwt']}",
        },
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["uri"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bsky_post.py <tweet_text>")
        sys.exit(1)
    
    text = sys.argv[1]
    if len(text) > 300:
        print(f"Warning: {len(text)} chars exceeds Bluesky 300 limit")
    
    creds = get_creds()
    session = get_session(creds["handle"], creds["app_password"])
    uri = post(session, text)
    print(f"OK {uri}")
    print(f"  [{len(text)} chars] {text[:120]}...")
