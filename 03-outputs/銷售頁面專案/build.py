import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_DIR = os.path.join(BASE_DIR, 'v_dev')
DIST_DIR = os.path.join(BASE_DIR, 'v_current')
DIST_FILE = os.path.join(DIST_DIR, 'index.html')

def read_file(filename):
    with open(os.path.join(DEV_DIR, filename), 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("🚀 Starting build process...")
    
    # Read source files
    print("📖 Reading source files...")
    css_content = read_file('styles.css')
    js_content = read_file('script.js')
    html_full = read_file('index.html')

    # Extract HTML body content
    start_marker = '<!-- CONTENT START -->'
    # We don't have an explicit end marker in the user's provided code, 
    # but we know it ends before the script tag or body close.
    # Let's use the wrapper div as the boundary.
    
    if start_marker in html_full:
        # Extract everything after start marker
        temp = html_full.split(start_marker)[1]
        # Remove the closing script tag and body/html tags if present
        if '<script src="script.js"></script>' in temp:
            html_body = temp.split('<script src="script.js"></script>')[0].strip()
        else:
            # Fallback if script tag is missing or different
            html_body = temp.split('</body>')[0].strip()
    else:
        print("⚠️ Markers not found, attempting fallback extraction...")
        # Fallback: Extract everything inside body
        if '<body>' in html_full and '</body>' in html_full:
             html_body = html_full.split('<body>')[1].split('</body>')[0].strip()
             # Remove script include if present
             html_body = html_body.replace('<script src="script.js"></script>', '')
        else:
             print("❌ Error: Could not extract content. Please ensure standard HTML structure in v_dev/index.html")
             return

    # Extract Link tags (Fonts/Icons) from Head
    # We want to preserve <link> tags but NOT <meta> or <title> or <head> wrapper
    head_links = []
    if '<head>' in html_full and '</head>' in html_full:
        head_content = html_full.split('<head>')[1].split('</head>')[0]
        for line in head_content.split('\n'):
            if '<link' in line:
                # Exclude local style link
                if 'styles.css' not in line:
                    head_links.append(line.strip())
    
    links_str = '\n'.join(head_links)

    # Construct monolithic file for Systeme.io
    # Structure:
    # 1. External Links (Fonts/Icons) - Placed at top (Browser usually handles this fine in body)
    # 2. CSS in <style>
    # 3. HTML Body Content
    # 4. JS in <script>
    
    print("🔨 Assembling monolithic file...")
    monolithic_content = f"""{links_str}

<style>
{css_content}
</style>

{html_body}

<script>
{js_content}
</script>"""

    # Ensure output directory exists
    os.makedirs(DIST_DIR, exist_ok=True)

    # Write output
    with open(DIST_FILE, 'w', encoding='utf-8') as f:
        f.write(monolithic_content)

    print(f"✅ Build complete! Output saved to: {DIST_FILE}")
    print(f"📊 Total size: {len(monolithic_content)} bytes")
    print("ℹ️  Note: <head> tags were stripped for Systeme.io compatibility.")

if __name__ == "__main__":
    main()
