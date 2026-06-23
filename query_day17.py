
import json, requests, time, sys
from datetime import datetime

BASE = r"C:\Users\pauti\Documents\Hegel Reader"

# Load reading units
with open(f"{BASE}/reading_units.json", encoding="utf-8") as f:
    units = json.load(f)

# Get units 17+18
u17 = [u for u in units if u["id"] == 17][0]
u18 = [u for u in units if u["id"] == 18][0]

reading_text = f"""UNIT 17 — {u17['subsection']}
{u17['text']}

UNIT 18 — {u18['subsection']}
{u18['text']}"""

# Load recent commentary for context (last 250 lines)
with open(f"{BASE}/commentary.md", encoding="utf-8") as f:
    lines = f.readlines()

recent = "".join(lines[-250:])

# Construct prompt
system_prompt = """You are a brilliant Hegel scholar producing daily commentary on Hegel's Science of Logic for an audience of smart, philosophically-curious readers. You write with warmth and clarity — never stiff, never academic-jargon-laden. You're tracking the dialectical movement step by step.

Your task: read the assigned Hegel text, understand the logical movement, and produce a structured analysis. Follow the format exactly. WRITE LIKE A SMART HUMAN, NOT AN AI."""

user_prompt = f"""## HEGEL TEXT FOR TODAY

{reading_text}

## RECENT COMMENTARY (for context — what's been covered)

{recent}

## YOUR TASK

Produce Day 17's analysis following this EXACT format. The reading is Units 17-18: "Existence and being-for-itself" (brief bridge section) + "Being-for-one" (substantial section with Remark on idealism from Eleatics through Kant).

### FORMAT:

```
## Day 17 — {datetime.now().strftime('%B %d, %Y')}
### Chapter 3: Being-for-itself — a. Existence and Being-for-itself / b. Being-for-one
**Pages 200–205 | Book One, Section I: Determinateness (Quality)**

---

### § The Reading
[Thorough explication. Unit 17 is a short bridge — cover it quickly. Unit 18 is the main event: Hegel's argument that being-for-itself and being-for-one are inseparable moments of ideality. Cover: the initial puzzle (nothing at hand for which it would be), the resolution (the self is that for which it is), the German "Was für ein Ding" etymology argument, and the long Remark reviewing idealism — Eleatics/Spinoza (abstract negation, no being-for-itself), Malebranche (more explicit, but mixed with theological content), Leibniz (monads as idealizations but plurality externally imposed), Kant/Fichte (stuck in dualism, the ought). Use direct quotes with paragraph numbers like 21.147.]

### 🗺️ System Map (Updated)
[ASCII diagram with box-drawing characters (│ ├ └ ─ → ▼ ★). Extend from the Day 16 map. ADD the new determinations: Being-for-one, Ideality, the distinction between being-for-itself and being-for-one as inseparable moments. Show the Remark's historical survey as side-notes.]

**New determinations introduced:**
- [Each new category with a one-line definition]

### 🔍 Coherence Evaluation
[Does this follow necessarily from being-for-itself? Evaluate the being-for-one move. Push constructively — is Hegel's argument that being-for-itself IS being-for-one convincing, or is it a sleight of hand? How does the Remark's historical survey function logically — is it demonstration or illustration?]

**Points of constructive pressure:**
1. [Specific question or tension]
2. [Another]

**How this retrospectively illuminates earlier material:**
- [What new light does this shed?]

### 🐦 Tweet 1 — Wisdom Condensation
[A single tweet, 260 CHARS OR FEWER. The URL takes ~40 chars so your text must be ≤260. Condense the deepest insight from today's reading. No hashtags. See TWEET VOICE RULES below.]

### 🐦 Tweet 2 — Current Events Connection
[A single tweet, 260 CHARS OR FEWER. Connect today's Hegel to something happening NOW in June 2026. No hashtags. See TWEET VOICE RULES below.]

### 🔄 Modern Rethinkings
[2-3 concrete reformulations using contemporary frameworks. Be specific.]

### 🔬 Research Project Ideas
[1-3 specific, named proposals. Don't repeat ones already in commentary.]

---

*Next: c. The One (§21.152+)*
```

## TWEET VOICE RULES — CRITICAL

### DO:
- Write like texting a smart friend who doesn't know Hegel
- Short sentences. Fragments are fine. Rhythm matters.
- Sound surprised by the ideas. Hegel should feel alive.
- Be specific. Name things.
- Connect tweet 2 to genuinely current June 2026 events.
- Let the tweet end abruptly if that's how the thought lands.

### NEVER:
- "Hegel's insight that..." or "Hegel shows us that..."
- "maps perfectly onto," "serves as a powerful reminder," "offers a framework"
- Colon-clause-comma structures
- Parenthetical glosses
- Words like "fascinating," "profound," "remarkable," "powerful"
- Any sentence that could appear in a Medium post
- Academic hedging

### Good example:
"turns out the emptiest thought possible — just 'being' with no qualities at all — is literally the same as thinking nothing. hegel starts his whole system here. not because it's deep. because there's nowhere else to start."

Output ONLY the formatted Day 17 entry — nothing before or after."""

# Call the API
api_url = "http://localhost:8081/v1/chat/completions"

payload = {
    "model": "Qwen2.5-72B-Instruct-IQ3_XXS.gguf",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 6000,
    "stream": False
}

print(f"Querying local Qwen 72B...", flush=True)
print(f"Prompt size: {len(user_prompt)} chars user + {len(system_prompt)} chars system", flush=True)

t0 = time.time()
resp = requests.post(api_url, json=payload, timeout=600)
elapsed = time.time() - t0

if resp.status_code != 200:
    print(f"ERROR {resp.status_code}: {resp.text[:500]}", flush=True)
    sys.exit(1)

data = resp.json()
content = data["choices"][0]["message"]["content"]
tokens = data.get("usage", {})

print(f"Generated in {elapsed:.1f}s", flush=True)
print(f"Usage: {tokens}", flush=True)
print(f"Output length: {len(content)} chars", flush=True)

# Save raw output
with open(f"{BASE}/test_runs/day17_raw.txt", "w", encoding="utf-8") as f:
    f.write(content)

print(f"Saved to test_runs/day17_raw.txt", flush=True)

# Print the content for the sandbox to capture
print("\n=== GENERATED ANALYSIS ===")
print(content)
