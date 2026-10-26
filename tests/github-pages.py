"""Validate the built project site before uploading it to GitHub Pages."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent / 'public-build/github-pages'
BASE = '/statistik-/'


class Links(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.page = page

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('href', 'src') or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or value.startswith('#'):
                continue
            if url.path.startswith('/'):
                assert url.path.startswith(BASE), (self.page, value)
                path = ROOT / unquote(url.path[len(BASE):])
            else:
                path = self.page.parent / unquote(url.path)
            assert path.exists(), (self.page, value)


for route in ('', 'focus', 'lan', 'score', 'boring'):
    page = ROOT / route / 'index.html'
    assert page.is_file(), page
for page in ROOT.rglob('*.html'):
    Links(page).feed(page.read_text(encoding='utf-8'))
revisions = json.loads((ROOT / 'data/score-revisions.json').read_text())
assert revisions
for revision in revisions:
    assert revision['file'].startswith(BASE + 'data/score-history/')
    assert (ROOT / revision['file'][len(BASE):]).is_file()
print('PASS Pages routes, static links, assets and score-history downloads')
