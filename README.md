# Bora Y'all!

Events all over mainland Portugal — concerts, festivals, exhibitions, theatre, markets,
workshops and community days — gathered daily and published as a single static page.

Live site: https://robtheriver72.github.io/borasetubal/

*Bora* is Portuguese for "let's go".

## How it works

- `events.csv`, `markets.csv` and `freenif.csv` are the data. This repo is the source of
  truth; the Google Sheets are a mirror, not the master.
- `concelhos.csv` is the crawl's backbone — see "How the country gets covered" below.
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

## How the country gets covered

For a long time coverage was driven by a hand-curated list of about 25 sites, and it showed:
Setúbal, a town of 120,000, had more events than Porto. That was never a bug in the code. It
was that Setúbal was the one place whose **municipal agenda** was being read, while Braga's
26 events were all from a single venue's brochure (Fórum Braga, 100%) and Faro's from one
theatre (Teatro das Figuras, 95%). The crawl found whatever the list pointed at and stopped.

`concelhos.csv` replaces the list. It holds all 202 Portuguese concelhos that have active
listings, with the URL slug for their agenda page, how many events that page shows, how many
the site currently has, and when it was last swept. On 9 Sept 2026 those pages listed 5,522
events between them; the site had 231. Setúbal was the only concelho at parity — its agenda
listed 31 and the site had 36.

The daily task sweeps 8–12 concelhos per run off that ledger, biggest gap first, always
including Lisboa or Porto, at least two small concelhos, and at least one within 60 km of
Setúbal. **There is no per-venue cap and no per-town quota.** One was tried and removed: a
cap limits what can be added, which makes the site smaller rather than better balanced. The
answer to a town with one venue is to sweep its agenda, not to refuse its events.

### What the source pages do wrong

Worth knowing before adding a source, because each of these has already produced a bad row:

- **Years are missing.** The agenda prints `qua 09 set`. Resolve the year from the weekday —
  9 Sept 2026 is a Wednesday — never by assuming it's this year.
- **Placeholder dates.** Montijo prints every undated ongoing item under one repeated date.
  Twelve rows sharing a date means those rows are undated, not that twelve things happen then.
- **Stale pages.** `nocartaz.pt/concelhos/faro/` was still serving August in September. If the
  first listed date is already past, the page is stale — `viralagenda.com/pt/faro` covers the
  same district and was live.
- **Archive content.** Óbidos returned a page of 2025 dates (FÓLIO 2025). Dropped entirely.
- **Titles that read like venues.** "PROMISED VALLEY CONFERENCE CENTER" is a play.

The `Notes` column in `concelhos.csv` is where these get recorded, so the next run doesn't
spend a fetch rediscovering them.

### Publishing

The scheduled task commits to this repo directly. If it cannot push it must say
**"NOT PUBLISHED — needs manual upload"** at the top of its report rather than reporting
success — a run whose data never reached the repo did nothing, and that failure was silent
for weeks.

The page also contains a branch that reads the Google Sheets live through the Drive
connector, guarded by `window.claude`. That object only exists when the page is open inside
Claude, so on GitHub Pages the branch never runs and visitors always see the baked snapshot.

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

## "Mais Info" — why cards search instead of linking the source

Each event card links to a web search built from its own title, venue and town, not to
its `Source` URL. Most Source values are aggregator landing pages
(`timeout.pt/coisas-para-fazer…`, `viralagenda.com/pt/setubal`) that drop the reader on a
generic listing rather than the event. `Source` stays in the CSV — the daily task's
source-link rule and Audit Log depend on it — it just isn't what the card links to.

Two things make the search work, and both are data-dependent:

The **whole title** goes into the query, brackets included, because it already carries the
Portuguese original where there is one and Google ignores the parentheses. Extracting "just
the Portuguese part" was tried and dropped: it discarded `7.ª Marcha do Orgulho de Santarém`
for starting with a digit while keeping English like `Street Festivities`.

The **venue** goes in too, and it matters more than it looks. Proper nouns survive
translation, so `Classic Cinema Cycle: 'Cops and Robbers'` alone returns Wikipedia pages
about unrelated films, while adding `Luísa Todi Municipal Forum` surfaces the Portuguese
listing and the council's own article. Vague venues (`Various venues`, anything with `TBC`,
multi-venue strings, or the town name repeated) are filtered out as noise — 199 of 213 rows
currently contribute a venue.

The upstream lever is the daily task's language rule: a row whose title exists only as an
English translation searches poorly. That rule now requires the Portuguese original in
brackets on every translated title, and Portuguese proper nouns kept in `Venue`.

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
rather than off a real distance. Every concelho the sweep is likely to reach next is already
in there; add new ones as they're swept.

**Calendar export is one toolbar button, not per-card.** Per-event "Add to calendar"
controls were tried and removed — two extra controls on every card for a rarely-used action
made the cards a mess. The toolbar exports the whole filtered set as .ics, which is enough.
Note that downloads are blocked inside Claude's artifact viewer, so that button only works
on the real site.

**Icons are a Google font of ligatures, and the page checks it actually loaded.** If it
hasn't — blocked host, flaky connection — every icon would otherwise render as its own name
("family_restroom", "contrast"). `iconFontWorks()` measures a ligature: one glyph is ~24px,
the literal word runs to ~180px. The probe must NOT carry the `.material-symbols-outlined`
class, because `no-icons` sets that class to `display:none` and a classed probe would then
measure 0px, read as "fine", and flip the state back on the next call.

**The logo is a CSS mask, not an image.** The azulejo mark is one flat colour on
transparency, so it ships as a single 41 KB WebP used as a `mask-image`, with
`background-color: var(--logo)` painting it. That is why it can be deep blue on paper and
light periwinkle on a dark ground from one asset — a plain `<img>` would have needed two,
and a `#010D87` logo on a dark background is unreadable. There is an `@supports` fallback to
a text wordmark for the rare browser without mask support, and an `h1.sr-only` carries the
real heading since the visible wordmark is pixels. Inlined as a data URI deliberately: the
repo is updated by dragging files into GitHub's uploader, and a separate file is one thing
that can be forgotten.

**The list leads with dated days, not long runs.** Anything that started before today is
pushed to a collapsed "Still on" section at the bottom, ordered by what ends soonest. The
page previously opened with 25 ongoing exhibitions, which is the wrong first impression for
a site called *é agora*.

**The picks strip is editorial, computed from data you already have.** `pickScore` rewards
free entry, short runs, proximity and distinctive categories, and penalises arena concerts;
then a diversity pass refuses two picks sharing a category or a town. It falls back from the
weekend to the next seven days, and hides itself below three candidates.

**Dates are formatted locally, not in UTC.** Use the `isoLocal` helper rather than
`toISOString()`; the latter shifts "today" by a day for the first hour after midnight in
Lisbon.

## What the page stores in your browser

Filters, saved events (the ★ on each card) and the theme choice live in `localStorage` on
one browser only. Nothing is sent anywhere and there are no accounts. Because saved events
are per-browser, "Copy link to this view" deliberately leaves them out of the URL — a shared
link carries the filters, not somebody else's stars.
