# KPIScope — Business Context for the Analyst Team

>

## 1. CEO Summary — What KPIScope Is, In Plain Business Terms

> *As if written/spoken by the CEO to the wider company.*

"Right now, every function in this business is answering the same question — 'are we growing or are we leaking?' — with a different spreadsheet. Sales has their own view of new logos. Customer Success has their own churn list. Finance reconciles MRR by hand at month-end. Nobody's numbers match, and by the time we spot a churn problem, it's already cost us a quarter.

KPIScope fixes that. It pulls every account, subscription, feature-usage log, support ticket, and churn event into **one governed source of truth** — cleaned and modeled once, in SQL Server, so there's no more 'whose number is right' debate. From that single foundation, we get two live views: a Python dashboard our data team can dig into freely, and a Power BI scorecard the leadership team reviews every week.

What I actually want to see on that scorecard: our **MRR and ARR trend**, whether we're **net-retaining revenue** (is expansion outpacing churn?), **which acquisition channel** is bringing in customers who actually stick around, **which plan tier** is both the most profitable and the most loyal, and whether **support load is quietly predicting churn** before it happens.

This isn't a reporting nice-to-have. It's how we catch a churn spike in week one instead of finding out in the board deck three months later."

---

## 2. Junior Analyst → Executive Dialogues

> Format: the junior analyst (JA) asking each stakeholder what they've struggled with historically and what they expect from KPIScope, grounded in the KPI dictionary and business questions from the technical spec.

### 2.1 With the CEO

**JA:** Before I start building, what's the one number you check first when you open any dashboard?

**CEO:** ARR trend, always. Everything else is context for that one line going up or down.

**JA:** And when it's *not* going up — what do you actually want the tool to tell you?

**CEO:** Whether it's a new-business problem or a retention problem. Right now I can't tell the difference fast, because Sales and CS report churn differently.

**JA:** So Net Revenue Retention — MRR minus churned MRR plus expansion MRR, over MRR — that's the number that separates those two stories for you?

**CEO:** Exactly. If NRR's healthy but ARR is flat, that's a top-of-funnel problem. If NRR is under 100%, that's a product or CS problem. I need that split visible at a glance, not buried in a filter.

---

### 2.2 With the CFO / Finance Lead

**JA:** What's been the biggest pain point in how MRR and ARR get reported today?

**CFO:** Every team rounds differently and no one flags mid-cycle plan changes properly, so my finance close never matches what Sales presented at the start of the month.

**JA:** The mart schema has an `expansion_flag` and `contraction_flag` built from a `LAG()` window function comparing MRR period over period per customer — would that solve the mid-cycle change problem?

**CFO:** Yes, if it's calculated identically in SQL, Python, *and* Power BI. I don't want three different expansion numbers depending on which tool someone opened.

**JA:** That's actually a hard rule in the build — cleaning and transformation only happen once, in SQL. Python and Power BI just read the finished `mart` schema and calculate off it independently, but from the same logic. We're also cross-reconciling five KPIs across all three at the end of the build specifically to catch that kind of drift.

**CFO:** Good. Then also make sure billing frequency — monthly vs. annual — doesn't distort the MRR trend line. Annual contracts front-load revenue in a way that can look like a spike if it's not normalized.

---

### 2.3 With the Head of Sales / RevOps

**JA:** What do you currently have no visibility into, that you want on this scorecard?

**Head of Sales:** Which acquisition channel is bringing in customers who actually stay. Right now I only track volume of new logos per channel, not what happens to them six months later.

**JA:** That lines up with one of the core business questions in the spec — "Which acquisition channel brings the most new customers, and which has the healthiest churn?" We'd join `dim_channel` against churn and retention on the fact table to answer both halves of that in one view.

**Head of Sales:** Perfect — and can I see it by plan tier too? I want to know if Enterprise deals from partner referrals outlast Basic deals from paid ads.

