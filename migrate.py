#!/usr/bin/env python3
"""Batch migration script — applies the new post template to all webpages."""

import re
import os
import sys

WEBPAGES_DIR = os.path.join(os.path.dirname(__file__), 'webpages')

NAV_HTML = """  <nav class="navbar">
    <div class="nav-container">
      <a href="/index.html" class="nav-logo">18gi0n</a>
      <button class="nav-toggle" id="navToggle" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links" id="navLinks">
        <li><a href="/index.html">Home</a></li>
        <li><a href="/blog.html">Blog</a></li>
        <li><a href="/projects.html">Projects</a></li>
        <li><a href="/code.html">Code &amp; Tools</a></li>
        <li><a href="/about.html">About</a></li>
      </ul>
    </div>
  </nav>"""

HEAD_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} | 18gi0n</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/styles.css" />
  <link rel="icon" type="image/x-icon" href="/assets/images/racoon.ico" />
</head>
<body>"""

POST_HEADER_TEMPLATE = """
  <header class="post-header">
    <a href="/blog.html" class="back-link">&larr; All Posts</a>
    <h1>{h1_text}</h1>
    <div class="post-meta">
      <span class="badge badge-{category}">{category_label}</span>
      <span class="reading-time" id="readingTime"></span>
    </div>
  </header>

  <nav class="toc" id="toc">
    <div class="toc-title">// Contents</div>
    <ol id="tocList"></ol>
  </nav>

  <article class="post-body" id="postBody">
"""

FOOTER = """  </article>

  <script src="/assets/js/post.js"></script>
