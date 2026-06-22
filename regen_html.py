#!/usr/bin/env python3
"""Regenerate index.html from commentary.md for Hegel Reader."""
import re, json
from pathlib import Path
from datetime import datetime

base = Path(r"C:\Users\pauti\Documents\Hegel Reader")

# Read commentary.md
md_text = base.joinpath("commentary.md").read_text(encoding="utf-8")
# Read state.json
state = json.loads(base.joinpath("state.json").read_text(encoding="utf-8"))
# Read existing index.html for the full CSS reference
existing_html = base.joinpath("index.html").read_text(encoding="utf-8")

# Extract CSS block from existing HTML
css_match = re.search(r'<style>(.*?)</style>', existing_html, re.DOTALL)
if not css_match:
    print("ERROR: Could not extract CSS from existing index.html")
    exit(1)
full_css = css_match.group(1)

def escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def inline_md(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`\n]+?)`', r'<code>\1</code>', s)
    return s

def md_to_html(text):
    if not text:
        return ""
    lines = text.split('\n')
    out = []
    i = 0
    in_list = False
    in_ol = False
    in_blockquote = False
    in_code_block = False
    code_content = []
    in_para = False
    para_lines = []
    
    def flush_para():
        nonlocal in_para, para_lines
        if not para_lines:
            return ""
        content = ' '.join(para_lines)
        content = inline_md(content)
        in_para = False
        para_lines = []
        return f"<p>{content}</p>"
    
    def flush_list():
        nonlocal in_list, in_ol
        tag = 'ol' if in_ol else 'ul'
        in_list = False
        in_ol = False
        return f"</{tag}>"
    
    def flush_blockquote():
        nonlocal in_blockquote
        in_blockquote = False
        return "</blockquote>"
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Code fence
        if stripped.startswith('```'):
            if in_code_block:
                code_text = '\n'.join(code_content)
                code_html = f'<pre><code>{escape_html(code_text)}</code></pre>'
                out.append(code_html)
                in_code_block = False
                code_content = []
            else:
                if in_list:
                    out.append(flush_list())
                if in_para:
                    out.append(flush_para())
                if in_blockquote:
                    out.append(flush_blockquote())
                in_code_block = True
                code_content = []
            i += 1
            continue
        
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
        
        # Blank line - break paragraphs
        if not stripped:
            if in_para:
                out.append(flush_para())
            i += 1
            continue
        
        # Headers
        h_match = re.match(r'^(#{1,4})\s+(.+)', stripped)
        if h_match:
            if in_list:
                out.append(flush_list())
            if in_para:
                out.append(flush_para())
            if in_blockquote:
                out.append(flush_blockquote())
            level = len(h_match.group(1))
            content = inline_md(h_match.group(2))
            out.append(f'<h{level}>{content}</h{level}>')
            i += 1
            continue
        
        # Ordered/unordered list
        li_match = re.match(r'^(?:\d+\.|\-|\*)\s+(.+)', stripped)
        if li_match:
            if in_para:
                out.append(flush_para())
            if in_blockquote:
                out.append(flush_blockquote())
            is_ordered = bool(re.match(r'^\d+\.', stripped))
            if not in_list:
                in_list = True
                in_ol = is_ordered
                out.append('<ol>' if is_ordered else '<ul>')
            elif in_ol != is_ordered:
                out.append(flush_list())
                in_list = True
                in_ol = is_ordered
                out.append('<ol>' if is_ordered else '<ul>')
            li_text = inline_md(li_match.group(1))
            out.append(f'<li>{li_text}</li>')
            i += 1
            continue
        
        # Blockquote
        if stripped.startswith('> '):
            if in_list:
                out.append(flush_list())
            if in_para:
                out.append(flush_para())
            if not in_blockquote:
                in_blockquote = True
                out.append('<blockquote>')
            bq_text = stripped[2:]
            out.append(f'<p>{inline_md(bq_text)}</p>')
            i += 1
            continue
        
        # Regular paragraph
        if stripped:
            if in_list:
                out.append(flush_list())
            if in_blockquote:
                out.append(flush_blockquote())
            para_lines.append(stripped)
            in_para = True
        
        i += 1
    
    if in_para:
        out.append(flush_para())
    if in_list:
        out.append(flush_list())
    if in_blockquote:
        out.append(flush_blockquote())
    
    return '\n'.join(out)

# Split into days
content_part = md_text.split('## Daily Readings\n\n', 1)
if len(content_part) < 2:
    print("ERROR: Could not find '## Daily Readings' marker")
    exit(1)
body_text = content_part[1]

# Split by day headers
day_splits = re.split(r'\n(?=## Day \d+ —)', body_text)

days = []
for day_text in day_splits:
    if not day_text.strip():
        continue
    
    header_match = re.match(r'## (Day \d+ — .*?)\n(### .*?)\n\*\*(.*?)\*\*\n', day_text)
    if not header_match:
        chunk = day_text[:80].replace('\n', '\\n')
        print(f"WARNING: Could not parse day header from: {chunk}...")
        continue
    
    day_label = header_match.group(1).strip()
    chapter_line = header_match.group(2).strip()
    pages_line = header_match.group(3).strip()
    
    day_body = day_text[header_match.end():]
    
    sections = {}
    
    # The Reading
    reading_match = re.search(r'### (?:§ )?(?:The )?Reading\n(.*?)(?=\n### (?:🗺️|System|🐦|🔄|🔬|🔍|Coherence)|\n---\n|\Z)', day_body, re.DOTALL)
    if reading_match:
        sections['reading'] = reading_match.group(1).strip()
    else:
        sections['reading'] = ""
    
    # System Map
    map_match = re.search(r'### (?:🗺️ )?System Map(?: \(Updated\))?\n(.*?)(?=\n### (?:🐦|🔄|🔬|🔍|Coherence)|\n---\n|\n## Day|\Z)', day_body, re.DOTALL)
    if map_match:
        sections['system_map'] = map_match.group(1).strip()
    else:
        sections['system_map'] = ""
    
    # Coherence Evaluation
    coh_match = re.search(r'### (?:🔍 )?Coherence Evaluation\n(.*?)(?=\n### (?:🐦|🔄|🔬)|\n---\n|\n## Day|\Z)', day_body, re.DOTALL)
    if coh_match:
        sections['coherence'] = coh_match.group(1).strip()
    else:
        sections['coherence'] = ""
    
    # Tweets
    tweet1_match = re.search(r'### (?:🐦 )?Tweet 1[—–\-].*?\n\n(?:> )?(.*?)(?=\n\n### (?:🐦 )?Tweet 2|\Z)', day_body, re.DOTALL)
    tweet2_match = re.search(r'### (?:🐦 )?Tweet 2[—–\-].*?\n\n(?:> )?(.*?)(?=\n\n### (?:🔄|🔬)|\n\n---|\Z)', day_body, re.DOTALL)
    
    tweets = []
    if tweet1_match:
        t1 = tweet1_match.group(1).strip()
        t1 = re.sub(r'\n> ?', ' ', t1).strip()
        tweets.append({'label': 'Tweet 1 — Wisdom', 'text': t1})
    if tweet2_match:
        t2 = tweet2_match.group(1).strip()
        t2 = re.sub(r'\n> ?', ' ', t2).strip()
        tweets.append({'label': 'Tweet 2 — Current Events', 'text': t2})
    sections['tweets'] = tweets
    
    # Modern Rethinkings
    rethink_match = re.search(r'### (?:🔄 )?Modern Rethinkings?\n(.*?)(?=\n### (?:🔬)|\n---\n|\n## Day|\Z)', day_body, re.DOTALL)
    if rethink_match:
        sections['rethinkings'] = rethink_match.group(1).strip()
    else:
        sections['rethinkings'] = ""
    
    # Research Project Ideas
    research_match = re.search(r'### (?:🔬 )?Research (?:Project )?Ideas?\n(.*?)(?=\n---\n\*Next|\n---\n\n*## Day|\n---\n\Z|\Z)', day_body, re.DOTALL)
    if research_match:
        sections['research'] = research_match.group(1).strip()
    else:
        sections['research'] = ""
    
    day_num = re.search(r'Day (\d+)', day_label)
    dn = int(day_num.group(1)) if day_num else 0
    
    days.append({
        'label': day_label,
        'number': dn,
        'id': f'day-{dn}',
        'chapter': chapter_line.replace('### ', ''),
        'pages': pages_line,
        'sections': sections
    })

print(f"Parsed {len(days)} days: {[d['label'] for d in days]}")

# Build sidebar links
sidebar_links = []
for day in days:
    chapter_short = day['chapter'][:55]
    if len(day['chapter']) > 55:
        chapter_short += '...'
    sidebar_links.append(
        f'<a href="#{day["id"]}">Day {day["number"]}'
        f'<span class="day-meta">{escape_html(chapter_short)}</span></a>'
    )
sidebar_html = '\n'.join(sidebar_links)

# Build day entries
day_entries_html = []
for day in days:
    sec = day['sections']
    
    search_content = f"{day['label']} {day['chapter']} {day['pages']}"
    for k in ['reading', 'system_map', 'coherence']:
        if sec.get(k):
            s = re.sub(r'<[^>]+>', ' ', sec[k])
            s = re.sub(r'\s+', ' ', s)
            search_content += ' ' + s[:500]
    
    parts = []
    parts.append(f'<article class="day-entry" id="{day["id"]}" data-search-content="{escape_html(search_content)}">')
    parts.append(f'<header class="day-header">')
    parts.append(f'<div class="day-number">{escape_html(day["label"])}</div>')
    parts.append(f'<div class="day-title">{escape_html(day["chapter"])}</div>')
    parts.append(f'<div class="day-meta-line">{escape_html(day["pages"])}</div>')
    parts.append(f'</header>')
    
    # Reading
    reading_html = md_to_html(sec.get('reading', ''))
    parts.append(f'<div class="section-block" data-searchable>')
    parts.append(f'<h3>The Reading</h3>')
    parts.append(reading_html)
    parts.append(f'</div>')
    
    # System Map
    if sec.get('system_map'):
        map_raw = sec['system_map']
        code_match = re.search(r'```\n(.*?)```', map_raw, re.DOTALL)
        if code_match:
            map_code = code_match.group(1).strip()
        else:
            map_code = map_raw.strip()
        map_code = escape_html(map_code)
        
        after_map = re.sub(r'```\n.*?```', '', map_raw, flags=re.DOTALL).strip()
        map_after_html = md_to_html(after_map) if after_map else ""
        
        parts.append(f'<div class="section-block" data-searchable>')
        parts.append(f'<h3>System Map</h3>')
        parts.append(f'<div class="system-map"><pre>{map_code}</pre></div>')
        if map_after_html:
            parts.append(map_after_html)
        parts.append(f'</div>')
    
    # Coherence
    if sec.get('coherence'):
        coh_html = md_to_html(sec['coherence'])
        parts.append(f'<div class="section-block" data-searchable>')
        parts.append(f'<h3>Coherence Evaluation</h3>')
        parts.append(coh_html)
        parts.append(f'</div>')
    
    # Tweets (collapsible)
    if sec.get('tweets'):
        tweet_cards = []
        for t in sec['tweets']:
            char_count = len(t['text'])
            tweet_cards.append(
                f'<div class="tweet-card"><div class="tweet-label">'
                f'{escape_html(t["label"])} ({char_count} chars)</div>'
                f'<blockquote>{inline_md(escape_html(t["text"]))}</blockquote></div>'
            )
        parts.append(f'<details class="collapsible-section tweets-section">')
        parts.append(f'<summary>Tweets &amp; Extras</summary>')
        parts.append(f'<div class="section-block">')
        parts.append('\n'.join(tweet_cards))
        parts.append(f'</div></details>')
    
    # Modern Rethinkings (collapsible)
    if sec.get('rethinkings'):
        rethink_html = md_to_html(sec['rethinkings'])
        parts.append(f'<details class="collapsible-section rethinkings-section">')
        parts.append(f'<summary>Modern Rethinkings</summary>')
        parts.append(f'<div class="section-block">')
        parts.append(rethink_html)
        parts.append(f'</div></details>')
    
    # Research Projects (collapsible)
    if sec.get('research'):
        research_html = md_to_html(sec['research'])
        parts.append(f'<details class="collapsible-section research-section">')
        parts.append(f'<summary>Research Project Ideas</summary>')
        parts.append(f'<div class="section-block">')
        parts.append(research_html)
        parts.append(f'</div></details>')
    
    parts.append(f'</article>')
    day_entries_html.append('\n'.join(parts))

# Build full page
now = datetime.now().strftime('%B %d, %Y at %H:%M')

page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Hegel Reader: The Science of Logic — Running Commentary</title>
<link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{full_css}</style>
</head>
<body>
<button class="menu-toggle" id="menu-toggle" aria-label="Toggle navigation">☰</button>
<div class="page">
<nav class="sidebar">
<div class="sidebar-header"><h1>Hegel Reader</h1><div class="subtitle">The Science of Logic</div></div>
<div class="search-wrap"><span class="search-icon">&#128269;</span><input type="text" id="search" placeholder="Search... (Ctrl+K)" autocomplete="off"></div>
<div class="sidebar-nav"><h3>Daily Readings</h3>
{sidebar_html}
</div>
<div class="sidebar-footer">Started June 06, 2026<br>Last updated: {now}<br>{len(days)} readings completed</div>
</nav>
<main class="main">
<header class="page-header"><h1>Hegel Reader: The Science of Logic — Running Commentary</h1><div class="subtitle">A day-by-day, spiraling-up commentary on Hegel's Science of Logic.</div><div class="meta">Started June 06, 2026 &middot; {len(days)} daily readings &middot; Updated {now}</div></header>
<div class="no-results" id="no-results">No entries match your search.</div>
{chr(10).join(day_entries_html)}
</main>
</div>
<script>
const searchInput = document.getElementById('search');
const entries = document.querySelectorAll('.day-entry');
const noResults = document.getElementById('no-results');

function doSearch() {{
  const q = searchInput.value.toLowerCase().trim();
  if (!q) {{
    entries.forEach(e => e.classList.remove('hidden-by-search'));
    noResults.style.display = 'none';
    document.querySelectorAll('mark.search-highlight').forEach(m => {{
      const parent = m.parentNode;
      parent.replaceChild(document.createTextNode(m.textContent), m);
      parent.normalize();
    }});
    return;
  }}
  let anyVisible = false;
  const words = q.split(/\\s+/).filter(w => w.length > 0);
  
  entries.forEach(entry => {{
    const searchContent = (entry.getAttribute('data-search-content') || '').toLowerCase();
    const matches = words.every(w => searchContent.includes(w));
    if (matches) {{
      entry.classList.remove('hidden-by-search');
      anyVisible = true;
    }} else {{
      entry.classList.add('hidden-by-search');
    }}
  }});
  
  noResults.style.display = anyVisible ? 'none' : 'block';
  
  document.querySelectorAll('mark.search-highlight').forEach(m => {{
    const parent = m.parentNode;
    parent.replaceChild(document.createTextNode(m.textContent), m);
    parent.normalize();
  }});
  
  if (q.length >= 2) {{
    entries.forEach(entry => {{
      if (entry.classList.contains('hidden-by-search')) return;
      const blocks = entry.querySelectorAll('[data-searchable]');
      blocks.forEach(block => {{
        highlightTextNodes(block, words);
      }});
    }});
  }}
}}

function highlightTextNodes(el, words) {{
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(node => {{
    let text = node.textContent;
    let changed = false;
    words.forEach(word => {{
      const escaped = word.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
      const re = new RegExp('(' + escaped + ')', 'gi');
      if (re.test(text)) {{
        text = text.replace(re, '<mark class="search-highlight">$1</mark>');
        changed = true;
      if (q.length >= 2) {{
        entries.forEach(entry => {{
          if (entry.classList.contains('hidden-by-search')) return;
          const blocks = entry.querySelectorAll('[data-searchable]');
          blocks.forEach(block => {{
            highlightTextNodes(block, words);
          }});
        }});
      }}
      }};

      document.addEventListener('keydown', e => {{
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }}
      if (e.key === '/' && document.activeElement !== searchInput && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {{
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }}
      }});
      </script>
      <script>
      const btn=document.getElementById('menu-toggle');
      const sidebar=document.querySelector('.sidebar');
      if(btn && sidebar){{
      btn.addEventListener('click',()=>sidebar.classList.toggle('open'));
      document.querySelectorAll('.sidebar-nav a').forEach(a=>a.addEventListener('click',()=>sidebar.classList.remove('open')));
      }}
      </script>
      </body>
      </html>'''

# Write output
output_path = base.joinpath("index.html")
output_path.write_text(page_html, encoding="utf-8")
file_size = output_path.stat().st_size
print(f"SUCCESS: Wrote index.html ({file_size} bytes, {len(days)} days)")