**JA:** Yes, that's the star schema doing its job — `dim_customer`, `dim_plan`, and `dim_channel` all key into the same fact table, so we can slice churn and retention by any combination of those without rebuilding anything.

---

### 2.4 With the Head of Customer Success

**JA:** What's your earliest warning sign today for an account that's about to churn, and how do you currently catch it?

**Head of CS:** Honestly, mostly gut feel and support ticket volume, checked manually. By the time it's official in our tracker, it's often too late to save the account.

**JA:** The spec calls that out directly — one of the five business questions is whether there's a relationship between support ticket load and churn. We won't claim causation, but we can surface the correlation: resolution time, escalation flags, and ticket volume plotted against churn events per account.

**Head of CS:** That would actually let me build an "at-risk" list instead of reacting after cancellation. Can it also show reactivations? We do win some accounts back.

**JA:** Yes — `is_reactivation` is a flag in the churn events data, about 10% of churned accounts come back. We can track that as its own retention story, separate from net-new churn.

---

### 2.5 With the Head of Support

**JA:** What would make support data actually useful to leadership, instead of just an internal ops metric?

**Head of Support:** Right now support looks like a cost center in every exec meeting. I want to show that fast resolution correlates with retention — that we're not just answering tickets, we're preventing churn.

**JA:** We can build that link directly — resolution time and satisfaction score against `is_churned_flag` for the same account, segmented by priority level. If low-satisfaction, slow-resolution accounts churn at a meaningfully higher rate, that's your business case in the data.

**Head of Support:** And urgent-priority tickets specifically — I want those isolated, because those are the accounts most likely to be evaluating whether to leave.

**JA:** Understood, we'll keep priority as a filterable dimension on every support-related visual, not just an average across all tickets.

---

## 3. Requirement Analysis — Summary Checklist

> Compiled by the analyst after the above conversations, before development starts.

### Business alignment
- [ ] Confirm the one-paragraph project summary is corrected to reflect the actual SaaS subscription/churn scope (not GL/payroll/EBITDA)
- [ ] Confirm ARR trend and NRR are the two headline metrics the CEO checks first
- [ ] Confirm NRR must be visibly split into its churn vs. expansion components, not shown as one blended number

### Finance requirements
- [ ] MRR/ARR calculated identically across SQL, Python, and Power BI — no per-tool rounding or logic drift
- [ ] Expansion and contraction MRR derived once in SQL via the `LAG()` window function, not recalculated downstream
- [ ] Billing frequency (monthly vs. annual) normalized so annual contracts don't distort the MRR trend line
- [ ] Five KPIs cross-reconciled across all three layers before sign-off (per Sprint 7 Definition of Done)

### Sales / RevOps requirements
- [ ] Churn and retention reportable by acquisition channel (`dim_channel`)
- [ ] Churn and retention reportable by plan tier (`dim_plan`)
- [ ] Support for combined slicing (e.g. channel × plan tier) without schema rework — validates the star schema design

### Customer Success requirements
- [ ] Support ticket load (volume, resolution time, escalation flag) correlated against churn, framed as correlation not causation
- [ ] Reactivation accounts (`is_reactivation`) tracked as a distinct retention signal, separate from net-new churn
- [ ] Groundwork laid for an "at-risk account" view usable before official churn is logged

### Support requirements
- [ ] Satisfaction score and resolution time linked to churn outcome per account
- [ ] Ticket priority kept as a filterable dimension, not averaged away
- [ ] Framing prepared to present support as a retention driver, not only a cost metric

### Data/architecture guardrails (non-negotiable per the technical spec)
- [ ] All cleaning and transformation logic lives only in SQL (`raw → staging → clean → mart`) — never duplicated in Python or DAX
- [ ] Python and Power BI both connect read-only, only to the finished `mart` schema
- [ ] Fact table grain explicitly documented before any KPI is built on top of it
- [ ] RavenStack dataset credited to River @ Rivalytics in any public write-up, per license terms



# Data Dictionary — KPIScope

## Status Note

