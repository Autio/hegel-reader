import re
import json

# Paths
COMMENTARY_PATH = r"C:\Users\pauti\Documents\Hegel Reader\commentary.md"
STATE_PATH = r"C:\Users\pauti\Documents\Hegel Reader\state.json"

def main():
    # Read commentary
    with open(COMMENTARY_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all Day entries
    day_matches = list(re.finditer(r'## Day (\d+)', content))
    if not day_matches:
        print("ERROR: No Day entries found in commentary.md")
        return
    
    # Get latest day
    latest_day_match = day_matches[-1]
    latest_day_num = int(latest_day_match.group(1))
    latest_day_start = latest_day_match.start()
    
    # Extract latest day section
    next_day_match = re.search(r'## Day \d+', content[latest_day_start + 1:])
    if next_day_match:
        latest_day_section = content[latest_day_start:latest_day_start + next_day_match.start() + 1]
    else:
        latest_day_section = content[latest_day_start:]
    
    # Extract Tweet 1 (match text after header until next ### or ---)
    tweet1_pattern = re.compile(r'### 🐦 Tweet 1[^\n]*\n+(.*?)(?=\n###|\n---|\Z)', re.DOTALL)
    tweet1_match = tweet1_pattern.search(latest_day_section)
    if not tweet1_match:
        print("ERROR: Tweet 1 not found in latest day")
        return
    tweet1 = ' '.join([line.strip() for line in tweet1_match.group(1).split('\n') if line.strip()])
    
    # Extract Tweet 2
    tweet2_pattern = re.compile(r'### 🐦 Tweet 2[^\n]*\n+(.*?)(?=\n###|\n---|\Z)', re.DOTALL)
    tweet2_match = tweet2_pattern.search(latest_day_section)
    if not tweet2_match:
        print("ERROR: Tweet 2 not found in latest day")
        return
    tweet2 = ' '.join([line.strip() for line in tweet2_match.group(1).split('\n') if line.strip()])
    
    # Check if already tweeted
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            state = json.load(f)
        last_tweeted = state.get('last_tweeted_day', 0)
        if latest_day_num <= last_tweeted:
            print(f"SILENT: Day {latest_day_num} already tweeted")
            return
    except FileNotFoundError:
        state = {}
    
    # Output results
    print(f"DAY:{latest_day_num}")
    print(f"TWEET1:{tweet1}")
    print(f"TWEET2:{tweet2}")

if __name__ == "__main__":
    main()
