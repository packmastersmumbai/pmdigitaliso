# Pack Masters Digital ISO — how to consume it

Hand this to another project. Verified 2026-09-11 against the live registry.

There is **one registry**: a JSON file. Everything else reads it.

---

## 1. If your app is inside the packmasters Google account

Add **PMCore** as an Apps Script library and call it. That is the whole
integration — no endpoint, no token, no sync.

```
Editor > Libraries > Add by script id
  1XrbNFnQWob8l5GuSCUyMT5u0tUX7netkqidSYEgqXpBV3nxE7KQunp9v
  identifier: PMCore
```

```js
var d = PMCore.doc('PM/FRM/5S-01');
//  { code, title, version, effective, clause, standard, state, url,
//    published_at, degraded }

PMCore.stamp('PM/FRM/5S-01');
//  "PM/FRM/5S-01 Rev 2.0, effective 01/07/2026"

PMCore.data('roster');              // any file in the data layer
PMCore.fetch('housekeeping_5s', '2026-07');   // live rows from another app
PMCore.health();                    // is the registry sound right now
PMCore.announce('5s', ISO_DOCS);    // once a day — tells the ISO you are bound
PMCore.log('5S app', 'submitted', 'Z-04');    // one audit trail
```

**`doc()` returning null is a stop, not an empty result.** Rendering a form that
cites no controlled document is exactly the finding this system exists to
prevent.

**Print `stamp()` on every record your app writes.** It is what makes the record
auditable: it says which issue of the document the work was done against.

---

## 2. If your app is outside the account — the JSON API

No credentials. Start at the index; it names every endpoint and their shapes.

```
https://packmastersmumbai.github.io/pmdigitaliso/api.json
```

| Endpoint | What you get |
|---|---|
| `/register.json` | **which** documents exist — code, title, version, effective, clause, standard, state (245) |
| `/json/<CODE>.json` | **what one looks like** — fields and blocks; copy this to build the same kind of document (223) |
| `/html/<CODE>.html` | the same document, rendered |
| `/data/<dataset>.json` | the rows behind the documents — roster, skills, training, zones, tasks (14 sets) |
| `/consumers.json` | which apps read which documents — check before revising one |
| `/hr/index.html` | filled records |

**Code to URL: replace `/` with `_`.** `PM/FRM/5S-03` → `/json/PM_FRM_5S-03.json`.

**Watch the code form.** `register.json` writes `PM/FRM/5S-03`; the `doc_code`
*inside* the document JSON writes `PM_FRM_5S-03`. Matching one against the other
directly finds nothing. Normalise both before comparing.

22 registered codes have no JSON — pictograms and layout images produced another
way. `api.json` lists them by name, so a 404 there is expected, not broken. Use
`/html/` for those.

**Validate the register before you trust it — `count` is the one that matters.**

### Building a document of the same kind

Fetch a document of the type you want, keep the structure, replace the content.
`api.json` → `doc_types` names one example per type and lists its block types, so
you do not have to fetch 223 to find a pattern:

```
audit_checklist  emergency_plan  form  generic_register  inspection_checklist
quality_manual   sop             tracking_sheet          wi_matrix
```

Blocks are `fields`, `table`, `text`, `note`, `ticks`, `summary`, `signoff`.
Header keys are the same on every document: `doc_code`, `doc_title`, `version`,
`effective_date`, `iso_standard`, `iso_clause`, `owner`, `approver`.

---

## 3. Where PMCore reads from, and why

```
1. https://packmastersmumbai.github.io/pmdigitaliso/register.json   <- primary
2. register.json in Drive                                            <- fallback, marked `degraded`
3. the last copy that passed validation                              <- if both fail
```

**Why not Drive first.** The file lives in Drive, so Drive looks like the
obvious source. It was tried and measured, and it was **wrong**: on 2026-09-11
`DriveApp` served 241 documents published 06:52 while the site served 245
published 18:37 — about eighteen hours stale. The folder is kept in Drive by the
desktop sync client, and that client is not a reliable transport. Rewriting the
file in place and waiting did not move it, so this is not a timing window.

The site is a published artifact with a timestamp on it. Drive stays as the
fallback for the case where the site is unreachable, and anything served from it
is stamped `degraded` so a record never quietly cites an unverified registry.

**Not baked into PMCore's source.** An Apps Script library is version-pinned: an
app on v5 keeps running v5 until somebody bumps it. Data inside the library
would inherit that, and revising one document would become a code deployment
across every app.

> pin the code. never pin the data.

Read at call time, the newest registry reaches an app still pinned to an old
library version.

**Not a Sheet.** The JSON is already the artifact the ISO produces. A Sheet
means flattening it to columns and keeping a second copy in step — and a copy
that can fall out of step is the failure the whole arrangement exists to
prevent.

**No tokens.** The site copy is public and needs none. Everything else is in one
Google account, so a script running as that account already has the authority.

---

## 4. Validation — enforced on both sides

The same rules run when the registry is written and when it is read.

| Refused | Why |
|---|---|
| `count` ≠ number of documents | **a partial write** — valid JSON holding half a registry, which every other check passes |
| no documents | |
| duplicate codes | two answers to one lookup |
| missing code, title or version | not resolvable |
| any document in `draft` | a draft is not a controlled document; one reaching an app puts unapproved instructions in front of an operator |
| no `published_at` | cannot be dated |

