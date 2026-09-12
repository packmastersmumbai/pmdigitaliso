# DWM ↔ Digital ISO — the contract

What Taskflow DWM must provide so that KRA, competence and KPI records build
themselves, and what the ISO gives back in return.

Written against the live data on 2026-09-10: 474 tasks, 10 users, 6 categories,
385 time-log rows.

---

## 0. The two facts that decide the design

**Category is unusable.** 464 of 474 tasks have no `category_id` — 98%. Any
mapping keyed on category would describe ten tasks and stay silent about the
rest. It is not a field to fix later; it is a field to stop relying on.

**`[dwm:N]` already works.** 428 of 474 tasks carry structured tags, with 53
distinct DWM item numbers, `[PDCA:D/C/A/P]` on 85, and a recurrence type on 90.
It is the convention the plant already uses, and it sits at the right level:
a DWM item is standard recurring work, so *"dwm:14 = Label Printing, daily,
120 min"* maps to a skill and a KRA once and stays true. A free-text task title
never does.

**So the mapping is keyed on the DWM item, not the category and not the text.**

---

## 1. What DWM must fix in what it already has

None of this is new structure — it is existing fields that do not yet carry
what they promise.

| Field | Today | Required |
|---|---|---|
| `completed_at` | **empty on all 474** | ISO 8601 timestamp, written when the task is completed. Never back-filled by a script. |
| `status` | todo 320, archived 98, in-progress 46, awaiting_check 4, done 2, deleted 4 | one settled vocabulary; `done` **must** carry `completed_at`, and nothing else may |
| `assignee_ids` | 346 set, but 2 rows hold the literal `[object` | JSON array of user ids. The `[object Object]` is a serialisation bug — fix at the write, not by cleaning the sheet |
| assignment | top assignee is **`Integration` (129 tasks)** — a system account | a task that counts toward a person's KRA must be assigned to a person |
| `category_id` | 98% empty | either populate it or retire it. Do not leave a field that looks meaningful and is not |

**Until `completed_at` is written, no KPI is real.** An engine run on today's
data returns zero for every person every month. Treating `archived` as done
would produce numbers, and none of them would be defensible in an audit. This
is the single blocking item.

---

## 2. New: `dwm_items` — the map itself, owned by DWM

One row per standard DWM item. 53 rows today. This is where the mapping lives,
so DWM stays the authority on its own work.

| Column | Type | Example | Notes |
|---|---|---|---|
| `dwm_no` | int | `14` | the N in `[dwm:14]`. Primary key |
| `title` | text | `Label Printing` | |
| `frequency` | enum | `daily` | daily / weekly / monthly / quarterly / once |
| `owner_role` | text | `ops` | a `roles.id` from DWM |
| `default_minutes` | int | `120` | the plan half of plan-versus-actual |
| `pdca` | enum | `D` | P / D / C / A |
| `skill_ids` | csv | `SKL-01,SKL-06` | **must exist** in AQRS `Skills` |
| `kra_ids` | csv | `KRA-278-03` | **must exist** in `KRA_REF` |
| `standard_ref` | text | `PM/WI/PRD-02` | **must exist** in `ISO_REGISTER` |
| `evidence` | enum | `experience` | `experience` or `none` — see §6 |
| `active` | bool | `TRUE` | |

A task inherits its item's skills and KRAs through `[dwm:N]`.

**Task-level override.** A tag in the description wins over the item default:

    [dwm:14] [PDCA:D] [Daily] [skill:SKL-03] [kra:KRA-278-01]

Explicit at source beats inferred downstream. Same bracket convention already
in use, so nothing new to learn.

**Unmapped is an exception, never a default.** A task with no `[dwm:N]` and no
override is listed by name in the monthly exception report and attributed to
nobody. A system that guesses quietly is worse than one that admits a gap: the
gap gets closed, a wrong number gets signed.

---

## 3. New: `user_map` — the identity bridge

Nothing works without this. DWM users are first names and initials (`Khushi`,
`Anuj`, `TBM`, `BBM`); AQRS employees are numbers (`687`, ANUJ PATHAK); the KRA
documents key on full names. Today a completed task cannot be attributed to a
person's KRA at all.

Ten rows. Maintained in DWM, validated by the ISO against the AQRS roster.

| Column | Example | Notes |
|---|---|---|
| `taskflow_user_id` | `023395f4-…` | `users.id` |
| `taskflow_name` | `Anuj` | as shown in DWM |
| `emp_id` | `687` | AQRS `Employees.EmpID` — the join |
| `is_person` | `TRUE` | `FALSE` for `Integration`, `Admin` — system accounts attribute to nobody |

The ISO refuses to publish a report if a `user_map` row names an `emp_id` that
is not ACTIVE on the roster. That check is how a leaver stops accruing KRA
performance.

---

## 4. What the ISO provides back

Reference data, read-only to every app, published by the ISO into a single
**`PM Reference`** spreadsheet that the ISO owns.

