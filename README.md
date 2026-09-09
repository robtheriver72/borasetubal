# Bora Y'all!

Events all over mainland Portugal — concerts, festivals, exhibitions, theatre, markets,
workshops and community days — gathered daily and published as a single static page.

Live site: https://robtheriver72.github.io/borasetubal/

*Bora* is Portuguese for "let's go".

## How it works

- `events.csv`, `markets.csv` and `freenif.csv` are the data. The first two mirror the
  Google Sheets "Freevent Events" and "Freevent Markets".
- `template.html` is the page, with a `__SNAPSHOT__` placeholder.
- `build.py` bakes the CSVs into the template and writes `index.html`. Events that have
  already finished are dropped at build time, so a freshly built page never ships a past event.
- `.github/workflows/rebuild.yml` runs `build.py` whenever a CSV or the template changes,
  and again every day at 06:30 UTC. The daily run is what makes finished events disappear:
  the filter in `build.py` only applies when it runs, so without it the site keeps showing
  events that are already over.

Rebuild locally:

```
python3 build.py            # snapshot dated today, Europe/Lisbon
python3 build.py 2026-10-01 # or pin the snapshot date
```

## The gap in the pipeline

**New events do not reach this repo on their own.** A daily Claude scheduled task crawls
listings and rewrites the Google Sheets in Drive, but nothing carries those sheets back into
`events.csv` — that step is manual. The daily Action rebuilds from whatever CSVs are
committed here; it cannot add events the sheets found.

The page contains code that reads the sheets live through the Drive connector, but it is
guarded by `window.claude`, which only exists when the page is open inside Claude. On GitHub
Pages that branch never runs and the baked snapshot is always what visitors see, so on the
live site that code is inert.

Closing the gap properly means one of: the scheduled task committing `events.csv` here
directly (which makes Drive unnecessary), or an Action pulling the sheets on a schedule
(which needs Google credentials in repo secrets, and has to cope with the task recreating
the sheets under new file IDs every day, because the Drive connector cannot edit cells in
place).

## Views

**List** (grouped by day), **Free w/ NIF** (museums free to residents on set days), and
**Markets** (recurring markets, with a "likely open this weekend" flag).

A month-grid Calendar and a schematic Map view existed earlier and were removed — they
duplicated the list without answering a question it couldn't. If either comes back, note
that the old view names may still sit in returning visitors' `localStorage`; the guard
after `applyHash()` is what stops an unknown saved view from rendering a blank page.

Location is one control, not three. A **Where** select picks any town in `TOWNS` as a
reference point, and a distance slider appears once one is chosen — bottom of the range
means that town only, top means genuinely no limit (`kmCap()` returns `Infinity` there,
because the slider stops at 650 km and Madeira is further out than that). The same filter
applies to Markets. An earlier separate "Town" select was redundant with this and is gone,
though old shared links using `#t=` are still honoured as a `Where` value.

## Things worth knowing before you edit

**Categories are a closed set.** `CATS` in `template.html` is the whole list, and every
category needs a colour variable in all three theme blocks (`:root`, the
`prefers-color-scheme: dark` media query, and `:root[data-theme="dark"]`) plus an entry in
`ICONS`. Anything the crawl emits that isn't in the set is folded in by `CAT_ALIAS` or lands
in `Other` — it can never end up invisible with no filter chip. Current set:

Local concert, Major concert, Festival, Food festival, Wine festival, Medieval festival,
Art exhibit, Theatre & performance, Market, Cinema, Sport, Workshop, Family, Pride,
Community, Heritage & talks, Other.

**If you add a category, update the daily task's prompt too**, or the next crawl will write
labels the page has to fold into `Other`.

**Distances can be unknown.** `~km from Setúbal` may be blank or non-numeric (Madeira, for
instance). `build.py` turns those into `null`, which renders as "distance n/a" and sorts
last — never as `0 km`.

**Towns need coordinates in `TOWNS` to take part in distance filtering.** Without them an
event falls back to its `~km from Setúbal` value, and a market to the same, so a town added
to the sheet but not to `TOWNS` will still appear but will sort and filter off that column
rather than off a real distance.

**Calendar handoff is .ics first.** Each card's "Add" builds a single-event .ics and
downloads it, which opens directly in Apple Calendar on iOS/macOS and imports into Outlook
and the rest; the smaller "Google" link beside it is the one-click path for Google Calendar
only. The toolbar exports the whole filtered set the same way. Note that downloads are
blocked inside Claude's artifact viewer — the .ics buttons only work on the real site.

**Dates are formatted locally, not in UTC.** Use the `isoLocal` helper rather than
`toISOString()`; the latter shifts "today" by a day for the first hour after midnight in
Lisbon.

## What the page stores in your browser

Filters, saved events (the ★ on each card) and the theme choice live in `localStorage` on
one browser only. Nothing is sent anywhere and there are no accounts. Because saved events
are per-browser, "Copy link to this view" deliberately leaves them out of the URL — a shared
link carries the filters, not somebody else's stars.
