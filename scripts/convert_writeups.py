import os
import re
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader

# --- CONFIGURATION ---
SRC_DIR = "blog-src"
DEST_DIR = "docs/blog"
HTML_OUTPUT_DIR = os.path.join(DEST_DIR, "html")
ASSETS_DIR = "docs/assets/images/writeups"
TEMPLATE_DIR = "scripts"
TEMPLATE_NAME = "blog_template.html"
BLOG_INDEX_FILE = os.path.join(DEST_DIR, "index.html")


def get_post_title(markdown_content):
    """Extracts the first H1 header from markdown content."""
    match = re.search(r"^#\s+(.*)", markdown_content, re.MULTILINE)
    if match:
        return match.group(1)
    return "Blog Post"


def convert_obsidian_images(content, md_file_path):
    """
    Finds all Obsidian-style image links, copies the images from
    blog-src/assets/images (or relative paths) to the assets
    directory, and replaces the links with standard markdown links.
    """

    image_pattern = r"!\[\[(.*?)\]\]"

    BLOG_ASSETS_DIR = os.path.join(SRC_DIR, "assets", "images")

    def replace_link(match):
        image_ref = match.group(1).strip()

        candidate_paths = [
            os.path.join(os.path.dirname(md_file_path), image_ref),
            os.path.join(BLOG_ASSETS_DIR, image_ref),
            os.path.join(BLOG_ASSETS_DIR, os.path.basename(image_ref)),
        ]

        src_image_path = next((p for p in candidate_paths if os.path.exists(p)), None)

        if not src_image_path:
            print(f"Warning: Image not found for {image_ref} in {md_file_path}")
            return f"![Image not found: {image_ref}]"

        os.makedirs(ASSETS_DIR, exist_ok=True)
        dest_filename = os.path.basename(src_image_path)
        dest_image_path = os.path.join(ASSETS_DIR, dest_filename)

        shutil.copy(src_image_path, dest_image_path)

        return f"![](../../assets/images/writeups/{dest_filename})"

    return re.sub(image_pattern, replace_link, content)


def extract_metadata(markdown_content):
    """Extract simple metadata lines like Title, Date, Author, Tags from the top of the markdown.
    Returns a dict and the markdown with those metadata lines removed.
    """
    meta = {}
    lines = markdown_content.splitlines()
    remaining_lines = []

    meta_re = re.compile(r'^(Title|Date|Author|Tags|Read_time)\s*:\s*(.*)$', re.IGNORECASE)

    for line in lines:
        m = meta_re.match(line.strip())
        if m:
            key = m.group(1).strip().lower()
            value = m.group(2).strip().strip('"')
            # Normalize tags (simple comma/ bracket handling)
            if key == 'tags':
                # remove surrounding brackets if present
                v = value
                v = v.strip()
                if v.startswith('[') and v.endswith(']'):
                    v = v[1:-1]
                meta['tags'] = [t.strip() for t in re.split(r',\s*', v) if t.strip()]
            else:
                meta[key] = value
            # Skip writing this line into remaining content (we remove metadata lines)
        else:
            remaining_lines.append(line)

    cleaned = "\n".join(remaining_lines)
    return meta, cleaned


def compute_read_time_from_lines(markdown_content, lines_per_min=20):
    """Simple read time estimate based on number of lines in the markdown.
    Defaults to 20 lines per minute; always returns at least 1 minute.
    """
    if not markdown_content:
        return "1 min read"
    num_lines = markdown_content.count('\n') + 1
    minutes = max(1, round(num_lines / float(lines_per_min)))
    return f"{minutes} min read"


def extract_challenge_metadata(markdown_content):
    """Parse markdown bullet lines like '- **Key:** Value' into a dict."""
    challenge = {}
    for m in re.finditer(r"^\s*-\s*\*\*(.+?)\*\*\s*:\s*(.+)$", markdown_content, re.MULTILINE):
        key = m.group(1).strip().lower().replace(' ', '_')
        val = m.group(2).strip()
        challenge[key] = val
    return challenge


