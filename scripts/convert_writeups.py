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
        post_list_html += f"""
      <article class="blog-card">
        <a href="{post['url']}" class="blog-card-content">
          <h2 class="title">{post['title']}</h2>
          <p class="description">
            A new writeup about {post['title']}.
          </p>
          <span class="read-more">
            Read More <i class="fas fa-arrow-right"></i>
          </span>
        </a>
      </article>
"""

    # Replace the content within the blog grid
    start_marker = '<section class="blog-grid">'
    end_marker = '</section>'
    
    start_index = index_content.find(start_marker)
    if start_index == -1:
        print(f"Warning: Could not find start marker in {BLOG_INDEX_FILE}")
        return

    start_index += len(start_marker)
    end_index = index_content.find(end_marker, start_index)
    
    if end_index == -1:
        print(f"Warning: Could not find end marker in {BLOG_INDEX_FILE}")
        return

    # Find all article tags within the blog grid and replace them
    new_index_content = index_content[:start_index] + post_list_html + index_content[end_index:]

    with open(BLOG_INDEX_FILE, "w") as f:
        f.write(new_index_content)
    print(f"Updated blog index at {BLOG_INDEX_FILE}")


def main():
    # Ensure output directories exist
    os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_NAME)

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
        final_html = template.render(title=title, content=html_fragment)

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
