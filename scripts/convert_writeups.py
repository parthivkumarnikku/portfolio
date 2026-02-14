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
    Finds all Obsidian-style image links, copies the images to the assets
    directory, and replaces the links with standard markdown links.
    """
    image_pattern = r"!\[\[(.*?)\]\]"
    
    def replace_link(match):
        image_name = match.group(1)
        src_image_path = os.path.join(os.path.dirname(md_file_path), image_name)
        dest_image_path = os.path.join(ASSETS_DIR, image_name)

        if os.path.exists(src_image_path):
            shutil.copy(src_image_path, dest_image_path)
            # The path should be relative from docs/blog/html/ to docs/assets/images/writeups/
            return f"![](../../assets/images/writeups/{image_name})"
        else:
            print(f"Warning: Image not found for {image_name} in {md_file_path}")
            return f"![Image not found: {image_name}]"

    return re.sub(image_pattern, replace_link, content)

def update_blog_index(posts):
    """Updates the blog index file with a list of posts."""
    with open(BLOG_INDEX_FILE, "r") as f:
        index_content = f.read()
        post_list_html = ""
        for post in posts:
                # Posts listed on the index should reference the HTML output relative
                # to docs/blog/index.html, so keep the "html/" prefix here.
                post_list_html += f"""
            <article class=\"blog-card\">\n        <a href=\"{post['url']}\" class=\"blog-card-content\">\n          <h2 class=\"title\">{post['title']}</h2>\n          <p class=\"description\">\n            A new writeup about {post['title']}.\n          </p>\n          <span class=\"read-more\">\n            Read More <i class=\"fas fa-arrow-right\"></i>\n          </span>\n        </a>\n      </article>\n"""

        # Use a regex to find the opening <section ... class="blog-grid" ...> tag
        # so this works even when the tag has attributes (like an id).
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
        with open(md_file_path, "r") as f:
            content = f.read()
        title = get_post_title(content)
        output_filename = os.path.splitext(md_file)[0] + ".html"
        posts.append({
            "title": title,
            "url": f"html/{output_filename}"
        })
    return posts

def main():
    # Ensure output directories exist
    os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_NAME)

    # Get all posts
    all_posts = get_all_posts()

    # Generate HTML for the list of posts in the sidebar
    posts_html = ""
    for post in all_posts:
        # Sidebar lives in docs/blog/html/*.html so links to other posts
        # should be relative filenames (e.g. "blog1.html"), not
        # "html/blog1.html" which would resolve to html/html/... when
        # rendered from inside the html/ directory.
        post_filename = os.path.basename(post["url"])
        posts_html += f'<li><a href="{post_filename}"><i class="fas fa-file-alt"></i> {post["title"]}</a></li>'

    # Find all markdown files in the source directory
    md_files = [f for f in os.listdir(SRC_DIR) if f.endswith(".md")]
    
    generated_posts = []

    for md_file in md_files:
        md_file_path = os.path.join(SRC_DIR, md_file)
        
        with open(md_file_path, "r") as f:
            content = f.read()

        # Convert image links
        content = convert_obsidian_images(content, md_file_path)

        # Get title
        title = get_post_title(content)

        # Convert markdown to HTML
        html_fragment = markdown.markdown(content, extensions=['fenced_code', 'tables'])

        # Render the template
        final_html = template.render(title=title, content=html_fragment, posts=posts_html)

        # Save the HTML file
        output_filename = os.path.splitext(md_file)[0] + ".html"
        output_path = os.path.join(HTML_OUTPUT_DIR, output_filename)
        
        with open(output_path, "w") as f:
            f.write(final_html)
        
        print(f"Converted {md_file} to {output_path}")

        generated_posts.append({
            "title": title,
            "url": f"html/{output_filename}"
        })

    # Update the blog index page
    if generated_posts:
        update_blog_index(generated_posts)

if __name__ == "__main__":
    main()
