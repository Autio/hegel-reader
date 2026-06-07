"""Post tweets to Bluesky via AT Protocol API — with clickable URL facet."""
import sys, json
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / ".bsky_creds.json"
PAGE_URL = "https://autio.github.io/hegel-reader/"

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
    
    # Build the full text with URL
    url_space = 2
    if len(text) + len(PAGE_URL) + url_space <= 300:
        full_text = text + chr(10) + chr(10) + PAGE_URL
    elif len(text) + len(PAGE_URL) + 1 <= 300:
        full_text = text + " " + PAGE_URL
    else:
        full_text = text
    
    # Build facets for the URL so it renders as a clickable link
    facets = []
    url_pos = full_text.find(PAGE_URL)
    if url_pos >= 0:
        # The byte positions matter for AT Protocol facets
        text_bytes = full_text.encode("utf-8")
        url_bytes = PAGE_URL.encode("utf-8")
        byte_start = text_bytes.find(url_bytes)
        if byte_start >= 0:
            byte_end = byte_start + len(url_bytes)
            facets = [{
                "index": {"byteStart": byte_start, "byteEnd": byte_end},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": PAGE_URL}]
            }]
    
    record = {
        "$type": "app.bsky.feed.post",
        "text": full_text,
        "createdAt": now,
    }
    if facets:
        record["facets"] = facets
    
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
            "Authorization": "Bearer " + session["accessJwt"],
        },
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["uri"], full_text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bsky_post.py <tweet_text>")
        sys.exit(1)
    
    text = sys.argv[1]
    if len(text) > 300:
        print("Warning: " + str(len(text)) + " chars exceeds Bluesky 300 limit")
        text = text[:297] + "..."
    
    creds = get_creds()
    session = get_session(creds["handle"], creds["app_password"])
    uri, final_text = post(session, text)
    
    has_url = PAGE_URL in final_text
    print("OK " + uri)
    print("  [" + str(len(final_text)) + " chars] " + final_text[:150] + "...")
    print("  URL clickable: " + str(has_url))
