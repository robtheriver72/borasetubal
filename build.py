#!/usr/bin/env python3
"""Build index.html for Bora Setúbal from events.csv + markets.csv + template.html.
Usage: python3 build.py [snapshot-date]  (defaults to today, Europe/Lisbon)"""
import csv, json, sys, datetime, zoneinfo, pathlib
root = pathlib.Path(__file__).parent
date = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Lisbon")).date().isoformat()
def num(s):
    try: return int(str(s).strip() or 0)
    except ValueError: return 0
ev = [dict(start=r['Start date'], end=r['End date'] or r['Start date'], name=r['Event'], type=r['Type'], cat=r['Category'] or 'Other',
           town=r['Town'], venue=r['Venue'], km=num(r['~km from Setúbal']), fp=r['Free / Paid'] or 'Unknown', price=r['Price (€)'],
           desc=r['Description'], freq=r['Frequency'], src=r['Source'], img=r.get('Image','')) for r in csv.DictReader(open(root/'events.csv', encoding='utf-8'))]
ev = [e for e in ev if e['end'] >= date]  # never ship past events
mk = [dict(name=r['Market'], cat=r['Category'], town=r['Town'], loc=r['Location'], km=num(r['~km from Setúbal']), freq=r['Frequency'],
           days=r['Days & hours'], goods=r['Types of goods'], entry=r['Entry'], note=r['Notes'], src=r['Source'], img=r.get('Image','')) for r in csv.DictReader(open(root/'markets.csv', encoding='utf-8'))]
snap = json.dumps({'date': date, 'events': ev, 'markets': mk}, ensure_ascii=False).replace('</', '<\\/')
body = open(root/'template.html', encoding='utf-8').read().replace('__SNAPSHOT__', snap)
i = body.index('</style>') + len('</style>')
doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       + body[:i] + '</head><body>' + body[i:] + '</body></html>')
(root/'index.html').write_text(doc, encoding='utf-8')
print(f'index.html built: {len(ev)} events, {len(mk)} markets, snapshot {date}')
