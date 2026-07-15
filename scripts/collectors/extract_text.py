#!/usr/bin/env python3
"""Extract readable text from downloaded tier-list HTML pages (stdlib only)."""
import re
import sys
from html.parser import HTMLParser

SKIP = {"script", "style", "noscript", "svg", "head"}
BLOCK = {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "h5", "section", "article", "br", "table"}


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip_depth += 1
        if tag in BLOCK:
            self.parts.append("\n")
        if tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip_depth:
            self.skip_depth -= 1
        if tag in BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)


def extract(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    p = TextExtractor()
    p.feed(html)
    text = "".join(p.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


if __name__ == "__main__":
    print(extract(sys.argv[1]))
