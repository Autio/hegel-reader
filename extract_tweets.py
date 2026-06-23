import re
import json
import subprocess
import sys

commentary_path = "C:/Users/pauti/Documents/Hegel Reader/commentary.md"
state_path = "C:/Users/pauti/Documents/Hegel Reader/state.json"
bsky_script = "C:/Users/pauti/Documents/Hegel Reader/bsky_post.py"

# Read commentary.md
with open(commentary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all Day sections
day_matches = list(re.finditer(r'^## Day (\d+)', content, re.MULTILINE))
print(f"Total Day entries found: {len(day_matches)}")

if not day_matches:
    print("ERROR: No Day entries found in commentary.md")
    sys.exit(1)

# Get the latest day
last_match = day_matches[-1]
latest_day = int(last_match.group(1))
print(f"Latest day: {latest_day}")

# Extract the section for the latest day
section_start = last_match.start()
remaining = content[section_start + 1:]
next_day = re.search(r'^## Day \d+', remaining, re.MULTILINE)
if next_day:
    section_end = section_start + 1 + next_day.start()
else:
    section_end = len(content)

latest_section = content[section_start:section_end]

# Debug: print positions of key markers
print("\n=== Debug: positions ===")
t1 = latest_section.find('Tweet 1')
t2 = latest_section.find('Tweet 2')
print(f"Tweet 1 at: {t1}")
print(f"Tweet 2 at: {t2}")

# Better approach: use regex to find the tweet sections
# Pattern: ### header, then blank line, then tweet text until next ### or ---
pattern1 = r'###[^\n]*Tweet 1[^\n]*\n\n(.*?)(?=\n###|\n---)'
pattern2 = r'###[^\n]*Tweet 2[^\n]*\n\n(.*?)(?=\n###|\n---)'

m1 = re.search(pattern1, latest_section, re.DOTALL)
m2 = re.search(pattern2, latest_section, re.DOTALL)

tweets = []
if m1:
    tweet1_text = m1.group(1).strip()
    tweet1_text = ' '.join(line.strip() for line in tweet1_text.split('\n') if line.strip())
    tweets.append(tweet1_text)
    print(f"\nFound Tweet 1 ({len(tweet1_text)} chars): {tweet1_text[:80]}...")

if m2:
    tweet2_text = m2.group(1).strip()
    tweet2_text = ' '.join(line.strip() for line in tweet2_text.split('\n') if line.strip())
    tweets.append(tweet2_text)
    print(f"Found Tweet 2 ({len(tweet2_text)} chars): {tweet2_text[:80]}...")

if len(tweets) != 2:
    print(f"ERROR: Expected 2 tweets, found {len(tweets)}")
    print("\n=== Latest section (full) ===")
    print(repr(latest_section[-1000:]))
    sys.exit(1)

print(f"\nTweet 1 ({len(tweets[0])} chars): {tweets[0]}")
print(f"\nTweet 2 ({len(tweets[1])} chars): {tweets[1]}")

# Verify they're different
if tweets[0] == tweets[1]:
    print("\nERROR: Both tweets are identical! Extraction failed.")
    sys.exit(1)

# Check state.json
with open(state_path, 'r', encoding='utf-8') as f:
    state = json.load(f)

last_posted = state.get('last_tweet_day', 0)
print(f"\nLast posted day: {last_posted}")

if latest_day <= last_posted:
    print(f"SKIPPING: Day {latest_day} already tweeted")
    sys.exit(0)

# Post tweets
print(f"\nPosting tweets for Day {latest_day}...")
for i, tweet in enumerate(tweets, 1):
    print(f"\nPosting Tweet {i} ({len(tweet)} chars)...")
    result = subprocess.run(
        ['python', bsky_script, tweet],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")
    if result.returncode != 0:
        print(f"ERROR posting tweet {i}")
        sys.exit(1)

# Update state
state['last_tweet_day'] = latest_day
with open(state_path, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2)
    f.write('\n')

print(f"\n✓ Successfully posted both tweets for Day {latest_day}")
print(f"✓ Updated state.json (last_tweet_day: {latest_day})")
