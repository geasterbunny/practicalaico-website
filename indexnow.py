"""
Ping IndexNow with every URL in sitemap.xml.

IndexNow is free and account-less: Bing, Yandex and Seznam accept a URL list as
long as a key file is reachable at the site root. Bing's index is what feeds
Copilot and ChatGPT search, so this is the cheapest route into AI answers.

Google does NOT use IndexNow — it still needs Search Console (see README-SEO.md).

    py indexnow.py           # submit every sitemap URL
    py indexnow.py --dry     # print what would be sent
"""
import json
import pathlib
import re
import sys
import urllib.request

HOST = "practicalaico.ai"
KEY = next(p.stem for p in pathlib.Path(__file__).parent.glob("*.txt")
           if re.fullmatch(r"[0-9a-f]{32}", p.stem))
ENDPOINT = "https://api.indexnow.org/IndexNow"


def urls():
    sm = (pathlib.Path(__file__).parent / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", sm)


def main(dry: bool) -> None:
    body = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls(),
    }
    print(f"{len(body['urlList'])} URLs, key {KEY[:8]}...")
    if dry:
        print("\n".join(body["urlList"]))
        return
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        # 200 = accepted, 202 = accepted but key not yet verified
        print(f"HTTP {r.status} {r.reason}")


if __name__ == "__main__":
    main("--dry" in sys.argv)
