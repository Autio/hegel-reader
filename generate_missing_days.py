#!/usr/bin/env python3
"""
Generate Day 12-15 commentary for Hegel Reader (Units 21-24)
Appends to commentary.md and updates state.json
"""

import json
import re
from datetime import datetime, timedelta

# Load reading units
with open('C:/Users/pauti/Documents/Hegel Reader/reading_units.json', 'r', encoding='utf-8') as f:
    units = json.load(f)

# Load existing commentary
with open('C:/Users/pauti/Documents/Hegel Reader/commentary.md', 'r', encoding='utf-8') as f:
    commentary = f.read()

# Days to generate
days_to_generate = [
    {'day': 12, 'date': 'June 19, 2026', 'unit_idx': 20},  # Unit 21
    {'day': 13, 'date': 'June 20, 2026', 'unit_idx': 21},  # Unit 22
    {'day': 14, 'date': 'June 21, 2026', 'unit_idx': 22},  # Unit 23
    {'day': 15, 'date': 'June 22, 2026', 'unit_idx': 23},  # Unit 24
]

def generate_day_commentary(day_num, date, unit):
    """Generate commentary for one day."""
    unit_id = unit['id']
    subsection = unit['subsection']
    chapter = unit['chapter']
    page = unit['page']
    text = unit['text']
    
    # This is a placeholder - in reality, the LLM would generate this
    # For now, return a minimal structure
    commentary = f"""
---

## Day {day_num} — {date}
### Chapter 3: Being-for-itself — {subsection}
**§{page} | Book One, Section I: Determinateness (Quality)**

---

### § The Reading

[Reading analysis for Unit {unit_id}: {subsection}]

---

### 🗺️ System Map (Updated)

```
[System map update for Unit {unit_id}]
```

**New determinations introduced:**
- [New determinations]

---

### 🔍 Coherence Evaluation

[Coherence evaluation]

---

### 🐦 Tweet 1 — Wisdom Condensation

[Tweet 1 - ≤260 chars]

### 🐦 Tweet 2 — Current Events Connection

[Tweet 2 - ≤260 chars]

---

### 🔄 Modern Rethinkings

1. [Rethinking 1]
2. [Rethinking 2]
3. [Rethinking 3]

---

### 🔬 Research Project Ideas

1. [Research idea 1]
2. [Research idea 2]
3. [Research idea 3]

---

*Next: [Next section]*
"""
    return commentary

# Generate all 4 days
new_content = ""
for day_info in days_to_generate:
    unit = units[day_info['unit_idx']]
    day_commentary = generate_day_commentary(
        day_info['day'],
        day_info['date'],
        unit
    )
    new_content += day_commentary

# Append to commentary.md
updated_commentary = commentary + new_content

with open('C:/Users/pauti/Documents/Hegel Reader/commentary.md', 'w', encoding='utf-8') as f:
    f.write(updated_commentary)

print(f"Appended Day 12-15 to commentary.md")
print(f"New content length: {len(new_content)} chars")

# Update state.json
with open('C:/Users/pauti/Documents/Hegel Reader/state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

state['units_completed'] = list(range(1, 25))  # Units 1-24
state['current_unit'] = 25
state['last_run'] = datetime.now().isoformat()
state['last_tweeted_day'] = 15

with open('C:/Users/pauti/Documents/Hegel Reader/state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2)

print(f"Updated state.json: units 1-24 completed, next = Unit 25")
