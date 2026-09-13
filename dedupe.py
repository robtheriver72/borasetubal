#!/usr/bin/env python3
"""Catch same-event-two-spellings pairs that a normalised-title match misses.

Two rows on the same date in the same town whose titles share most of their
meaningful words are almost certainly one event listed twice.
"""
import csv, re, unicodedata, os, sys
from itertools import combinations

BASE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(BASE, "events.csv")

STOP = {"de","da","do","das","dos","e","a","o","as","os","em","no","na","the","of",
        "and","march","marcha","pride","festival","festa","concerto","concert",
        "com","para","um","uma","por","ao","aos","2026","2027"}

def toks(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return {w for w in s.split() if len(w) > 2 and w not in STOP}

rows = list(csv.DictReader(open(PATH, encoding="utf-8")))
by = {}
for i, r in enumerate(rows):
    by.setdefault((r["Start date"], r["Town"]), []).append((i, r))

sus = []
for key, group in by.items():
    for (i, a), (j, b) in combinations(group, 2):
        ta, tb = toks(a["Event"]), toks(b["Event"])
        if not ta or not tb:
            continue
        overlap = len(ta & tb) / min(len(ta), len(tb))
        if overlap >= 0.6:
            sus.append((overlap, i, j, a, b))

sus.sort(reverse=True, key=lambda x: x[0])
print(f"{len(sus)} suspected duplicate pair(s)\n")
for ov, i, j, a, b in sus:
    print(f"  [{ov:.0%}] {a['Start date']} {a['Town']}")
    print(f"        A row{i}: {a['Event'][:60]!r}  @ {a['Venue'][:34]!r}  ({a['Added on']})")
    print(f"        B row{j}: {b['Event'][:60]!r}  @ {b['Venue'][:34]!r}  ({b['Added on']})")
