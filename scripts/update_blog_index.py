#!/usr/bin/env python3
import os
import re
from datetime import datetime

SRC_DIR = "blog-src"
DEST_DIR = "docs/blog"
BLOG_INDEX_FILE = os.path.join(DEST_DIR, "index.html")


def extract_metadata(markdown_content):
    meta = {}
    lines = markdown_content.splitlines()
    meta_re = re.compile(r'^(Title|Date|Author|Tags|Read_time)\s*:\s*(.*)$', re.IGNORECASE)
    remaining = []
    for line in lines:
        m = meta_re.match(line.strip())
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().strip('"')
            if key == 'tags':
                v = val
                if v.startswith('[') and v.endswith(']'):
                    v = v[1:-1]
                meta['tags'] = [t.strip() for t in re.split(r',\s*', v) if t.strip()]
            else:
                meta[key] = val
        else:
            remaining.append(line)
    return meta


def try_parse_date(d):
    if not d:
        return datetime.min
    fmts = ["%B %d, %Y", "%Y-%m-%d", "%d %B %Y", "%b %d, %Y"]
    for f in fmts:
        try:
            return datetime.strptime(d, f)
        except Exception:
            continue
    m = re.search(r"(19|20)\d{2}", d)
    if m:
        try:
            return datetime(int(m.group(0)), 1, 1)
        except Exception:
            return datetime.min
    return datetime.min


def build_posts_list():
    md_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.md') and 'template' not in f.lower() and not f.startswith('.')]
    posts = []
    for md in md_files:
        path = os.path.join(SRC_DIR, md)
        with open(path, 'r', encoding='utf-8') as fh:
            content = fh.read()
        meta = extract_metadata(content)
        title = meta.get('title') or (re.search(r'^#\s+(.*)', content, re.MULTILINE) and re.search(r'^#\s+(.*)', content, re.MULTILINE).group(1)) or os.path.splitext(md)[0]
        date = meta.get('date','')
        author = meta.get('author','')
        tags = meta.get('tags',[])
        read_time = meta.get('read_time', '')
        posts.append({
            'title': title,
            'url': f'html/{os.path.splitext(md)[0]}.html',
            'date': date,
            'author': author,
            'tags': tags,
            'read_time': read_time
        })
    posts.sort(key=lambda p: try_parse_date(p.get('date','')), reverse=True)
    return posts


def update_index(posts):
    with open(BLOG_INDEX_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    post_list_html = ''
    for post in posts:
        tags_html = ''
        if post.get('tags'):
            tags_html = ' '.join([f"<span class=\"tag tag-{t.lower().replace(' ','-')}\">{t}</span>" for t in post.get('tags')])
        post_list_html += f'''\n            <article class="blog-card"> 
                <a href="{post['url']}" class="blog-card-content"> 
                    <div class="blog-card-date"><i class="fas fa-calendar-alt"></i> {post.get('date','')}</div>
                    <h2 class="blog-card-title">{post.get('title','')}</h2>
                    <div style="display:flex;gap:0.75rem;align-items:center;margin-top:0.5rem;flex-wrap:wrap;"> 
                        <span class="blog-meta"><i class="fas fa-clock"></i> {post.get('read_time','')} </span>
                        <span class="blog-meta"><i class="fas fa-user"></i> {post.get('author','')}</span>
                        <span style="margin-left:0.25rem;">{tags_html}</span>
                    </div>
                </a>
            </article>'''

    start_tag_re = re.search(r'<section[^>]*class=["\'][^"\']*blog-grid[^"\']*["\'][^>]*>', html)
    if not start_tag_re:
        print('blog-grid section not found in index.html')
        return
    start_index = start_tag_re.end()
    end_index = html.find('</section>', start_index)
    if end_index == -1:
        print('closing </section> not found')
        return

    new_html = html[:start_index] + '\n' + post_list_html + html[end_index:]
    with open(BLOG_INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print('Updated', BLOG_INDEX_FILE)


if __name__ == '__main__':
    posts = build_posts_list()
    update_index(posts)
