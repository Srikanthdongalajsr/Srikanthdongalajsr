"""Writes the 3 latest long YouTube videos into README.md between the VIDEOS markers.

Public RSS feed only (no API key). Shorts are skipped: youtube.com/shorts/<id> answers 200
for a Short and redirects for a normal video. Videos under 2 minutes are not checked here;
the RSS feed has no duration, so the Shorts check is the filter.
"""
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CHANNEL_ID = "UCWZWdpd-F8sqjQdwOOHbIeQ"
README = Path(__file__).resolve().parent.parent / "README.md"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
UA = {"User-Agent": "Mozilla/5.0 (profile-readme-updater)"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def is_short(vid):
    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", headers=UA), timeout=15)
        return r.status == 200
    except urllib.error.HTTPError:
        return False  # 3xx raised as HTTPError when redirects are blocked: a normal video


def main():
    xml = urllib.request.urlopen(urllib.request.Request(
        f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}", headers=UA), timeout=20).read()
    picks = []
    for e in ET.fromstring(xml).findall("a:entry", NS):
        vid = e.find("yt:videoId", NS).text
        if is_short(vid):
            continue
        picks.append((vid, e.find("a:title", NS).text.strip()))
        if len(picks) == 3:
            break
    if not picks:
        return
    w = "32%" if len(picks) == 3 else "49%"
    cells = "\n".join(
        f'<a href="https://www.youtube.com/watch?v={v}" title="{t.replace(chr(34), "&quot;")}">'
        f'<img src="https://i.ytimg.com/vi/{v}/mqdefault.jpg" width="{w}" alt="{t.replace(chr(34), "&quot;")}"></a>'
        for v, t in picks)
    block = f"<!-- VIDEOS:START -->\n<p>\n{cells}\n</p>\n<!-- VIDEOS:END -->"
    text = README.read_text(encoding="utf-8")
    new = re.sub(r"<!-- VIDEOS:START -->.*?<!-- VIDEOS:END -->", block, text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("updated:", [t for _, t in picks])
    else:
        print("no change")


if __name__ == "__main__":
    main()
