#!/usr/bin/env python3
"""Fix mobile sidebar in index.html - add hamburger menu and overlay."""

import re

html_path = r"C:\Users\pauti\Documents\Hegel Reader\index.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add hamburger button after <body>
html = html.replace('<body>', '<body>\n<button class="menu-toggle" id="menu-toggle" aria-label="Toggle navigation">☰</button>')

# 2. Add mobile CSS before </style>
mobile_css = """
/* Mobile sidebar overlay */
@media(max-width:768px){
  .menu-toggle{display:block;position:fixed;top:1rem;left:1rem;z-index:100;background:var(--accent);color:#fff;border:none;border-radius:var(--radius);padding:.5rem .75rem;font-size:1.2rem;cursor:pointer;line-height:1}
  .sidebar{left:-260px;transition:left .3s ease;width:260px;z-index:99}
  .sidebar.open{left:0;box-shadow:2px 0 12px rgba(0,0,0,.2)}
  .main{padding:4rem 1.5rem 2rem;margin-left:0;max-width:100%}
  .page-header h1{font-size:2rem}
}
@media(min-width:769px){
  .menu-toggle{display:none}
  .sidebar{left:0!important}
  .main{margin-left:var(--nav-width)}
}
"""

html = html.replace('</style>', mobile_css + '\n</style>')

# 3. Add JavaScript before </body>
js = """
<script>
const btn=document.getElementById('menu-toggle');
const sidebar=document.querySelector('.sidebar');
if(btn && sidebar){
  btn.addEventListener('click',()=>sidebar.classList.toggle('open'));
  document.querySelectorAll('.sidebar-nav a').forEach(a=>a.addEventListener('click',()=>sidebar.classList.remove('open')));
}
</script>
"""

html = html.replace('</body>', js + '\n</body>')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed mobile sidebar in index.html")
print("- Added hamburger menu button")
print("- Added mobile CSS (sidebar overlay)")
print("- Added toggle JavaScript")
