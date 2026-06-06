import re
from datetime import datetime

COMMENTARY_PATH = '/mnt/c/Users/pauti/Documents/Hegel Reader/commentary.md'
OUTPUT_PATH = '/mnt/c/Users/pauti/Documents/Hegel Reader/index.html'

with open(COMMENTARY_PATH, encoding='utf-8') as f:
    md = f.read()

header_match = re.match(r'(.*?
## Daily Readings
)', md, re.DOTALL)
header_block = header_match.group(1) if header_match else md
rest = md[header_match.end():] if header_match else ''

title_match = re.search(r'^# (.+)$', header_block, re.MULTILINE)
sub_match = re.search(r'\*(.+?)\*', header_block)
started_match = re.search(r'\*\*Started:\*\*\s*(.+)$', header_block, re.MULTILINE)
title = title_match.group(1) if title_match else 'Hegel Reader'
subtitle = sub_match.group(1) if sub_match else ''
started = started_match.group(1) if started_match else ''

day_blocks = re.split(r'
(?=## Day \d+ â)', rest)
day_blocks = [d for d in day_blocks if len(d.strip()) > 10]
print(f'Parsed {len(day_blocks)} days')
for db in day_blocks:
    print(f'  {len(db)} chars: {db.strip().split(chr(10))[0][:80]}')
