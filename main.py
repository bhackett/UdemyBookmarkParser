from html.parser import HTMLParser
from collections import Counter
from datetime import datetime
from pathlib import Path
import sys

class LinkTitleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_href = None
        self.capture = False
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.capture = True
            self.current_href = dict(attrs).get("href")

    def handle_data(self, data):
        if self.capture:
            self.buffer.append(data.strip())

    def handle_endtag(self, tag):
        if tag == "a" and self.capture:
            title = " ".join(self.buffer).strip()
            self.links.append((self.current_href, title))
            self.buffer.clear()
            self.capture = False

def get_bookmark_filename():
    today = datetime.today()
    return f"bookmarks_{today.month}_{today.day}_{str(today.year)[-2:]}.html"

def extract_links_from_file(filepath):
    parser = LinkTitleExtractor()
    with filepath.open("r", encoding="utf-8") as f:
        parser.feed(f.read())
    return parser.links

def write_udemy_bookmarks(links, output_path):
    started = False
    count = 0
    with output_path.open("w", encoding="utf-8") as out:
        for _, title in links:
            if title.startswith("Course: _Start_ | Udemy") and not started:
                started = True
                continue
            if started and title.startswith("Course: "):
                cleaned_title = title.replace("Course: ", "", 1).replace(" | Udemy", "")
                out.write(f"{cleaned_title}\n")
                count += 1
    return count

def find_duplicates(file_path):
    with file_path.open("r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return {line: count for line, count in Counter(lines).items() if count > 1}

def main():
    bookmark_file = Path(get_bookmark_filename())
    if not bookmark_file.exists():
        print(f"File not found: {bookmark_file}")
        sys.exit()

    links = extract_links_from_file(bookmark_file)
    output_file = Path("Udemy Bookmarks.txt")
    count = write_udemy_bookmarks(links, output_file)
    print(f"Bookmarks processed: {count}")

    duplicates = find_duplicates(output_file)
    if duplicates:
        print("Duplicate lines found:")
        for line, count in duplicates.items():
            print(f"{line} (x{count})")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    main()