def remove_leading_h1(markdown_content):
    """Remove the first H1 (`# Title`) line from markdown to avoid duplicate titles.
    Returns modified markdown.
    """
    lines = markdown_content.splitlines()
    new_lines = []
    removed = False
    for line in lines:
        if not removed and re.match(r"^#\s+", line):
            removed = True
            continue
        new_lines.append(line)
    return "\n".join(new_lines)
def update_blog_index(posts):
    """Updates the blog index file with a list of posts."""
    with open(BLOG_INDEX_FILE, "r") as f:
        index_content = f.read()

        post_list_html = ""
        for post in posts:
                # Build simple tag HTML with per-tag classes
                tags_html = ""
                if post.get('tags'):
                        tags_html = ' '.join([f"<span class=\"tag tag-{t.lower().replace(' ','-')}\">{t}</span>" for t in post.get('tags')])

                # Difficulty badge
                difficulty_html = ''
                if post.get('difficulty'):
                        difficulty_html = f"<span class=\"meta-item difficulty difficulty-{post.get('difficulty').lower()}\">{post.get('difficulty')}</span>"

                post_list_html += f"""
            <article class=\"blog-card\"> 
                <a href=\"{post['url']}\" class=\"blog-card-content\"> 
                    <div class=\"blog-card-date\"><i class=\"fas fa-calendar-alt\"></i> {post.get('date','')}</div>
                    <h2 class=\"blog-card-title\">{post['title']}</h2>
                    <div style=\"display:flex;gap:0.75rem;align-items:center;margin-top:0.5rem;flex-wrap:wrap;\"> 
                        <span class=\"blog-meta\"><i class=\"fas fa-clock\"></i> {post.get('read_time','')} </span>
                        <span class=\"blog-meta\"><i class=\"fas fa-user\"></i> {post.get('author','')}</span>
                        {difficulty_html}
                        <span style=\"margin-left:0.25rem;\">{tags_html}</span>
                    </div>
                    <!--<span class=\"read-more blog-card-link\"> <i class=\"fas fa-arrow-right\"></i></span>-->
                </a>
            </article>
        """

    start_tag_re = re.search(r'<section[^>]*class=["\'][^"\']*blog-grid[^"\']*["\'][^>]*>', index_content)
    if not start_tag_re:
        print(f"Warning: Could not find blog-grid section start in {BLOG_INDEX_FILE}")
        return

    start_index = start_tag_re.end()
    end_index = index_content.find('</section>', start_index)
    if end_index == -1:
        print(f"Warning: Could not find closing </section> in {BLOG_INDEX_FILE}")
        return

    new_index_content = index_content[:start_index] + '\n' + post_list_html + index_content[end_index:]

    with open(BLOG_INDEX_FILE, "w") as f:
        f.write(new_index_content)

    print(f"Updated blog index at {BLOG_INDEX_FILE}")