| Tab | Rows | Contents |
|---|---|---|
| `ISO_REGISTER` | 241 | code, title, version, effective, clause, state, url — already built |
| `SKILLS_REF` | 21 | skill id, name, group, min level, the topics that confer it |
| `KRA_REF` | *to build* | kra_id, emp_id, statement, measure, target, frequency, source document |
| `USER_MAP` | 10 | the bridge above, after validation |

So a DWM screen can show *"this task evidences SKL-01 Filling, against
KRA-278-03, under PM/WI/PRD-02 Rev 2.0"* — every part of that sentence traced
to a controlled source.

**`ISO_REGISTER` currently lives in the Pack Masters QMS sheet.** That was the
fastest route and it works, but it means the ISO writes into a sheet the QMS app
owns. Moving it to `PM Reference` removes the only cross-app write in the whole
design, and is worth doing before more apps depend on it.

**KRAs are not yet data.** They exist as ten rendered KRA documents — prose, not
rows. Nothing can be measured against a paragraph. Converting them to `KRA_REF`
is a one-time extraction, after which the documents render *from* the rows.

---

## 5. Access control, and writing between applications

**No tokens anywhere.** Every sheet belongs to one Google account, so a script
running as that account already has the authority. A token would be a secret to
leak in exchange for access that exists. The only thing a token would buy is
the ability for something *outside* the account to write — which is exactly what
should not be possible.

**One rule: an app owns its data and publishes it. Nothing writes another
app's records.**

```
        writes                     reads
DWM     tasks, time_log,           ISO_REGISTER, SKILLS_REF,
        dwm_items, user_map        KRA_REF          (reference, read-only)

ISO     PM Reference tabs,         tasks, time_log, dwm_items, user_map,
        its own records            5S, MMT, AQRS    (evidence, read-only)
```

The ISO never edits a task. DWM never edits a controlled document. The one
apparent exception — the ISO writing `ISO_REGISTER` — is the ISO writing its
own tab in its own sheet, which is why §4 moves it out of the QMS sheet.

**Enforcement is `PMCore`, not trust.** All cross-app access goes through the
shared library (`sources/PMCore.gs`): it holds the only copy of the sheet ids,
exposes `fetch` / `doc` / `stamp`, and writes `PMCORE_LOG` on every call. Once
it is deployed, direct `openById` calls come out of the individual apps. The
real risk in a one-account estate is that any app *could* write any sheet; the
protection is that access goes through one place and leaves a trace.

**Three roles, defined once in `PMCore`, not per app:**

| Role | May |
|---|---|
| record | write their own rows — any operator |
| review | read all, close findings — in-charges |
| approve | issue and revise controlled documents — MR and Proprietor |

The account is shared, so the identity that matters is the one the app collects
at sign-in. `PMCORE_LOG` is what turns that into evidence.

---

## 6. What the ISO then generates, monthly and silently

| Output | Built from |
|---|---|
| KRA performance per person | tasks done in the period → `user_map` → `dwm_items.kra_ids`, against `KRA_REF.target` |
| Plan versus actual effort | `estimated_minutes` (set on all 474) against `time_log` |
| Competence — experience | tasks done → `dwm_items.skill_ids`, as **experience**, never as training |
| KPI rollup for the MRM | the above, into `PM/PLN/MR-01` |
| Exception report | tasks with no `[dwm:N]`, unmapped items, system-account assignments, `user_map` rows failing validation |

**On competence, one distinction that must not blur.** Doing the work is not
attending training. But ISO 9001 clause 7.2 accepts *education, training **or
experience***, so task history is legitimate competence evidence — recorded in
its own column, never overwriting the training-derived result.

This matters more than it sounds. Today **0 of 406 requirements are Met**,
because 23 of 40 training topics have never been delivered. Experience evidence
can legitimately close part of that gap without anyone inventing a training
record.

---

## 7. Order of work

1. **DWM writes `completed_at`** and settles the status vocabulary. Everything
   downstream is zeros until this lands.
2. **`user_map`** — 10 rows. Nothing person-level works without it.
3. **`KRA_REF`** — extract the ten KRA documents into rows.
4. **`dwm_items`** — 53 rows, mapping each to skills, KRAs and a standard.
   Reviewed and approved as a controlled document, because it decides what
   counts as evidence.
5. **Attribution job** in the ISO — monthly, with the exception report.
6. **`PM Reference`** and **PMCore deployment** — the tidy-up that makes it
   maintainable rather than merely working.

Items 2, 3 and 5 can be built now; they do not depend on item 1, and they make
item 1 useful the day it lands.

---

## 8. The checks that keep it honest

Any of these failing stops the report rather than degrading it:

* a `skill_id` not in AQRS `Skills`
* a `kra_id` not in `KRA_REF`
* a `standard_ref` not in `ISO_REGISTER`, or pointing at a draft
* a `user_map` `emp_id` not ACTIVE on the roster
* a task with `status = done` and no `completed_at`
* a period with tasks but no `time_log` rows — plan without actual

A generated record must be traceable to the task ids behind it. If a figure
cannot be explained by naming rows, it does not go on a document that gets
signed.
