"""Fetch public DPM lineage pages and extract their primary biography, not glossary popovers."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, html, json, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
class BiographyParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div':
            if self.depth: self.depth += 1
            elif attrs.get('id') == 'content_with_keyword': self.depth = 1
        if self.depth and tag in ('br', 'p'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if self.depth and tag == 'div': self.depth -= 1
        elif self.depth and tag == 'p': self.parts.append('\n')
    def handle_data(self, data):
        if self.depth: self.parts.append(data)
def extract_biography(raw):
    parser = BiographyParser(); parser.feed(raw)
    text = '\n'.join(re.sub(r'[\t \u3000]+', ' ', line).strip() for line in ''.join(parser.parts).splitlines())
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    if len(text) < 100: raise ValueError('Primary biography missing or unexpectedly short; do not ingest glossary as biography')
    return text

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--cached', action='store_true'); args = ap.parse_args()
    items = json.loads((ROOT/'Docs/source-manifest.json').read_text())
    for item in items:
        raw = ROOT/'Docs'/f"{item['key']}.html"
        if not args.cached:
            temp = raw.with_suffix('.download')
            subprocess.run(['curl','--fail','-L','--max-time','40','-sS',item['url'],'-o',str(temp)],check=True)
            extract_biography(temp.read_text()); temp.replace(raw)
        text = extract_biography(raw.read_text())
        # The manifest and primary document must agree on which person was fetched.
        name = re.search(r'朱[\u4e00-\u9fff]{1,3}', item['title'])
        if name and name[0] not in text: raise ValueError(f"Identity mismatch: {item['key']} {name[0]}")
        (ROOT/'Docs'/f"{item['key']}.txt").write_text(text)
        print(item['key'],len(text),text[:45])
if __name__ == '__main__': main()