**On write:** a registry that fails is not published. The file is written to a
temp path and moved into place, so a publish that fails halfway leaves the
previous registry intact rather than a truncated one that still parses.

**On read:** a registry that fails is not served. PMCore serves the last copy
that passed, marks it `degraded`, and `stamp()` appends *"(registry unverified
— …)"* to what your app prints. An app carrying on with the previous approved
versions is recoverable; one carrying on with half a registry reports documents
as missing that exist.

Tested against the live 245: healthy passes; truncated, empty, duplicate,
missing-version and draft-slipped-in are each refused.

---

## 5. How an update reaches you

```
document approved  ->  register.json rewritten (validated, atomic)
                   ->  git push       : GitHub Pages serves it, ~1 minute
                   ->  PMCore         : within its 5-minute cache
```

One command does all of it — `python scripts/release.py -m "..."` — and it
refuses to finish if the site is still serving the previous file, because a
publish that stops halfway leaves apps stamping a revision that was never
current.

`PMCore.health()` reports the state at any moment, including which source it
read from.

---

## 6. Live data, if you need more than the registry

`PMCore.fetch(dataset, period)` — `'2026-07'` or `'2026-01..2026-12'`.

```
roster  skills  training_topics  zones        state — no period
training  training_attendance                 events
housekeeping_5s  maintenance_kpi  clit        events
```

| Source | Sheet id |
|---|---|
| AQRS — attendance, training, HR | `19sZN-uUARWqQ3o8QKmwDtKhXtfiGCS1LC-g4Vnxfvwo` |
| 5S PM App | `1ogONmemeA_WPCqrWquQAZ7JU9tas0AK_Y5O9TI_9EFU` |
| MMT — maintenance | `1-3d_FmvwT_0fkdrJnO0Q0zfmy9rb6WrIdBQOrSRX2WM` |
| Taskflow DWM | `1a17AzXT60a5tYZFlxODHwA4ZCBT3QATrtrf1GcaGHI0` |
| Pack Masters QMS | `1qw-Ko6_-NTRVtC8joxAQrb7Izvef6mU2gr8W4X-tXCE` |

MMT's logs put their header on **row 3** under a bilingual title band. Reading
row 1 returns a banner and every column misses without erroring.

---

## 6b. Announce yourself

**Call `PMCore.announce(app, ISO_DOCS)` once a day** from a trigger you already
have. It never throws and nothing should wait on it.

Without it, whether your app is wired is a claim in a file. With it, the ISO can
see which apps are bound, which library version each runs, when each was last
seen, and **which documents each depends on** — so a revision is no longer made
blind to who reads it. An app that stops announcing does not vanish; it goes
stale, and silence is the signal.

Published at `/consumers.json` beside the registry.

---

## 7. The one rule

**An app owns its data and publishes it. Nothing writes another app's records.**

The ISO never edits a task. DWM never edits a controlled document. Cross-app
reads go through PMCore, which is the only holder of the sheet ids and logs
every call.

---

## 8. Where things are

```
scripts
  PMCore (library)   1XrbNFnQWob8l5GuSCUyMT5u0tUX7netkqidSYEgqXpBV3nxE7KQunp9v
  ISO data sync      1SSn9UeChCxEy9kta31kbik5bLjigUjJp4XEaB4kAX9xD_gnkG7sWmlup
  Cloud project      883421378799   (both must be attached to it)

project   C:\Users\Appex\My Drive (packmasters.mumbai@gmail.com)\Pack Masters Digital ISO\qms_app
  registry     _gh_tmp\register.json        <- the one registry
  documents    data\projects\pack-masters\generated\{json,html}\
  records      _hr_src\
  data layer   data\observed\<dataset>\<period>.json
               data\reference\*.json
  site (git)   _gh_tmp\      is the Pages repo, packmastersmumbai/pmdigitaliso
```

Everything above is inside the packmasters Drive, so every file already has a
Drive id — which is how PMCore reads them.

---

## 9. Not finished yet — do not build on these

* **PMCore is live as a library at version 1** and proven against the real
  245-document registry on 2026-09-11 — healthy read, `doc()`, `stamp()`,
  an unknown code returning null, the fallback to Drive marked `degraded`,
  the "(registry unverified)" suffix reaching the stamp, the last-good copy
  when neither transport answers, and recovery once the site returns.
  `gas_sync` is the first consumer. **No production app is wired to it yet.**
* **A prolonged outage can leave apps on a slightly older set.** The fallback
  serves the last registry that *passed validation*, which may be the Drive
  copy rather than the last healthy one. It is always marked `degraded`, so it
  is visible rather than silent — but it is not the current set.
* **`ISO_REGISTER`** still exists in the QMS sheet from the previous design. It
  is no longer read by anything and should be removed once PMCore is wired in.
* **`PM/FRM/HR-017` carries no effective date** in the registry. Validation does
  not require one; a stamp on that document will read "effective" and stop.
* **Taskflow records no completion** — `completed_at` is empty on all 474
  tasks, so any KPI built on task data is zero.
* **The employee master marks the Proprietor and the Plant In-charge INACTIVE.**
* **21 of 29 active people cannot be matched to a job description** — the master
  records them all as "Worker" while three job descriptions exist below
  in-charge level.

The last three are on `SYSREV/2026-09` in Actual data, with an owner each.
