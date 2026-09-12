# Connecting the apps to the Digital ISO — both directions

## What is actually true today

I checked every `.clasp.json` and `appsscript.json` on this machine rather than
taking the arrangement on trust, and one premise needs correcting before
anything is built on it:

**The apps do not share a Cloud project or a token.** No `.clasp.json` declares
a `projectId`, so each of the ten scripts runs on its own auto-created default
Cloud project, with its own OAuth consent, its own quota and its own logs.
Scopes differ nine ways. Consolidating is work to do — not a state to rely on.

Full inventory: `system_map.json`. The other things it turned up:

* the QMS script has two working copies on disk (`PM QMS/` and `qms_app/gas/`)
  on one scriptId — whichever is pushed last wins, silently
* the 5S system has two *different* script projects, so a fix applied to one
  does nothing to the other
* `qms_app/apps-script/` holds an `appsscript.json` and no code: pull before
  touching it or the push will empty the project
* two apps hold `script.projects` and `script.deployments` — scopes that let
  them rewrite other scripts

## The mechanism: no tokens at all

The instinct is an API key or a token per app. Do not. Every app and every
sheet belongs to **one Google account**, and a script running as that account
opens any of them with `SpreadsheetApp.openById`. A token would add a secret to
leak, rotate and store, in exchange for access that already exists.

Tokens are only needed to cross an account boundary. Nothing here crosses one.

    ┌──────────────── one Google account, one Cloud project ────────────────┐
    │                                                                       │
    │   5S app ──┐                                    ┌── ISO registry      │
    │   MMT   ───┼──►  PMCore (shared library)  ◄─────┤   (doc code, ver,   │
    │   AQRS  ───┤     read / write / audit          │    clause, status)   │
    │   Taskflow ┘                                    └─────────┬───────────┘
    │                          │                                │           │
    └──────────────────────────┼────────────────────────────────┼───────────┘
                               ▼                                ▼
                 data/observed/<dataset>/<YYYY-MM>.json    a form in the 5S app
                 (synced Drive folder, read by Python)     cites the CURRENT
                                                           version of PM/FRM/5S-01

## Both directions, and what each is for

**Apps → ISO (evidence).** The app publishes what it recorded in a period; the
ISO renders the record. Already built: `qms_data_sync.gs`, `fetch_period_data`,
`build_period_matrix`.

**ISO → apps (control).** This is the half that makes the ISO worth keeping.
The app asks the ISO for the current controlled document before it renders a
form, so the checklist on a phone in the plant is the issued version, and a
revision reaches the shop floor by being approved rather than by someone
remembering to update a script. The app displays the code and version it used
and writes them onto the record — which is what makes the record auditable.

That direction needs the ISO registry readable from Apps Script, so the
registry moves into a sheet the scripts can open (`knowledge_graph.json` stays
the build-time source; the sheet is its published form).

## The pieces to build, in order

1. **One Cloud project.** Create `packmasters-apps`. In each script: Project
   Settings → Google Cloud Platform project → change to its number. Add
   `"projectId"` to each `.clasp.json` so it is recorded rather than
   remembered. One consent screen, one quota, one log to search.

2. **`PMCore`, a shared library — not copied code.** One script project,
   deployed as a library, added to every app's `appsscript.json` dependencies.
   It holds the only copy of:
   * the registry of sheet ids (no app hardcodes another app's id again)
   * `readDataset(name, period)` / `writeSnapshot(name, period, rows)`
   * `currentDoc(code)` → `{code, version, effective, clause, url}`
   * `logAccess(app, action, target)` — one audit trail across all apps
   A change to a sheet id is then one edit, not ten.

3. **Least scope, per app.** Drop `script.projects` and `script.deployments`
   from 5S and Taskflow — an app that records audits has no business rewriting
   scripts. Prefer `drive.file` over full `drive` wherever the app only touches
   files it made.

4. **Deduplicate first.** Reconcile `PM QMS/` against `qms_app/gas/` and keep
   one; decide which 5S project is live and delete the fork; pull the bound
   script's code before pushing anything to it. Consolidating auth on top of
   duplicated source just makes both copies authoritative.

5. **Then the schema.** With `PMCore` in place, each dataset is a named
   contract in `registry.json` — fields, grain, and which documents it feeds —
   and `describeSources()` proves the source still matches it.

## Access

Three roles, enforced in `PMCore` rather than per app: **record** (any operator
— write their own rows), **review** (in-charges — read all, close findings),
**approve** (MR and Proprietor — issue and revise documents). The account is
shared, so the identity that matters is the one the app collects at sign-in;
`logAccess` is what makes it evidence.

## The one real risk

Every app running as one account means any app can write any sheet. The
protection is not a token — it is that `PMCore` is the only writer, and it logs.
Keep direct `openById` calls out of the individual apps once the library exists.