def get_all_posts():
    """Returns a list of all blog posts."""
    md_files = [f for f in os.listdir(SRC_DIR) if f.endswith(".md")]
    posts = []

    for md_file in md_files:
        md_file_path = os.path.join(SRC_DIR, md_file)
        with open(md_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        meta, cleaned = extract_metadata(content)
        challenge_meta = extract_challenge_metadata(cleaned)
        title = meta.get('title') or get_post_title(content)
        output_filename = os.path.splitext(md_file)[0] + ".html"

        posts.append({
            "title": title,
            "url": f"html/{output_filename}",
            "date": meta.get('date',''),
            "author": meta.get('author',''),
            "tags": meta.get('tags',[]),
            "read_time": compute_read_time_from_lines(cleaned),
            "difficulty": challenge_meta.get('difficulty','')
        })

    return posts


def main():
    os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_NAME)

    all_posts = get_all_posts()

    posts_html = ""
    for post in all_posts:
        post_filename = os.path.basename(post["url"])
        posts_html += f'<li><a href="{post_filename}"><i class="fas fa-file-alt"></i> {post["title"]}</a></li>'

    md_files = [f for f in os.listdir(SRC_DIR) if f.endswith(".md")]

    generated_posts = []

    for post_idx, md_file in enumerate(md_files, start=1):
        md_file_path = os.path.join(SRC_DIR, md_file)

        with open(md_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # First convert obsidian-style images and extract metadata lines
        content_with_images = convert_obsidian_images(content, md_file_path)
        meta, cleaned_content = extract_metadata(content_with_images)

        # Title preference: metadata Title else first H1
        title = meta.get('title') or get_post_title(content_with_images)

        # Remove leading H1 from content so template title doesn't duplicate it
        cleaned_no_h1 = remove_leading_h1(cleaned_content)

        # Process figures: replace markdown image syntax, Obsidian images, and HTML <img> with <figure> blocks and generate ids
        def process_figures(md_text, post_index):
            fig_i = 1
            placeholders = {}
            mapping = {}

            # Protect fenced code blocks and inline code by replacing with placeholders
            code_placeholders = {}
            cp_i = 0
            def mask_code(text):
                nonlocal cp_i
                def fenced_repl(m):
                    nonlocal cp_i
                    key = f"__CODE_BLOCK_{cp_i}__"
                    code_placeholders[key] = m.group(0)
                    cp_i += 1
                    return key
                text = re.sub(r'```[\s\S]*?```', fenced_repl, text)

                def inline_repl(m):
                    nonlocal cp_i
                    key = f"__INLINE_CODE_{cp_i}__"
                    code_placeholders[key] = m.group(0)
                    cp_i += 1
                    return key
                text = re.sub(r'`[^`]*`', inline_repl, text)
                return text

            def unmask_code(text):
                for k, v in code_placeholders.items():
                    text = text.replace(k, v)
                return text

            masked = mask_code(md_text)

            # Normalize Obsidian-style ![[name]] to markdown-like references
            masked = re.sub(r'!\[\[(.*?)\]\]', lambda m: f'![]({m.group(1).strip()})', masked)

            # Helper to create a placeholder for a figure and record mapping
            def make_placeholder_for_img(src, alt, original_img_tag=None):
                nonlocal fig_i
                fig_id = f"fig-{post_index}-{fig_i}"
                caption = f"Fig{post_index}.{fig_i} - {alt}"
                if original_img_tag:
                    html = f'<figure class="post-figure" id="{fig_id}">\n  {original_img_tag}\n  <figcaption>{caption}</figcaption>\n</figure>'
                else:
                    html = f'<figure class="post-figure" id="{fig_id}">\n  <img src="{src}" alt="{alt}"/>\n  <figcaption>{caption}</figcaption>\n</figure>'
                placeholder = f"__FIG_PLACEHOLDER_{fig_i}__"
                placeholders[placeholder] = html
                mapping[os.path.basename(src)] = (fig_id, caption, placeholder)
                fig_i += 1
                return placeholder

            # Replace markdown images ![alt](src) with placeholders
            def md_img_repl(m):
                alt = m.group(1).strip() or os.path.splitext(os.path.basename(m.group(2).strip()))[0]
                src = m.group(2).strip()
                return make_placeholder_for_img(src, alt)
            masked = re.sub(r'!\[(.*?)\]\((.*?)\)', md_img_repl, masked)

            # Replace HTML <img ...> tags with placeholders, preserving original tag
            def html_img_repl(m):
                full_tag = m.group(0)
                attrs = m.group(1)
                src_m = re.search(r'src\s*=\s*"([^\"]+)"', attrs)
                alt_m = re.search(r'alt\s*=\s*"([^\"]+)"', attrs)
                src = src_m.group(1) if src_m else ''
                alt = alt_m.group(1) if alt_m else os.path.splitext(os.path.basename(src))[0]
                return make_placeholder_for_img(src, alt, full_tag)
            masked = re.sub(r'<img\s+([^>]+?)\s*/?>', html_img_repl, masked)

            # Replace bare mentions of the image filename with links to the figure, but only in text nodes
            parts = re.split(r'(<[^>]+>)', masked)
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    for basename, (fid, caption, placeholder) in mapping.items():
                        part = re.sub(rf'\b{re.escape(basename)}\b', f'<a href="#'+fid+f'">{caption}</a>', part)
                    parts[i] = part
            masked = ''.join(parts)

            # Replace placeholders with actual figure HTML
            for placeholder, html in placeholders.items():
                masked = masked.replace(placeholder, html)

            final = unmask_code(masked)
            simple_map = {k: (v[0], v[1]) for k, v in mapping.items()}
            return final, simple_map

        cleaned_no_h1, figures = process_figures(cleaned_no_h1, post_idx)

        # Compute read time from cleaned content (metadata removed)
        read_time = compute_read_time_from_lines(cleaned_no_h1)

        # Extract challenge-specific metadata from the body (Room Name, Difficulty, Category)
        challenge_meta = extract_challenge_metadata(cleaned_no_h1)
        challenge_name = challenge_meta.get('room_name') or challenge_meta.get('room') or ''

        html_fragment = markdown.markdown(cleaned_no_h1, extensions=["fenced_code", "tables"])

        final_html = template.render(
            title=title,
            content=html_fragment,
            posts=posts_html,
            page_date=meta.get('date',''),
            page_author=meta.get('author',''),
            page_tags=meta.get('tags',[]),
            read_time=read_time,
            challenge=challenge_meta,
            challenge_name=challenge_name
        )

        output_filename = os.path.splitext(md_file)[0] + ".html"
        output_path = os.path.join(HTML_OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"Converted {md_file} -> {output_path}")

        generated_posts.append({
            "title": title,
            "url": f"html/{output_filename}",
            "date": meta.get('date',''),
            "author": meta.get('author',''),
            "tags": meta.get('tags',[]),
            "read_time": read_time
        })

    if generated_posts:
        update_blog_index(generated_posts)


if __name__ == "__main__":
    main()
import os
import re
import shutil
import markdown
from jinja2 import Environment, FileSystemLoader

# --- CONFIGURATION ---
SRC_DIR = "blog-src"
DEST_DIR = "docs/blog"
HTML_OUTPUT_DIR = os.path.join(DEST_DIR, "html")
ASSETS_DIR = "docs/assets/images/writeups"
TEMPLATE_DIR = "scripts"
TEMPLATE_NAME = "blog_template.html"
BLOG_INDEX_FILE = os.path.join(DEST_DIR, "index.html")


def get_post_title(markdown_content):
    """Extracts the first H1 header from markdown content."""
    match = re.search(r"^#\s+(.*)", markdown_content, re.MULTILINE)
    if match:
        def process_figures(md_text, post_index):
            fig_i = 1
            placeholders = {}
            mapping = {}

            # Protect fenced code blocks and inline code by replacing with placeholders
            code_placeholders = {}
            cp_i = 0
            def mask_code(text):
                nonlocal cp_i
                def fenced_repl(m):
                    nonlocal cp_i
                    key = f"__CODE_BLOCK_{cp_i}__"
                    code_placeholders[key] = m.group(0)
                    cp_i += 1
                    return key
                text = re.sub(r'```[\s\S]*?```', fenced_repl, text)

                def inline_repl(m):
                    nonlocal cp_i
                    key = f"__INLINE_CODE_{cp_i}__"
                    code_placeholders[key] = m.group(0)
                    cp_i += 1
                    return key
                text = re.sub(r'`[^`]*`', inline_repl, text)
                return text

            def unmask_code(text):
                for k, v in code_placeholders.items():
                    text = text.replace(k, v)
                return text

            masked = mask_code(md_text)

            # Normalize Obsidian-style ![[name]] to markdown-like references
            masked = re.sub(r'!\[\[(.*?)\]\]', lambda m: f'![]({m.group(1).strip()})', masked)

            # Helper to create a placeholder for a figure and record mapping
            def make_placeholder_for_img(src, alt, original_img_tag=None):
                nonlocal fig_i
                fig_id = f"fig-{post_index}-{fig_i}"
                caption = f"Fig{post_index}.{fig_i} - {alt}"
                if original_img_tag:
                    html = f'<figure class="post-figure" id="{fig_id}">\n  {original_img_tag}\n  <figcaption>{caption}</figcaption>\n</figure>'
                else:
                    html = f'<figure class="post-figure" id="{fig_id}">\n  <img src="{src}" alt="{alt}"/>\n  <figcaption>{caption}</figcaption>\n</figure>'
                placeholder = f"__FIG_PLACEHOLDER_{fig_i}__"
                placeholders[placeholder] = html
                mapping[os.path.basename(src)] = (fig_id, caption, placeholder)
                fig_i += 1
                return placeholder

            # Replace markdown images ![alt](src) with placeholders
            def md_img_repl(m):
                alt = m.group(1).strip() or os.path.splitext(os.path.basename(m.group(2).strip()))[0]
                src = m.group(2).strip()
                return make_placeholder_for_img(src, alt)
            masked = re.sub(r'!\[(.*?)\]\((.*?)\)', md_img_repl, masked)

            # Replace HTML <img ...> tags with placeholders, preserving original tag
            def html_img_repl(m):
                def process_figures(md_text, post_index):
                    fig_i = 1
                    placeholders = {}
                    mapping = {}

                    # Protect fenced code blocks and inline code by replacing with placeholders
                    code_placeholders = {}
                    cp_i = 0
                    def mask_code(text):
                        nonlocal cp_i
                        def fenced_repl(m):
                            nonlocal cp_i
                            key = f"__CODE_BLOCK_{cp_i}__"
                            code_placeholders[key] = m.group(0)
                            cp_i += 1
                            return key
                        text = re.sub(r'```[\s\S]*?```', fenced_repl, text)

                        def inline_repl(m):
                            nonlocal cp_i
                            key = f"__INLINE_CODE_{cp_i}__"
                            code_placeholders[key] = m.group(0)
                            cp_i += 1
                            return key
                        text = re.sub(r'`[^`]*`', inline_repl, text)
                        return text

                    def unmask_code(text):
                        for k, v in code_placeholders.items():
                            text = text.replace(k, v)
                        return text

                    masked = mask_code(md_text)

                    # Normalize Obsidian-style ![[name]] to markdown-like references
                    masked = re.sub(r'!\[\[(.*?)\]\]', lambda m: f'![]({m.group(1).strip()})', masked)

                    # Helper to create a placeholder for a figure and record mapping
                    def make_placeholder_for_img(src, alt, original_img_tag=None):
                        nonlocal fig_i
                        fig_id = f"fig-{post_index}-{fig_i}"
                        caption = f"Fig{post_index}.{fig_i} - {alt}"
                        if original_img_tag:
                            html = f'<figure class="post-figure" id="{fig_id}">\n  {original_img_tag}\n  <figcaption>{caption}</figcaption>\n</figure>'
                        else:
                            html = f'<figure class="post-figure" id="{fig_id}">\n  <img src="{src}" alt="{alt}"/>\n  <figcaption>{caption}</figcaption>\n</figure>'
                        placeholder = f"__FIG_PLACEHOLDER_{fig_i}__"
                        placeholders[placeholder] = html
                        mapping[os.path.basename(src)] = (fig_id, caption, placeholder)
                        fig_i += 1
                        return placeholder

                    # Replace markdown images ![alt](src) with placeholders
                    def md_img_repl(m):
                        alt = m.group(1).strip() or os.path.splitext(os.path.basename(m.group(2).strip()))[0]
                        src = m.group(2).strip()
                        return make_placeholder_for_img(src, alt)
                    masked = re.sub(r'!\[(.*?)\]\((.*?)\)', md_img_repl, masked)

                    # Replace HTML <img ...> tags with placeholders, preserving original tag
                    def html_img_repl(m):
                        full_tag = m.group(0)
                        attrs = m.group(1)
                        src_m = re.search(r'src\s*=\s*"([^\"]+)"', attrs)
                        alt_m = re.search(r'alt\s*=\s*"([^\"]+)"', attrs)
                        src = src_m.group(1) if src_m else ''
                        alt = alt_m.group(1) if alt_m else os.path.splitext(os.path.basename(src))[0]
                        return make_placeholder_for_img(src, alt, full_tag)
                    masked = re.sub(r'<img\s+([^>]+?)\s*/?>', html_img_repl, masked)

                    # Replace bare mentions of the image filename with links to the figure, but only in text nodes
                    parts = re.split(r'(<[^>]+>)', masked)
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            for basename, (fid, caption, placeholder) in mapping.items():
                                part = re.sub(rf'\b{re.escape(basename)}\b', f'<a href="#'+fid+f'">{caption}</a>', part)
                            parts[i] = part
                    masked = ''.join(parts)

                    # Replace placeholders with actual figure HTML
                    for placeholder, html in placeholders.items():
                        masked = masked.replace(placeholder, html)

                    final = unmask_code(masked)
                    simple_map = {k: (v[0], v[1]) for k, v in mapping.items()}
                    return final, simple_map

            # 1) Convert Obsidian-style image links ![[name]] -> markdown image syntax (if not already converted)
            def obsidian_repl(m):
                inner = m.group(1).strip()
                # leave as markdown-like reference; convert_obsidian_images will have already handled file copying
                return f'![]({inner})'
            masked = re.sub(r'!\[\[(.*?)\]\]', obsidian_repl, masked)

            # 2) Replace markdown images ![alt](src)
            def md_img_repl(m):
                alt = m.group(1).strip() or os.path.splitext(os.path.basename(m.group(2).strip()))[0]
                src = m.group(2).strip()
                return build_figure(src, alt)
            masked = re.sub(r'!\[(.*?)\]\((.*?)\)', md_img_repl, masked)

            # 3) Replace HTML <img ...> tags
            def html_img_repl(m):
                attrs = m.group(1)
                # find src and alt
                src_m = re.search(r'src\s*=\s*"([^"]+)"', attrs)
                alt_m = re.search(r'alt\s*=\s*"([^"]+)"', attrs)
                src = src_m.group(1) if src_m else ''
                alt = alt_m.group(1) if alt_m else os.path.splitext(os.path.basename(src))[0]
                return build_figure(src, alt)
            masked = re.sub(r'<img\s+([^>]+?)\s*/?>', html_img_repl, masked)

            # 4) Replace bare mentions of the image filename with links to the figure,
            # but only in text nodes (not inside HTML tags/attributes) to avoid breaking src attributes.
            parts = re.split(r'(<[^>]+>)', masked)
            for i, part in enumerate(parts):
                # even indices are text outside tags
                if i % 2 == 0:
                    for basename, (fid, caption) in mapping.items():
                        part = re.sub(rf'\b{re.escape(basename)}\b', f'<a href="#{fid}">{caption}</a>', part)
                    parts[i] = part

            masked = mask_code(md_text)

            # helper to build figure html and a placeholder mapping so we don't replace inside generated HTML
            placeholders = {}

            def build_figure_and_placeholder(src, alt):
                nonlocal fig_i
                fig_id = f"fig-{post_index}-{fig_i}"
                caption = f"Fig{post_index}.{fig_i} - {alt}"
                html = f'<figure class="post-figure" id="{fig_id}">\n  <img src="{src}" alt="{alt}"/>\n  <figcaption>{caption}</figcaption>\n</figure>'
                placeholder = f"__FIG_PLACEHOLDER_{fig_i}__"
                placeholders[placeholder] = html
                mapping[os.path.basename(src)] = (fig_id, caption, placeholder)
                fig_i += 1
                return placeholder

            # 1) Convert Obsidian-style image links ![[name]] -> markdown-like, but will be handled below
            def obsidian_repl(m):
                inner = m.group(1).strip()
                return f'![]({inner})'
            masked = re.sub(r'!\[\[(.*?)\]\]', obsidian_repl, masked)

            # 2) Replace markdown images ![alt](src) with placeholders
            def md_img_repl(m):
                alt = m.group(1).strip() or os.path.splitext(os.path.basename(m.group(2).strip()))[0]
                src = m.group(2).strip()
                return build_figure_and_placeholder(src, alt)
            masked = re.sub(r'!\[(.*?)\]\((.*?)\)', md_img_repl, masked)

            # 3) Replace HTML <img ...> tags with placeholders
            def html_img_repl(m):
                full_tag = m.group(0)
                attrs = m.group(1)
                src_m = re.search(r'src\s*=\s*"([^"]+)"', attrs)
                alt_m = re.search(r'alt\s*=\s*"([^"]+)"', attrs)
                src = src_m.group(1) if src_m else ''
                alt = alt_m.group(1) if alt_m else os.path.splitext(os.path.basename(src))[0]
                # Build figure that contains the original img tag to preserve attributes
                nonlocal fig_i
                fig_id = f"fig-{post_index}-{fig_i}"
                caption = f"Fig{post_index}.{fig_i} - {alt}"
                html = f'<figure class="post-figure" id="{fig_id}">\n  {full_tag}\n  <figcaption>{caption}</figcaption>\n</figure>'
                placeholder = f"__FIG_PLACEHOLDER_{fig_i}__"
                placeholders[placeholder] = html
                mapping[os.path.basename(src)] = (fig_id, caption, placeholder)
                fig_i += 1
                return placeholder
            masked = re.sub(r'<img\s+([^>]+?)\s*/?>', html_img_repl, masked)

            # 4) Replace bare mentions of the image filename with links to the figure, only in text nodes
            parts = re.split(r'(<[^>]+>)', masked)
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    for basename, (fid, caption, placeholder) in mapping.items():
                        part = re.sub(rf'\b{re.escape(basename)}\b', f'<a href="#{fid}">{caption}</a>', part)
                    parts[i] = part

            masked = ''.join(parts)

            # 5) Replace placeholders with actual figure HTML
            for placeholder, html in placeholders.items():
                masked = masked.replace(placeholder, html)

            final = unmask_code(masked)
            # convert mapping values to fid,caption only for caller convenience
            simple_map = {k: (v[0], v[1]) for k, v in mapping.items()}
            return final, simple_map

        cleaned_no_h1, figures = process_figures(cleaned_no_h1, post_idx)

        # Compute read time from cleaned content (metadata removed)
        read_time = compute_read_time_from_lines(cleaned_no_h1)

        # Extract challenge-specific metadata from the body (Room Name, Difficulty, Category)
        challenge_meta = extract_challenge_metadata(cleaned_no_h1)
        challenge_name = challenge_meta.get('room_name') or challenge_meta.get('room') or ''

        html_fragment = markdown.markdown(cleaned_no_h1, extensions=["fenced_code", "tables"])

        final_html = template.render(
            title=title,
            content=html_fragment,
            posts=posts_html,
            page_date=meta.get('date',''),
            page_author=meta.get('author',''),
            page_tags=meta.get('tags',[]),
            read_time=read_time,
            challenge=challenge_meta,
            challenge_name=challenge_name
        )

        output_filename = os.path.splitext(md_file)[0] + ".html"
        output_path = os.path.join(HTML_OUTPUT_DIR, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"Converted {md_file} -> {output_path}")

        generated_posts.append({
            "title": title,
            "url": f"html/{output_filename}",
            "date": meta.get('date',''),
            "author": meta.get('author',''),
            "tags": meta.get('tags',[]),
            "read_time": read_time
        })

    if generated_posts:
        update_blog_index(generated_posts)


if __name__ == "__main__":
    main()
