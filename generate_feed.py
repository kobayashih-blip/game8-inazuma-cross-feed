#!/usr/bin/env python3
import html
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from html.parser import HTMLParser
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace
from zoneinfo import ZoneInfo

SOURCE = "https://game8.jp/inazuma-cross/search?q="
SITE = "https://game8.jp"
ATOM = "http://www.w3.org/2005/Atom"
register_namespace("atom", ATOM)


class SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.item = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        if tag == "li" and "c-archiveSearchListItem" in classes:
            self.item = {"link": "", "title": "", "description": "", "date": ""}
        elif self.item is not None and tag == "a":
            href = attrs.get("href", "")
            if href.startswith("/inazuma-cross/"):
                self.item["link"] = SITE + href
        elif self.item is not None and tag == "p":
            fields = {
                "c-archiveSearchListItem__title": "title",
                "c-archiveSearchListItem__description": "description",
                "c-archiveSearchListItem__date": "date",
            }
            self.field = next((value for key, value in fields.items() if key in classes), None)

    def handle_data(self, data):
        if self.item is not None and self.field:
            self.item[self.field] += data

    def handle_endtag(self, tag):
        if tag == "p":
            self.field = None
        elif tag == "li" and self.item is not None:
            if self.item["link"] and self.item["title"] and self.item["date"]:
                self.items.append({key: value.strip() for key, value in self.item.items()})
            self.item = None
            self.field = None


def load_source():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).read_text(encoding="utf-8")
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "Mozilla/5.0 (personal RSS feed)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_date(value):
    return datetime.strptime(" ".join(value.split()), "%Y.%m.%d %H:%M").replace(
        tzinfo=ZoneInfo("Asia/Tokyo")
    )


def build_feed(items):
    rss = Element("rss", {"version": "2.0"})
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Game8 イナイレクロス 更新情報"
    SubElement(channel, "link").text = SOURCE
    SubElement(channel, "description").text = "Game8『イナイレクロス』の記事を最終更新日時順で配信"
    SubElement(channel, "language").text = "ja"
    SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
    SubElement(channel, "ttl").text = "15"
    SubElement(channel, f"{{{ATOM}}}link", {
        "href": "https://kobayashih-blip.github.io/game8-inazuma-cross-feed/feed.xml",
        "rel": "self",
        "type": "application/rss+xml",
    })
    for entry in sorted(items, key=lambda item: parse_date(item["date"]), reverse=True):
        item = SubElement(channel, "item")
        SubElement(item, "title").text = html.unescape(entry["title"])
        SubElement(item, "link").text = entry["link"]
        SubElement(item, "guid", {"isPermaLink": "true"}).text = entry["link"]
        SubElement(item, "pubDate").text = format_datetime(parse_date(entry["date"]))
        SubElement(item, "description").text = html.unescape(entry["description"])
    return rss


parser = SearchParser()
parser.feed(load_source())
if not parser.items:
    raise SystemExit("記事を取得できませんでした。Game8のHTML構造を確認してください。")
Path("public").mkdir(exist_ok=True)
ElementTree(build_feed(parser.items)).write("public/feed.xml", encoding="utf-8", xml_declaration=True)
print(f"public/feed.xml に {len(parser.items)} 件を書き出しました")