Profiling below is built from the `.info()` output provided for **4 of the 5** files (`churn_events`, `feature_usage`, `subscriptions`, `support_tickets`). No `.info()` or `.head(10)` output was provided for **`account`**, and no `.head(10)` example rows were provided for any file. Those gaps are flagged inline — send the missing outputs and I'll fill them in.

---

## 1. `churn_events`

| Item | Value |
| --- | --- |
| Row count | 600 |
| Grain (what 1 row = ) | One churn event for one account, on one date |
| Primary key | `churn_event_id` |
| Join key(s) | `account_id` → `account.account_id` |

| Column | Dtype | Non-null |
| --- | --- | --- |
| churn_event_id | object | 600 |
| account_id | object | 600 |
| churn_date | object | 600 |
| reason_code | object | 600 |
| refund_amount_usd | float64 | 600 |
| preceding_upgrade_flag | bool | 600 |
| preceding_downgrade_flag | bool | 600 |
| is_reactivation | bool | 600 |
| feedback_text | object | 452 |

**Example row:** not provided — need `churn_events.head(1)`.

**Data quality issues:**

- `feedback_text` is missing on 148/600 rows (24.7%) — expected for optional free text, but worth noting for any sentiment/NLP KPI.
- `churn_date` is typed `object`, not `datetime` — will need parsing before any time-based analysis.
- No `mrr` or `subscription_id` column here, so churned *revenue* cannot be derived from this table alone — it must be joined to `subscriptions` via `account_id` (see §Cross-file notes).

**Suggested dtypes & transformations:**

