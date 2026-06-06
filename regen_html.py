"""Regenerate index.html from commentary.md — call after each daily reading."""
import re, sys
from datetime import datetime
from pathlib import Path

BASE = Path(r"C:\Users\pauti\Documents\Hegel Reader")

with open(BASE / 'commentary.md', encoding='utf-8') as f:
    md = f.read()

hm = re.match(r'(.*?\n## Daily Readings\n)', md, re.DOTALL)
header_block = hm.group(1) if hm else md
rest = md[hm.end():] if hm else ''

tm = re.search(r'^# (.+)$', header_block, re.MULTILINE)
sm = re.search(r'\*(.+?)\*', header_block)
stm = re.search(r'\*\*Started:\*\*\s*(.+)$', header_block, re.MULTILINE)
title = tm.group(1) if tm else 'Hegel Reader'
subtitle = sm.group(1) if sm else ''
started = stm.group(1) if stm else ''

day_blocks = re.split(r'\n(?=## Day \d+)', rest)
day_blocks = [d for d in day_blocks if len(d.strip()) > 10]

LS = '\xa7'

def parse_day(content):
    lines = content.strip().split('\n')
    dh = lines[0].replace('## ', '').strip()
    dn = re.match(r'Day (\d+)', dh)
    day_num = int(dn.group(1)) if dn else 0
    chap_title = ''; meta = ''; rs = 0
    for i, line in enumerate(lines[1:], 1):
        if line.startswith('### ') and LS not in line:
            chap_title = line.replace('### ', '')
        elif line.startswith('**') and '|' in line:
            meta = line.strip('*')
        elif 'The Reading' in line and line.startswith('###'):
            rs = i; break
    body = '\n'.join(lines[rs:])
    s = {'day_num': day_num, 'chap_title': chap_title, 'meta': meta}
    markers = [
        ('reading', LS + ' The Reading'),
        ('system_map', '\U0001f5fa\ufe0f System Map'),
        ('coherence', '\U0001f50d Coherence Evaluation'),
        ('tweet1', '\U0001f426 Tweet 1'),
        ('tweet2', '\U0001f426 Tweet 2'),
        ('rethinkings', '\U0001f504 Modern Rethinkings'),
        ('research', '\U0001f52c Research Project Ideas'),
    ]
    positions = []
    for key, marker in markers:
        idx = body.find('### ' + marker)
        if idx >= 0: positions.append((idx, key))
    positions.sort()
    for i, (pos, key) in enumerate(positions):
        end = positions[i+1][0] if i+1 < len(positions) else len(body)
        text = body[pos:end]; nl = text.find('\n')
        text = text[nl+1:] if nl >= 0 else ''
        s[key] = text.strip()
    mt = s.get('system_map', '')
    cb = mt.find('```')
    if cb >= 0:
        ce = mt.find('```', cb+3)
        if ce >= 0: s['map_diagram'] = mt[cb+3:ce].strip()
    dm = re.search(r'\*\*New determinations.*?\*\*\s*\n(.*?)(?=\*\*Key|\Z)', mt, re.DOTALL)
    s['map_determinations'] = dm.group(1).strip() if dm else ''
    pm = re.search(r'\*\*Key methodological.*?\*\*\s*\n(.*?)(?=\Z)', mt, re.DOTALL)
    s['map_principles'] = pm.group(1).strip() if pm else ''
    coh = s.get('coherence', '')
    prm = re.search(r'\*\*Points of constructive pressure:\*\*\s*\n(.*?)(?=\*\*How|\Z)', coh, re.DOTALL)
    s['pressure_points'] = prm.group(1).strip() if prm else ''
    rem = re.search(r'\*\*How this retrospectively.*?\*\*\s*\n(.*?)(?=\Z)', coh, re.DOTALL)
    s['retro_illumination'] = rem.group(1).strip() if rem else ''
    for tk in ['tweet1', 'tweet2']:
        txt = s.get(tk, '')
        if txt:
            cleaned = []
            for line in txt.split('\n'):
                line = line.strip()
                if line.startswith('> '): cleaned.append(line[2:])
                elif line and not line.startswith('*') and not line.startswith('#'):
                    cleaned.append(line)
            s[tk] = ' '.join(cleaned)
    return s

parsed = [parse_day(db) for db in day_blocks]
print(f'Regenerated HTML for {len(parsed)} day(s)')
