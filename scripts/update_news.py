#!/usr/bin/env python3
"""Refresh Atlas of the Cosmos from public NASA RSS feeds, without API keys.

Runs inside GitHub Actions at ~07:00 IST daily. If providers are unavailable,
keeps the previous published snapshot rather than claiming fresh results.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import ssl
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
JSON_FILE = ROOT / 'data' / 'news.json'
JS_FILE = ROOT / 'data' / 'news.js'
FEEDS = [
 ('NASA Artemis', 'Artemis', 'https://www.nasa.gov/blogs/artemis/feed/'),
 ('NASA Artemis missions', 'Artemis', 'https://www.nasa.gov/missions/artemis/feed/'),
 ('NASA Technology', 'Engineering', 'https://www.nasa.gov/technology/feed/'),
 ('NASA Science', 'Science', 'https://science.nasa.gov/feed/'),
 ('NASA Space Station', 'Space Station', 'https://www.nasa.gov/missions/station/feed/'),
 ('NASA news', 'Other', 'https://www.nasa.gov/feed/'),
 ('NASA mission blogs', 'Other', 'https://www.nasa.gov/blogs/feed/'),
]
IOTD = ('NASA Image of the Day', 'Science', 'https://www.nasa.gov/feeds/iotd-feed/')
NS = {'content': 'http://purl.org/rss/1.0/modules/content/', 'media': 'http://search.yahoo.com/mrss/', 'dc': 'http://purl.org/dc/elements/1.1/'}
USER_AGENT = 'Atlas-of-the-Cosmos/1.0 (public RSS reader; static GitHub Pages)' 

class PlainText(HTMLParser):
    def __init__(self): super().__init__(); self.bits = []
    def handle_data(self, s): self.bits.append(s)
    def get(self): return ' '.join(' '.join(self.bits).split())

def strip_html(s):
    p=PlainText()
    try: p.feed(s or '')
    except Exception: return ' '.join(str(s or '').split())
    return unescape(p.get())

def child_text(node, name):
    x=node.find(name)
    return ''.join(x.itertext()).strip() if x is not None else ''

def date_iso(s):
    if not s: return None
    try:
        d=parsedate_to_datetime(s)
    except Exception:
        try: d=datetime.fromisoformat(s.replace('Z','+00:00'))
        except Exception: return None
    if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat()

def trusted_url(s):
    try:
        p=urllib.parse.urlparse(s)
        return p.scheme=='https' and (p.hostname=='nasa.gov' or (p.hostname or '').endswith('.nasa.gov'))
    except (TypeError,ValueError): return False

def category(title, default):
    t=title.lower()
    if any(x in t for x in ('artemis','moon mission','orion crew','lunar landing','lunar science','sls rocket')): return 'Artemis'
    if any(x in t for x in ('heat shield','thermal','manufactur','3d-print','3d print','nuclear electric','reactor','engineer','propulsion','robotic','spacecraft test','technology','deployable','satellite inspection')): return 'Engineering'
    if any(x in t for x in ('perseverance','mars rover','mars helicopter','mars sample','mars exploration')): return 'Mars'
    if any(x in t for x in ('space station','expedition','crew-','spacewalk','microgravity','iss ')): return 'Space Station'
    if any(x in t for x in ('webb','hubble','planet','galax','black hole','star','telescope','science','asteroid','ocean','earth','weather','climate','solar')): return 'Science'
    return default

def fetch_feed(feed):
    source, cat, url=feed
    req=urllib.request.Request(url, headers={'User-Agent': USER_AGENT,'Accept':'application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.8'})
    with urllib.request.urlopen(req,timeout=25,context=ssl.create_default_context()) as response:
        content=response.read(7_000_000)
    root=ET.fromstring(content)
    items=root.findall('.//item')
    is_atom=False
    if not items:
        items=root.findall('{http://www.w3.org/2005/Atom}entry')
        is_atom=True
    parsed=[]
    for item in items:
        if is_atom:
            a=item.find('{http://www.w3.org/2005/Atom}link')
            link=a.get('href','') if a is not None else ''
            title=child_text(item,'{http://www.w3.org/2005/Atom}title')
            pub=child_text(item,'{http://www.w3.org/2005/Atom}published') or child_text(item,'{http://www.w3.org/2005/Atom}updated')
            body=child_text(item,'{http://www.w3.org/2005/Atom}summary')
        else:
            link=child_text(item,'link')
            title=child_text(item,'title')
            pub=child_text(item,'pubDate') or child_text(item,'{http://purl.org/dc/elements/1.1/}date')
            body=child_text(item,'description') or child_text(item,'{http://purl.org/rss/1.0/modules/content/}encoded')
        if not trusted_url(link): continue
        title=strip_html(title)
        if not title: continue
        dt=date_iso(pub)
        if not dt: continue
        parsed.append({'title':title[:180], 'category':category(title,cat), 'published':dt,
                       'url':link.split('#')[0], 'summary':strip_html(body)[:230], 'source':source})
    return source, parsed, root

def image_from(root):
    for item in root.findall('.//item')[:5]:
        title=strip_html(child_text(item,'title'))
        link=child_text(item,'link')
        pub=date_iso(child_text(item,'pubDate'))
        for el in list(item.findall('media:content',NS))+list(item.findall('media:thumbnail',NS))+list(item.findall('enclosure')):
            url=el.get('url','')
            if trusted_url(url) and not any(s in url.lower() for s in ('.mp4','.mov','.pdf')):
                return {'title':title,'url':link,'image':url,'published':pub,'caption':'NASA Image of the Day · NASA'}
    return None

def main():
    old=json.loads(JSON_FILE.read_text('utf-8')) if JSON_FILE.exists() else {'articles':[]}
    new_items=[]; successes=[]; image=None; errors=[]
    all_feeds=FEEDS+[IOTD]
    with ThreadPoolExecutor(max_workers=7) as pool:
        calls={pool.submit(fetch_feed, f):f[0] for f in all_feeds}
        for fut in as_completed(calls):
            try:
                name, items, root=fut.result()
                successes.append(name)
                if name==IOTD[0]: image=image_from(root)
                else: new_items.extend(items)
                print(f'{name}: {len(items)} items')
            except Exception as e:
                errors.append(f'{calls[fut]}: {type(e).__name__}: {e}')
    print('Successfully checked',len(successes),'feeds')
    for err in errors: print('WARN:',err)
    if not new_items:
        print('No NASA news retrieved; retaining the previous snapshot and update timestamp.')
        return
    cutoff=datetime.now(timezone.utc)-timedelta(days=120)
    # Merge with earlier stories so daily feeds with short windows do not empty the archive.
    by_url={}
    for item in list(old.get('articles',[]))+new_items:
        if not trusted_url(item.get('url','')): continue
        dt=date_iso(item.get('published',''))
        if not dt: continue
        d=datetime.fromisoformat(dt)
        if d<cutoff or d>datetime.now(timezone.utc)+timedelta(days=1): continue
        link=item['url'].split('?')[0].rstrip('/')
        previous=by_url.get(link)
        if previous is None or (len(item.get('summary',''))>len(previous.get('summary',''))):
            item['published']=dt
            by_url[link]=item
    result=sorted(by_url.values(),key=lambda a:a['published'],reverse=True)[:100]
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    data={'updated_at':now,'status':'updated','sources':successes,'articles':result,
          'feed_success_count':len(successes),'feed_failure_count':len(errors)}
    if image and image.get('image'): data['image_of_day']=image
    elif old.get('image_of_day'):data['image_of_day']=old['image_of_day']
    JSON_FILE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    JS_FILE.write_text('window.NASA_NEWS = '+json.dumps(data,ensure_ascii=False,indent=2).replace('</','<\\/')+';\n',encoding='utf8')
    print(f'Wrote {len(result)} stories; snapshot time {now}.')

if __name__=='__main__': main()