</body>
</html>
"""

# Category map: filename → (category, label)
CATEGORIES = {
    'homesiem':         ('blue-team', 'Blue Team'),
    'rsyslog':          ('blue-team', 'Blue Team'),
    'cyberthreatfeedn8n': ('threat-intel', 'Threat Intel'),
    'timelines':        ('blue-team', 'Blue Team'),
    'fcssdsetup':       ('blue-team', 'Blue Team'),
    'forensicscollection': ('blue-team', 'Blue Team'),
    'win_for_anaylsis': ('blue-team', 'Blue Team'),
    'Cap':              ('ctf', 'CTF'),
    'soulmate':         ('ctf', 'CTF'),
    '2m':               ('ctf', 'CTF'),
    'titanic':          ('ctf', 'CTF'),
    'fluffy':           ('ctf', 'CTF'),
    'DC-4':             ('ctf', 'CTF'),
    'Djinn3':           ('ctf', 'CTF'),
    'expressway':       ('ctf', 'CTF'),
    'outbound':         ('ctf', 'CTF'),
    'Bjorn':            ('homelab', 'Homelab'),
    'wifipineapple':    ('homelab', 'Homelab'),
    'travelrouter':     ('homelab', 'Homelab'),
    'p4wn':             ('homelab', 'Homelab'),
    'pwnagotchi':       ('homelab', 'Homelab'),
    'nh_twp3':          ('homelab', 'Homelab'),
    'defconn33':        ('ctf', 'CTF'),
    'ansible':          ('code', 'Code & Tools'),
    'ansible_setup':    ('homelab', 'Homelab'),
    'credr':            ('code', 'Code & Tools'),
    'windowsf':         ('code', 'Code & Tools'),
    'linuxf':           ('code', 'Code & Tools'),
    'ymlcreate':        ('code', 'Code & Tools'),
    'cve':              ('blue-team', 'Blue Team'),
    'awsseclab':        ('blue-team', 'Blue Team'),
    'Resources':        ('blue-team', 'Blue Team'),
    'KQL':              ('blue-team', 'Blue Team'),
    'bluequery':        ('blue-team', 'Blue Team'),
    'digitalforensics': ('blue-team', 'Blue Team'),
    'cybereng':         ('threat-intel', 'Threat Intel'),
    'threatintel':      ('threat-intel', 'Threat Intel'),
    'artifical':        ('ai', 'AI / Hardware'),
    'editor':           ('ctf', 'CTF'),
    'n8nsetup':         ('ai', 'AI / Hardware'),
    'code':             ('ctf', 'CTF'),
}

# Listing pages — these use project-box layout, only do Tier 1 (nav/head/css)
LISTING_PAGES = {'bluequery', 'cybereng', 'digitalforensics', 'n8nsetup', 'Resources', 'threatintel', 'cve', 'awsseclab', 'KQL'}

def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if m:
        t = m.group(1).strip()
        t = re.sub(r'\s*[|\-–—]\s*18gi0n.*$', '', t, flags=re.IGNORECASE).strip()
        t = re.sub(r'\s*-\s*(Tech Lair|18gi0n).*$', '', t, flags=re.IGNORECASE).strip()
        return t
    return 'Post'

def extract_first_h1(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
    if m:
        inner = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        return inner
    return ''

def extract_body_content(html):
    """Extract everything inside .left-aligned-content div."""
    m = re.search(r'<div[^>]+class=["\']left-aligned-content["\'][^>]*>(.*?)</div>\s*</div>\s*(?:<script|</body)', html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # fallback: try .content div
    m = re.search(r'<div[^>]+class=["\']content["\'][^>]*>(.*?)</div>\s*(?:<script|</body)', html, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ''

def strip_h1(content):
    """Remove the first h1 from content (it goes to post-header)."""
    return re.sub(r'<h1[^>]*>.*?</h1>', '', content, count=1, flags=re.DOTALL | re.IGNORECASE).strip()

def strip_inline_copycode(content):
    """Remove inline copy-btn buttons that use onclick=copyCode."""
    return re.sub(r'<button\s+class=["\']copy-btn["\'][^>]*onclick=["\'][^"\']*["\'][^>]*>.*?</button>', '', content, flags=re.DOTALL | re.IGNORECASE)

def migrate_post(filename, html):
    stem = os.path.splitext(filename)[0]
    category, category_label = CATEGORIES.get(stem, ('blue-team', 'Blue Team'))
    title = extract_title(html)
    h1_text = extract_first_h1(html)
    if not h1_text:
        h1_text = title

    body_content = extract_body_content(html)
    body_content = strip_h1(body_content)
    body_content = strip_inline_copycode(body_content)

    # Indent content for readability
    lines = body_content.split('\n')
    indented = '\n'.join('    ' + l if l.strip() else '' for l in lines)

    out = HEAD_TEMPLATE.format(title=title)
    out += '\n'
    out += NAV_HTML
    out += POST_HEADER_TEMPLATE.format(
        h1_text=h1_text,
        category=category,
        category_label=category_label,
    )
    out += indented
    out += '\n'
    out += FOOTER
    return out

def migrate_listing(filename, html):
    """Tier 1 only: update head + nav, keep content wrapper."""
    stem = os.path.splitext(filename)[0]
    title = extract_title(html)

    # Extract content div
    m = re.search(r'<div[^>]+class=["\']content["\'][^>]*>(.*?)</div>\s*(?:<script|</body)', html, re.DOTALL | re.IGNORECASE)
    content_inner = m.group(1).strip() if m else ''

    out = HEAD_TEMPLATE.format(title=title)
    out += '\n'
    out += NAV_HTML
    out += '\n\n  <div class="content">\n'
    out += content_inner + '\n'
    out += '  </div>\n\n'
    out += '  <script src="/assets/js/post.js"></script>\n</body>\n</html>\n'
    return out

def process_file(filepath):
    filename = os.path.basename(filepath)
    stem = os.path.splitext(filename)[0]

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Skip already-migrated files
    if 'class="navbar"' in html and 'class="post-body"' in html:
        print(f'  SKIP (already migrated): {filename}')
        return False

    if stem in LISTING_PAGES:
        new_html = migrate_listing(filename, html)
        mode = 'listing'
    else:
        new_html = migrate_post(filename, html)
        mode = 'post'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f'  OK [{mode}]: {filename}')
    return True

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else None
    changed = 0
    for fname in sorted(os.listdir(WEBPAGES_DIR)):
        if not fname.endswith('.html'):
            continue
        if targets and os.path.splitext(fname)[0] not in targets:
            continue
        path = os.path.join(WEBPAGES_DIR, fname)
        if process_file(path):
            changed += 1
    print(f'\nDone: {changed} files updated.')