| Column | Current | Suggested | Why |
| --- | --- | --- | --- |
| churn_date | object | `datetime64[ns]` | Needed for any trend/cohort/time-window analysis. `pd.to_datetime(df["churn_date"])`. |
| reason_code | object | `category` | Small, fixed set of values — saves memory and enables ordered grouping. |
| refund_amount_usd | float64 | keep `float64` | Already numeric; check for negative values (shouldn't exist for a refund) as a validation step. |
| feedback_text | object | keep `object`, add `has_feedback` (bool) | Derive `df["has_feedback"] = df["feedback_text"].notna()` so the missingness itself becomes a usable flag rather than a data-quality wart. |
| preceding_upgrade_flag / preceding_downgrade_flag / is_reactivation | bool | keep `bool` | Already correctly typed. |

Other transformations:

- Join to `subscriptions` on `account_id` to pull `mrr_amount` as of `churn_date`, so churn events carry a dollar value (needed for revenue-weighted churn analysis, not just event counts).
- Consider deriving `days_since_signup = churn_date − subscriptions.start_date` once joined — useful for early-churn vs. tenure-churn segmentation.

---

## 2. `feature_usage`

| Item | Value |
| --- | --- |
| Row count | 25,000 |
| Grain (what 1 row = ) | One feature's usage stats for one subscription, on one date |
| Primary key | `usage_id` |
| Join key(s) | `subscription_id` → `subscriptions.subscription_id` |

| Column | Dtype | Non-null |
| --- | --- | --- |
| usage_id | object | 25,000 |
| subscription_id | object | 25,000 |
| usage_date | object | 25,000 |
| feature_name | object | 25,000 |
| usage_count | int64 | 25,000 |
| usage_duration_secs | int64 | 25,000 |
| error_count | int64 | 25,000 |
| is_beta_feature | bool | 25,000 |

**Example row:** not provided — need `feature_usage.head(1)`.

**Data quality issues:**

- No nulls — clean on completeness.
- `usage_date` is `object`, needs datetime conversion.
- Worth checking for duplicate `usage_id` and for multiple rows per (`subscription_id`, `feature_name`, `usage_date`) — can't confirm without the actual data, only counts.
- This table links to `account`/`churn_events` only indirectly, through `subscriptions.account_id` — there is no direct `account_id` column here.

**Suggested dtypes & transformations:**

| Column | Current | Suggested | Why |
| --- | --- | --- | --- |
| usage_date | object | `datetime64[ns]` | Required for any usage-trend or "usage in the N days before churn" KPI. |
| feature_name | object | `category` | Fixed, repeating set of feature names — much cheaper across 25,000 rows and enables clean groupby ordering. |
| usage_count / usage_duration_secs / error_count | int64 | keep `int64`, check for negatives | Negative durations/counts would indicate a data issue; worth a `.describe()` sanity pass once loaded. |
| is_beta_feature | bool | keep `bool` | Already correct. |

Other transformations:

- Derive `error_rate = error_count / usage_count` (guard divide-by-zero) — much more useful for a product-health KPI than raw error counts.
- Aggregate to `subscription_id` level (`sum`/`mean` per subscription, per date range) before joining to `subscriptions` — this table is at usage-event grain, not subscription grain, so it needs a groupby before it can sit next to MRR/churn data in the same row.
- If the intent is "engagement leading up to churn," derive a rolling 30-day usage window per subscription rather than joining raw rows — otherwise a churned account with years of history will dominate any naive join.

---

## 3. `subscriptions`

| Item | Value |
| --- | --- |
| Row count | 5,000 |
| Grain (what 1 row = ) | One subscription (one account may have more than one subscription over time) |
| Primary key | `subscription_id` |
| Join key(s) | `account_id` → `account.account_id`; `subscription_id` → `feature_usage.subscription_id` |

| Column | Dtype | Non-null |
| --- | --- | --- |
| subscription_id | object | 5,000 |
| account_id | object | 5,000 |
| start_date | object | 5,000 |
| end_date | object | 486 |
| plan_tier | object | 5,000 |
| seats | int64 | 5,000 |
| mrr_amount | int64 | 5,000 |
| arr_amount | int64 | 5,000 |
| is_trial | bool | 5,000 |
| upgrade_flag | bool | 5,000 |
| downgrade_flag | bool | 5,000 |
| churn_flag | bool | 5,000 |
| billing_frequency | object | 5,000 |
| auto_renew_flag | bool | 5,000 |

**Example row:** not provided — need `subscriptions.head(1)`.

**Data quality issues:**

- `end_date` non-null on only 486/5,000 rows — this is expected (only closed/churned subscriptions should have an end date), but worth confirming `end_date` is null for every row where `churn_flag == False`, and non-null everywhere `churn_flag == True`, as a consistency check.
- `start_date`/`end_date` are `object`, need datetime conversion.
- No `channel` column — see KPI feasibility note below.
- No `expansion_flag` / `contraction_flag` columns — only `upgrade_flag` / `downgrade_flag`, which is a related but not identical concept (see KPI feasibility).

**Suggested dtypes & transformations:**

| Column | Current | Suggested | Why |
| --- | --- | --- | --- |
| start_date / end_date | object | `datetime64[ns]` | Core to tenure, cohorting, and any "active as of date X" logic. |
| plan_tier | object | `category` | Small fixed set (e.g. Free/Pro/Enterprise) — cheaper and orderable. |
| billing_frequency | object | `category` | Same reasoning — likely Monthly/Annual only. |
| seats | int64 | keep `int64` | Fine as-is. |
| mrr_amount / arr_amount | int64 | consider `float64` if any prorated/partial values are expected | Currently whole-dollar ints; keep int if genuinely always whole dollars, otherwise switch before any per-seat or prorated calc introduces rounding loss. |
| is_trial / upgrade_flag / downgrade_flag / churn_flag / auto_renew_flag | bool | keep `bool` | Already correct. |

Other transformations:

- Derive `is_active = end_date.isna()` — an explicit boolean is easier to filter on than checking for nulls every time, and doubles as a cross-check against `churn_flag`.
- Derive `tenure_days = (end_date.fillna(today) − start_date).dt.days` for tenure-based cohort or survival analysis.
- If `arr_amount` doesn't cleanly equal `mrr_amount × 12` once real data is loaded, add a `arr_variance = arr_amount − (mrr_amount * 12)` column to quantify and explain the gap (e.g. mid-cycle upgrades, discounts) rather than silently picking one as "the" ARR.

---

## 4. `support_tickets`

| Item | Value |
| --- | --- |
| Row count | 2,000 |
| Grain (what 1 row = ) | One support ticket for one account |
| Primary key | `ticket_id` |
| Join key(s) | `account_id` → `account.account_id` |

| Column | Dtype | Non-null |
| --- | --- | --- |
| ticket_id | object | 2,000 |
| account_id | object | 2,000 |
| submitted_at | object | 2,000 |
| closed_at | object | 2,000 |
| resolution_time_hours | float64 | 2,000 |
| priority | object | 2,000 |
| first_response_time_minutes | int64 | 2,000 |
| satisfaction_score | float64 | 1,175 |
| escalation_flag | bool | 2,000 |

**Example row:** not provided — need `support_tickets.head(1)`.

**Data quality issues:**

- `satisfaction_score` missing on 825/2,000 rows (41.25%) — large gap, will bias any CSAT-style KPI if not handled (e.g. exclude nulls rather than treat as 0).
- `submitted_at`/`closed_at` are `object`, need datetime conversion.
- `resolution_time_hours` is already pre-computed — worth spot-checking it actually equals `closed_at − submitted_at` once real values are visible.

**Suggested dtypes & transformations:**

| Column | Current | Suggested | Why |
| --- | --- | --- | --- |
| submitted_at / closed_at | object | `datetime64[ns]` | Needed to validate `resolution_time_hours` and for any ticket-volume-over-time KPI. |
| priority | object | ordered `category` (e.g. Low \< Medium \< High \< Urgent) | Enables correct sorting/comparison instead of alphabetical. |
| resolution_time_hours / first_response_time_minutes | float64 / int64 | keep, but standardize units | Two different time units across two columns (hours vs. minutes) — convert one so KPIs comparing them don't silently mix units. |
| satisfaction_score | float64 | keep `float64`, add `has_csat` (bool) | Same pattern as `feedback_text` above — `df["has_csat"] = df["satisfaction_score"].notna()`, so the 41% non-response rate is trackable as its own metric rather than just dropped. |
| escalation_flag | bool | keep `bool` | Already correct. |

Other transformations:

- Derive `resolution_time_days = resolution_time_hours / 24` if the KPI spec's "days" wording (see §8) is taken literally.
- When computing `Avg. Resolution Time`, exclude tickets with `closed_at` null (if any exist once real data loads) rather than letting them silently produce `NaN` durations.
- For CSAT-based KPIs, always compute over `satisfaction_score.notna()` only — averaging with nulls-as-zero would understate satisfaction by \~41%.

---

## 5. `account`

**Not yet profiled — `.info()` output was not provided for this table.**

Needed to complete this section:

- `account.info()`
- `account.head(10)`

This table is expected to be the hub that `churn_events`, `subscriptions`, and `support_tickets` all join to via `account_id`. Until it's profiled, two things are unconfirmed:

1. Whether `account_id` is actually the primary key here (i.e., one row per account, no duplicates).
2. Whether a **channel** (acquisition channel), industry, or segment field exists — this directly determines whether "by Channel" KPIs (§8) are measurable at all.

---

## Cross-File Join Map

```
account (account_id) ──┬── subscriptions (account_id → subscription_id)
                        │         └── feature_usage (subscription_id)
                        ├── churn_events (account_id)
                        └── support_tickets (account_id)
```

- `account` is the hub table (pending profiling).
- `subscriptions` is the only path from `account` to `feature_usage` — there's no direct `account_id` on `feature_usage`.
- Revenue-related KPIs (MRR, ARR, expansion, contraction) live entirely in `subscriptions`.
- Churn *event* detail (reason, refund, feedback) lives in `churn_events`; churn *flag* at the subscription level lives in `subscriptions.churn_flag`. These should tell the same story per account — worth reconciling once real data is loaded (e.g., does every `churn_flag == True` subscription have a matching `churn_events` row?).

---

## Duplicate-Key Check (pending)

Row counts and non-null counts don't reveal duplicate keys — that requires checking actual values (`.duplicated()` on each primary key). Flagging as a to-do once the files are loaded:

- [ ] `churn_events.churn_event_id` unique?
- [ ] `feature_usage.usage_id` unique?
- [ ] `subscriptions.subscription_id` unique?
- [ ] `support_tickets.ticket_id` unique?
- [ ] `account.account_id` unique? (pending profiling)

---

## Initial KPI List — Feasibility Against Current Columns

| KPI | Logic (from spec) | Measurable now? | Notes |
| --- | --- | --- | --- |
| Total MRR | Sum of `mrr` | ✅ Yes | Column is `mrr_amount` in `subscriptions`, not `mrr` — naming needs to match the actual schema. |
| Total ARR | Total MRR × 12 | ⚠️ Partial | `subscriptions.arr_amount` already exists as its own column — need to confirm whether it equals `mrr_amount × 12` or is independently derived (e.g. accounts for billing frequency/discounts). Don't assume; check both. |
| Churn Rate | Churned ÷ Total customers | ✅ Yes | `subscriptions.churn_flag` gives churned subscriptions; need `account`-level distinct count for "total customers" (pending `account` profiling to confirm grain). |
| Net Revenue Retention | (MRR − Churned MRR + Expansion MRR) ÷ MRR | ❌ Blocked | Requires Expansion MRR and Contraction MRR (see below), which aren't directly measurable yet. |
| Expansion MRR | Sum of MRR where `expansion_flag = 1` | ❌ Not measurable as specified | No `expansion_flag` column exists. Closest proxy is `subscriptions.upgrade_flag`, but that's a boolean flag on the current row, not a *delta in MRR* — you'd need either (a) a history/snapshot table showing MRR before and after upgrade, or (b) to treat `upgrade_flag = True` rows as expansion events and compute delta some other way. Flag for the client/stakeholder: is there an MRR-change or subscription-history table we're missing? |
| Contraction MRR | Sum of MRR where `contraction_flag = 1` | ❌ Not measurable as specified | Same issue as Expansion MRR — only `downgrade_flag` exists, no MRR delta. |
| New Customers by Channel | Distinct customers grouped by channel | ❌ Blocked | No `channel` column in any profiled table. Depends entirely on what `account` contains — this is the single biggest open question in the whole KPI list. |
| Churn Rate by Channel | Churn rate grouped by channel | ❌ Blocked | Same blocker — needs `channel` on `account`. |
| Avg. Resolution Time | Avg days between ticket opened/resolved | ✅ Yes, with a units correction | `support_tickets.resolution_time_hours` already exists — the spec says "days" but the column is in hours. Either divide by 24 or just report the KPI in hours and rename it for clarity. |

### Summary: what can / can't be measured right now

**Measurable as-is (once dtypes are fixed):**

- Total MRR, Churn Rate (subscription-level), Avg. Resolution Time

**Measurable but needs a definition decision:**

- Total ARR (confirm `arr_amount` vs. `mrr_amount × 12`)

**Blocked — missing data:**

- Expansion MRR / Contraction MRR / Net Revenue Retention — need either an MRR history table or a defined way to compute MRR delta from a single snapshot per subscription
- New Customers by Channel / Churn Rate by Channel — need a `channel` field, most likely expected to live in `account` (unprofiled)

**Action items to unblock:**

1. Send `account.info()` and `.head(10)` — resolves the channel question and confirms account is the true customer grain.
2. Send `.head(10)` for the other 4 tables — needed for the "example row" column in this dictionary and to sanity-check join key formats (e.g. do `account_id` values match format/casing across tables?).
3. Confirm with the KPI spec's owner whether there's a subscription *history* or *change log* table intended to exist for Expansion/Contraction MRR — as given, the current schema can't support those two KPIs or NRR.

---

## Alternative Measures for Blocked KPIs

These approximate the *intent* of the spec's KPI using only the columns that actually exist. They are not substitutes for the real thing — each one is flagged with what it can't capture — but they let the dashboard/report ship something directional instead of a blank tile while the real fields are sourced.

### Expansion MRR / Contraction MRR (intent: revenue gained/lost from existing customers upgrading/downgrading)

**What's missing:** an MRR *delta* per change event. `upgrade_flag`/`downgrade_flag` are static booleans on the current subscription row — they say a change happened at some point, not what the MRR was before vs. after.

**Alternative 1 — Event-count proxy (weakest, but zero new data needed):**

```python
expansion_events = subscriptions[subscriptions["upgrade_flag"]].shape[0]
contraction_events = subscriptions[subscriptions["downgrade_flag"]].shape[0]
```

Reports "number of upgrades/downgrades," not dollars. Useful as a leading indicator, not a revenue KPI — label it clearly as a count, not an MRR figure, so it isn't mistaken for the real thing.

**Alternative 2 — Current-MRR-weighted proxy (better, still an approximation):**

```python
expansion_mrr_proxy = subscriptions.loc[subscriptions["upgrade_flag"], "mrr_amount"].sum()
contraction_mrr_proxy = subscriptions.loc[subscriptions["downgrade_flag"], "mrr_amount"].sum()
```

Treats the *current* MRR of upgraded/downgraded subscriptions as a stand-in for the *change* in MRR. Overstates expansion (counts the whole plan, not just the increase) and is directionally wrong for contraction (counts what's left, not what was lost). Only use this as a rough "which segment/tier is most affected" cut, not a headline number.

**Real fix:** ask whether a `plan_tier_history` or `mrr_change_log` table exists (with `subscription_id`, `change_date`, `mrr_before`, `mrr_after`). If Track B's Power BI model is meant to compute this properly, this table is a prerequisite, not optional.

### Net Revenue Retention

**What's missing:** it's a direct function of Expansion MRR and Contraction MRR above, so it inherits the same blocker.

**Alternative — approximate NRR using the proxies:**

```python
starting_mrr = subscriptions["mrr_amount"].sum()  # as of period start — needs a snapshot date filter
churned_mrr = subscriptions.loc[subscriptions["churn_flag"], "mrr_amount"].sum()
nrr_proxy = (starting_mrr - churned_mrr + expansion_mrr_proxy) / starting_mrr
```

This inherits Alternative 2's overstatement problem and also needs a true point-in-time snapshot of "starting MRR" (the current table is a snapshot of *now*, not of a defined period start) — so period-over-period NRR isn't really available without a dated MRR snapshot. Label any output from this as directional/estimated, not a reportable NRR figure, until a proper history table exists.

### New Customers by Channel / Churn Rate by Channel

**What's missing:** no `channel` column has been confirmed anywhere. This depends entirely on the unprofiled `account` table.

**Alternative 1 — if `account` turns out to have no channel field either:** Drop the "by Channel" cut entirely and substitute a dimension that *does* exist, e.g.:

```python
# Churn rate by plan tier instead of by channel
churn_by_tier = subscriptions.groupby("plan_tier")["churn_flag"].mean()
```

`plan_tier` and `billing_frequency` are both confirmed columns and can stand in as the segmentation axis until/unless `channel` is sourced.

**Alternative 2 — if `account` has a related-but-not-identical field** (e.g. `signup_source`, `referrer`, `industry`): Use that as `channel`'s substitute and rename the KPI to match what's actually in the data (e.g. "Churn Rate by Signup Source") rather than forcing the original label onto a different field.

**Real fix:** this is the single highest-priority item to resolve — send `account.info()` before finalizing which KPIs Track A/Track B will actually build, since the whole "by Channel" row of the KPI dictionary depends on it.