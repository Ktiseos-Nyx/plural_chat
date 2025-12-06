import os
from markdown_it import MarkdownIt
from bs4 import BeautifulSoup

# --- Configuration ---
# Use an absolute path to the README.md file
# os.path.abspath() gets the full path to the file
FILE_TO_PARSE = os.path.abspath("DIY_REFACTOR_GUIDE.md")

# --- Main Script ---

# 1. Initialize the Markdown parser
# We pass 'gfm-like' to enable GitHub Flavored Markdown rules
md = MarkdownIt("gfm-like")

# 2. Read the content of the README file
try:
    with open(FILE_TO_PARSE, "r", encoding="utf-8") as f:
        markdown_text = f.read()
    print("--- Successfully read README.md ---")
except FileNotFoundError:
    print(f"Error: The file was not found at {FILE_TO_PARSE}")
    exit()

# 3. Convert the Markdown content to HTML
html_content = md.render(markdown_text)
# You can uncomment the line below to see the intermediate HTML
# print("\n--- Rendered HTML ---\n", html_content)

# 4. Parse the HTML and extract the plain text
# 'html.parser' is a built-in, good-enough parser
soup = BeautifulSoup(html_content, "html.parser")
plain_text = soup.get_text(separator="\n", strip=True)

# 5. Print the final, clean text
print("\n--- Parsed Text from README ---")
print(plain_text)
