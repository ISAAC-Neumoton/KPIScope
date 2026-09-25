# KPIScope

A project that pulls a company's customer/subscription/support data into one place, so a data team can dig into it in Python and leadership can check a Power BI scorecard every week — both looking at the exact same numbers.

This README explains **what problem this solves** and **what all the business terms mean**, written for someone with little business background. If a word feels obvious to you already, skip it — this is meant to be a lookup, not a lecture.

---

## 1. What problem is this actually solving?

Picture a company where:

- The Sales team has their own spreadsheet of "new customers this month."
- The Customer Success team has their own list of "customers we lost."
- Finance manually adds up subscription revenue by hand at the end of each month.

None of these three numbers agree with each other, because each team built their own version from their own partial data. Nobody can say for sure "how much money are we making" or "are we gaining or losing customers faster" — and by the time someone finally notices a problem (like a wave of customers cancelling), months have already gone by.

**KPIScope's fix:** combine every relevant piece of data — accounts, subscriptions, feature usage, support tickets, churn events — into one clean, single source, so every team is reading from the same numbers instead of five different spreadsheets that disagree.

---

## 2. Business jargon, explained

### MRR — Monthly Recurring Revenue

The amount of money the company earns *every month* from subscriptions. If a customer pays $100/month, they contribute $100 to MRR. This is the core "how much money is coming in right now, on a recurring basis" number.

### ARR — Annual Recurring Revenue

The same idea as MRR, just scaled up to a yearly view. Usually just `MRR × 12`. Companies use ARR when talking about big-picture, year-level revenue instead of month-to-month.

### Churn / Churn Rate

"Churn" = a customer cancels or leaves. "Churn rate" = what percentage of customers left in a given period. If you had 100 customers and 5 cancelled this month, that's a 5% churn rate. High churn = the business is leaking customers.

### Expansion (MRR)

When an *existing* customer pays the company **more** money than before — e.g., they upgrade to a bigger plan, add more seats/users, or buy an add-on. This grows revenue without needing a single new customer.

### Contraction (MRR)

The opposite of expansion — an existing customer downgrades or removes something, so the company earns **less** from them than before (but they haven't fully cancelled yet).

### Net Revenue Retention (NRR)

A single number that answers: "If we got zero new customers this year, would our revenue from existing customers alone have grown or shrunk?" It's calculated as:

```
(Starting MRR − Revenue lost to churn + Revenue gained from expansion) ÷ Starting MRR
```

- **Above 100%** = existing customers are spending *more* over time, even accounting for the ones who left. This is considered a very healthy sign for a subscription business.
- **Below 100%** = the business is shrinking from within, even if it's still adding new customers on top.

### Acquisition Channel / Referral Source

*How* a customer found and joined the company — e.g., organic, paid ads, an event, a partner referral, etc. Businesses track this to figure out which channel brings in customers who actually stick around, versus ones who sign up once and leave quickly. In our actual data (see §6) this column is named `referral_source`.

### Plan Tier

The subscription "level" a customer is on — Basic, Pro, or Enterprise in our dataset. Usually tied directly to price and feature access.

### Seats

How many individual users a company's account is paying for (like "we bought 20 seats" for 20 employees to use the product).

### CSAT / Satisfaction Score

A rating a customer gives after a support interaction — 1–5 in our dataset — showing how happy they were with the help they got. About 41% of tickets in our data have no score at all (customer didn't respond) — see §6's data quality notes.

### SLA-style metrics (Resolution Time, First Response Time)

How long it took a support ticket to get a first reply, and how long it took to fully resolve. Slow support is often an early warning sign that a customer might leave.

### Escalation

When a support ticket gets kicked up to a more senior or specialized team because the first person couldn't resolve it — usually a sign of a more serious or frustrating issue.

---

## 3. Data/technical jargon, explained

### Table / Row / Column

Think of each data file (accounts, subscriptions, etc.) as a spreadsheet. A **row** is one single record (e.g., one subscription). A **column** is one type of information about every record (e.g., "start date").

### Grain

"What does one row actually represent?" For example, in the `subscriptions` table, one row = one subscription line item, and — this is a real finding from profiling our actual data, not a guess — **one account can have many concurrent subscription rows at once** (we found accounts with up to 16 rows). They are *not* a time-ordered history of one subscription changing over time; they behave more like separate product lines or add-ons under the same account. Getting the grain wrong here is exactly the kind of mistake that silently breaks a KPI — see the Expansion/Contraction MRR note in Sprint 4 (§13) for what this actually changes.

### Primary Key

The column that makes every row in a table unique — like an ID number. No two rows should ever share the same primary key.

### Join / Join Key

"Joining" means connecting two tables together using a shared column, so you can pull information from both at once. In our dataset, every table connects back to `account_id`, either directly or (for `feature_usage`) through `subscription_id`.

### dtype (Data Type)

What *kind* of value a column holds — a number, text, a date, true/false, etc. In our profiling, every date column (`signup_date`, `start_date`, `churn_date`, `submitted_at`, etc.) came in as plain text and needs converting before it can be used for any date math — that's what "transformations" refers to in Sprint 3/4 below.

### Null / Missing Value

An empty cell — no data recorded for that row/column. Two real examples from our data: `feedback_text` in `churn_events` is missing on \~25% of rows, and `satisfaction_score` in `support_tickets` is missing on \~41% of rows. Both are expected (optional fields), not broken data — but any KPI built on them needs to explicitly exclude the nulls rather than treat them as zero.

### Flag

A column that's just `True`/`False` (yes/no) — e.g., `churn_flag = True` means "this account/subscription has churned."

### Proxy

A stand-in measurement used when the *exact* thing you want to measure isn't directly available in the data, but something closely related is. Proxies are useful but imperfect — they should always be labeled as estimates, not treated as the real number. Expansion MRR and Contraction MRR (see Sprint 4, §13) are the clearest example of this in KPIScope.

---

## 4. Git terms that came up (quick glossary)

- **Commit** — saving a snapshot of your changes locally.
- **Push** — sending your saved commits up to GitHub.
- **Pull** — downloading commits from GitHub that you don't have locally yet.
- **Rejected (non-fast-forward)** — GitHub has commits you don't have locally (e.g., someone/something changed the repo since you last synced), so it won't accept your push until you pull first.
- **Rebase** — a way of pulling in GitHub's changes and replaying your own commits on top of them, keeping history clean.
- **Detached HEAD** — you're "floating" outside of any real branch; any commits made here can get lost if not merged back onto a branch.
- **.gitignore** — a file that tells Git "never track these files" (used here to keep local cache/notebook junk files out of the repo).

---

**Architecture:** One shared SQL Server pipeline (injection → cleaning → transformation → modeling) feeding TWO independent, parallel visualization tracks — Python and Power BI — both connecting read-only to the same finished tables and doing ONLY calculations + visuals.

**Methodology:** Agile (sprints, backlog, Definition of Done, sprint review)

---

## 5. Architecture

```mermaid
flowchart TD
    subgraph SQL["SQL Server — single source of truth"]
        direction TB
        R[raw schema<br/>data injection] --> S[staging schema<br/>cleaning]
        S --> C[clean schema<br/>transformation]
        C --> M[mart schema — star<br/>modeling]
    end

    M -->|read-only connection| PY
    M -->|read-only connection| PBI

    subgraph PY["Track A — Python"]
        direction TB
        PY1[pyodbc / sqlalchemy]
        PY2[pandas calculations]
        PY3[plotly / matplotlib]
        PY4[Streamlit dashboard]
        PY1 --> PY2 --> PY3 --> PY4
    end

    subgraph PBI["Track B — Power BI"]
        direction TB
        PB1[Import / DirectQuery]
        PB2[DAX calculations]
        PB3[Report visuals]
        PB4[Published .pbix]
        PB1 --> PB2 --> PB3 --> PB4
    end
```

**Rule:** Injection, cleaning, transformation, and modeling happen **once**, entirely in SQL Server/SSMS. Python and Power BI never touch raw data — they only read from the finished `mart` schema and are each responsible for their own calculations and visuals, independently.

---

## 6. The Dataset — RavenStack

Everything downstream (schemas, SQL, Python, DAX) has to match this exactly — this section is the ground truth the rest of the document was corrected against.

**Dataset:** RavenStack: Synthetic SaaS Dataset (Multi-Table) **Author:** River @ Rivalytics **Credit Requirement:** This dataset may be used or remixed for educational/portfolio purposes, but **must credit the original author — River @ Rivalytics** — in any public write-up, repo, or portfolio post. **License:** MIT-like (fully synthetic, no PII) **Refresh Interval:** Monthly **Complexity:** Capstone-level (multi-table, event-driven, time-sensitive)

**Scenario:** RavenStack is a stealth-mode SaaS startup delivering AI-driven team tools, secretly piloted with coding bootcamp graduates. Every sign-up, feature use, support ticket, and churn event was captured, with the goal of discovering what drove conversions, support load, and churn before public launch.

**How it was generated:**

- Scripted in Python using `pandas`, `numpy`, and `uuid`
- Temporal logic validated (e.g. signup ≤ subscription ≤ churn dates)
- Statistical realism via exponential and Poisson distributions for seats, usage, and durations
- Primary/foreign keys fully linked — no orphaned records
- Deliberate edge cases included: mid-cycle plan changes, null fields, reactivations, duplicate referrals, beta feature spikes
- Deliberate nulls included: satisfaction scores, feature usage, churn feedback

**Row volumes:**

| Table | Rows |
| --- | --- |
| accounts | 500 |
| subscriptions | 5,000 |
| feature_usage | 25,000 |
| support_tickets | 2,000 |
| churn_events | 600 |

**Table relationships:**

```mermaid
erDiagram
    ACCOUNTS ||--o{ SUBSCRIPTIONS : "account_id"
    SUBSCRIPTIONS ||--o{ FEATURE_USAGE : "subscription_id"
    ACCOUNTS ||--o{ SUPPORT_TICKETS : "account_id"
    ACCOUNTS ||--o{ CHURN_EVENTS : "account_id"

    ACCOUNTS {
        string account_id PK
    }
    SUBSCRIPTIONS {
        string subscription_id PK
        string account_id FK
    }
    FEATURE_USAGE {
        string usage_id PK
        string subscription_id FK
    }
    SUPPORT_TICKETS {
        string ticket_id PK
        string account_id FK
    }
    CHURN_EVENTS {
        string churn_event_id PK
        string account_id FK
    }
```

**Full column reference:**

*accounts.csv* — account_id (PK), account_name, industry, country (ISO-2), signup_date, referral_source (organic/ads/event/partner/other), plan_tier (Basic/Pro/Enterprise), seats, is_trial, churn_flag

*subscriptions.csv* — subscription_id (PK), account_id (FK), start_date, end_date (nullable), plan_tier, seats, mrr_amount, arr_amount, is_trial, upgrade_flag, downgrade_flag, churn_flag, billing_frequency (monthly/annual), auto_renew_flag (\~80% true)

*feature_usage.csv* — usage_id (PK), subscription_id (FK), usage_date, feature_name (pool of 40 features), usage_count, usage_duration_secs, error_count, is_beta_feature (\~10% flagged)

*support_tickets.csv* — ticket_id (PK), account_id (FK), submitted_at, closed_at, resolution_time_hours, priority (low/medium/high/urgent), first_response_time_minutes, satisfaction_score (1–5, null = no response), escalation_flag

*churn_events.csv* — churn_event_id (PK), account_id (FK), churn_date, reason_code (pricing/support/features/etc.), refund_amount_usd ($0 default, \~25% have credit/refund), preceding_upgrade_flag (upgrade within 90 days), preceding_downgrade_flag (downgrade within 90 days), is_reactivation (\~10% previously churned), feedback_text (optional)

**Suggested project angles (from source docs):** churn prediction using subscriptions + support data, feature adoption tracking during beta phases, support workload forecasting, revenue cohort analysis by referral channel, plan tier upgrade funnel by industry, latency analysis by seat count and plan tier.

> **Confirmed during our own Sprint 0 profiling (not just the source docs):** `subscriptions` rows per `account_id` are concurrent line items, not a time-ordered version history of one subscription. We tested this directly — checking whether any row's `start_date` lines up with a prior row's `end_date` for the same account — and only found 7 coincidental matches out of 5,000 rows, which is noise, not a real handoff pattern. This has a direct, corrected consequence in Sprint 4 (§13) below.

---

## 7. Project Setup

### 7.1 Repository Structure

```
kpiscope/
├── README.md
├── data/
│   └── raw/                         # original CSV files, untouched
├── sql/
│   ├── 01_create_raw_schema.sql
│   ├── 02_injection.sql
│   ├── 03_staging_cleaning.sql
│   ├── 04_transformation.sql
│   ├── 05_mart_star_schema.sql
│   └── 06_profiling_queries.sql
├── python/
│   ├── connection.py                 # SQL Server connection only
│   ├── calculations.py               # KPI calculations (pandas)
│   ├── visuals.py                    # chart-building functions
│   └── dashboard.py                  # Streamlit/Dash app entry point
├── powerbi/
│   └── KPIScope_Model.pbix
├── documentation/
│   ├── Data_Dictionary.md
│   ├── Data_Quality_Report.md
│   ├── Business_Insights.md
│   └── Sprint_Boards/
│       ├── sprint-0.md
│       ├── sprint-1.md
│       ├── sprint-2.md
│       ├── sprint-3.md
│       ├── sprint-4.md
│       ├── sprint-5.md
│       └── sprint-6.md
└── screenshots/
```

### 7.2 Components & Dependencies

| Layer | Component | Purpose |
| --- | --- | --- |
| Database | SQL Server (Developer or Express edition) | Hosts all four schemas |
| Database client | SSMS (SQL Server Management Studio) | Write/run all SQL scripts |
| Python | Python 3.11+ | Runtime |
| Python | `pyodbc` or `sqlalchemy` + `pyodbc` driver | Connect Python to SQL Server |
| Python | `pandas`, `numpy` | KPI calculations |
| Python | `plotly` or `matplotlib`/`seaborn` | Chart generation |
| Python | `streamlit` (recommended) or `dash` | Interactive dashboard shell |
| Python | ODBC Driver 17/18 for SQL Server | Required by pyodbc to talk to SQL Server |
| Visualization | Power BI Desktop | DAX + report pages |
| Hosting (deployment) | Azure SQL Database (or another cloud SQL Server instance) | Makes the database reachable outside your local machine |
| Version control | Git + GitHub | Repository hosting |

### 7.3 Installation Sequence

1. Install **SQL Server** (Developer edition — free for non-production use).
2. Install **SSMS** and connect to your local SQL Server instance.
3. Install **Python 3.11+** and add it to PATH.
4. Install the **ODBC Driver for SQL Server** (required before `pyodbc` will connect).
5. Create a virtual environment and install Python dependencies:

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   pip install pandas numpy pyodbc sqlalchemy plotly streamlit
   ```
6. Install **Power BI Desktop** (Windows only).
7. Install **Git**, initialize the repository, connect to GitHub.
8. (Deployment step, later) Provision a free/low-tier **Azure SQL Database** instance so the finished `mart` schema is reachable by anyone opening the Power BI file or Python dashboard — not just on your local machine.

---

## 8. Agile Structure

| Sprint | Theme | Owns |
| --- | --- | --- |
| Sprint 0 | Discovery & Data Understanding | Profiling, backlog, KPI wishlist |
| Sprint 1 | Environment & Project Setup | Repo, installs, SQL Server instance live |
| Sprint 2 | Data Injection (SQL) | Raw schema populated from source files |
| Sprint 3 | Data Cleaning (SQL) | Staging schema, standardized values, typed columns |
| Sprint 4 | Data Transformation (SQL) | Clean schema, flags, bands, derived columns |
| Sprint 5 | Data Modeling (SQL) | Mart schema — star schema, fact + dimension tables |
| Sprint 6A | Python Track — Calculations & Visuals | KPI functions, charts, dashboard app |
| Sprint 6B | Power BI Track — Calculations & Visuals | DAX measures, report pages |
| Sprint 7 | Validation, Deployment & Insights | Cross-track number reconciliation, cloud hosting, written insights |

Each sprint below follows: **Goal → Tasks → Definition of Done.**

---

## 9. Sprint 0 — Discovery & Data Understanding

**Goal:** Understand the real structure of the data before writing any SQL.

**Tasks**

1. Download all 5 source files.
2. Open each file and record: row count, column names, data types, an example row.
3. For each file, answer: What does one row represent? What key(s) join it to the other files?
4. Identify obvious data quality issues (blank cells, inconsistent casing, duplicate keys).
5. Draft the initial KPI list (see §18) and confirm it against the columns that actually exist.

**Definition of Done**

- [x] All 5 files profiled and documented in `Data_Dictionary.md`
- [x] Join keys between files identified — all roads lead back to `account_id` (§6)
- [x] Initial backlog and KPI list drafted — with feasibility flags on Expansion/Contraction MRR, NRR, and Channel-based KPIs (see Sprint 4 note and §18)

---

## 10. Sprint 1 — Project Setup & Environment

**Goal:** Every tool installed, repo scaffolded, SQL Server instance reachable from SSMS.

**Tasks**

1. Run through the Installation Sequence (§7.3) in full.
2. Create the repository folder structure (§7.1).
3. In SSMS, create the `kpiscope` database and switch into it (`CREATE DATABASE` does **not** auto-select it):

   ```sql
   CREATE DATABASE kpiscope;
   GO

   USE kpiscope;
   GO
   ```
4. Create all four schemas — each `CREATE SCHEMA` must be the only statement in its batch, so separate them with `GO`:

   ```sql
   CREATE SCHEMA raw;
   GO

   CREATE SCHEMA staging;
   GO

   CREATE SCHEMA clean;
   GO

   CREATE SCHEMA mart;
   GO
   ```
5. Confirm Python can connect to the database:

   ```python
   # python/connection.py
   import os
   import pyodbc
   from dotenv import load_dotenv

   load_dotenv()

   def get_connection_string():
       conn_str = (
           "DRIVER={ODBC Driver 18 for SQL Server};"
           f"SERVER={os.getenv('DB_SERVER')};"
           f"DATABASE={os.getenv('DB_NAME')};"
           "Trusted_Connection=yes;"
           "TrustServerCertificate=yes;"
       )
       return conn_str

   def get_connection():
       return pyodbc.connect(get_connection_string())
   ```

   Credentials live in a `.env` file (never committed — add it to `.gitignore`):

   ```
   DB_SERVER=localhost\SQLEXPRESS
   DB_NAME=kpiscope
   ```
6. Confirm Power BI Desktop can connect: Get Data → SQL Server → your server name → `kpiscope`.

**Definition of Done**

- [x] Database and all 4 schemas exist — verified via:

  ```sql
  SELECT name FROM sys.schemas WHERE schema_id < 16384 ORDER BY name;
  ```
- [x] Python successfully queries `SELECT @@SERVERNAME, DB_NAME();` against the database
- [ ] Power BI successfully connects and lists the (empty) schemas

---

## 11. Sprint 2 — Data Injection (SQL Server)

**Goal:** Load the 5 raw files into SQL Server exactly as received, with zero transformation.

**Tasks**

1. Create one raw table per source file, all columns typed as `NVARCHAR` (avoids load failures from inconsistent formatting), matching the real column names confirmed in §6 — not guessed names:

   ```sql
   CREATE TABLE raw.accounts (
       account_id NVARCHAR(50),
       account_name NVARCHAR(200),
       industry NVARCHAR(100),
       country NVARCHAR(10),
       signup_date NVARCHAR(50),
       referral_source NVARCHAR(50),
       plan_tier NVARCHAR(50),
       seats NVARCHAR(50),
       is_trial NVARCHAR(10),
       churn_flag NVARCHAR(10)
   );
   -- repeat for subscriptions, feature_usage, support_tickets, churn_events,
   -- using each table's exact column list from §6
   ```
2. Load each file into its raw table using SSMS's **Import Flat File** wizard (right-click database → Tasks → Import Flat File), or `BULK INSERT`:

   ```sql
   BULK INSERT raw.accounts
   FROM 'C:\kpiscope\data\raw\accounts.csv'
   WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');
   ```
3. Run row-count and null-count profiling queries against every raw table; log results in `Data_Quality_Report.md`. Known nulls to expect going in (from §6/Sprint 0): `feedback_text` (\~25% missing in churn_events), `satisfaction_score` (\~41% missing in support_tickets), `end_date` (only populated for closed subscriptions).

**Definition of Done**

- [ ] All 5 raw tables populated, row counts match source file counts exactly (500 / 5,000 / 25,000 / 2,000 / 600 — see §6)
- [ ] No transformation logic applied at this stage
- [ ] Profiling results documented

---

## 12. Sprint 3 — Data Cleaning (SQL Server)

**Goal:** Produce standardized, correctly-typed data in the `staging` schema, without changing meaning.

**Tasks**

1. Create typed staging tables (proper `DATE`, `DECIMAL`, `INT`, `BIT` columns instead of `NVARCHAR`).
2. Write `INSERT INTO staging... SELECT ... FROM raw...` statements that:
   - Trim whitespace: `TRIM(column)`
   - Standardize casing: `UPPER()`/proper-case logic for categorical fields (e.g. `plan_tier`, `referral_source`)
   - Cast types safely: `TRY_CAST(mrr_amount AS DECIMAL(10,2))`
   - Preserve failed casts as `NULL` rather than silently defaulting to 0
3. Flag (don't drop) duplicate and orphaned rows — but be precise about what "duplicate" means per table, since our Sprint 0 profiling found tables have different grains:

   ```sql
   -- accounts: account_id should be genuinely unique — a hit here IS a duplicate
   SELECT account_id, COUNT(*) AS occurrences
   FROM staging.accounts
   GROUP BY account_id
   HAVING COUNT(*) > 1;
   ```

   ```sql
   -- subscriptions: DO NOT apply the same ">1 per account_id" logic here.
   -- Confirmed in Sprint 0: one account legitimately has many concurrent
   -- subscription rows (we saw up to 16). Check subscription_id for true
   -- duplicates instead — account_id repeating is expected, not an error.
   SELECT subscription_id, COUNT(*) AS occurrences
   FROM staging.subscriptions
   GROUP BY subscription_id
   HAVING COUNT(*) > 1;
   ```
4. Document every standardization decision made (e.g. "Enterprise / enterprise / ENT" → "Enterprise").

**Definition of Done**

- [ ] `staging` schema populated with correctly typed columns
- [ ] All casing/format inconsistencies resolved and logged
- [ ] Duplicate/orphaned rows identified per-table, using the correct grain for each — and a decision documented for each finding

---

## 13. Sprint 4 — Data Transformation (SQL Server)

**Goal:** Derive the analytical columns the KPIs depend on, writing results into the `clean` schema.

**Tasks — build these as views or `INSERT ... SELECT` statements**

| Column | SQL Logic | Feeds |
| --- | --- | --- |
| `is_active_flag` | `CASE WHEN churn_flag = 0 THEN 1 ELSE 0 END` — uses `accounts.churn_flag` directly; there is no separate `status` column | Active Accounts |
| `is_churned_flag` | `CASE WHEN account_id IN (SELECT account_id FROM staging.churn_events) THEN 1 ELSE 0 END` | Churn Rate |
| `is_churned_flag` (reconciliation check) | Compare against `subscriptions.churn_flag` / `accounts.churn_flag` — these three should agree per account; log any mismatch instead of silently picking one source | Data quality |
| `tenure_days` | `DATEDIFF(DAY, signup_date, COALESCE(churn_date, GETDATE()))` (join `accounts.signup_date` to `churn_events.churn_date`) | Cohort analysis |
| `tenure_band` | `CASE WHEN tenure_days <= 90 THEN '0-90' WHEN tenure_days <= 180 THEN '91-180' ... END` | Segmentation |
| `mrr_band` | `CASE WHEN mrr_amount < 500 THEN 'Low' WHEN mrr_amount < 2000 THEN 'Medium' ... END` | Segmentation |
| `support_load_flag` | `CASE WHEN ticket_count > threshold THEN 1 ELSE 0 END` | Operational risk |

> **Corrected based on Sprint 0 findings — read before building Expansion/Contraction MRR.** The original plan for `expansion_flag`/`contraction_flag` was a `LAG()` window function comparing "current vs. prior period `mrr`" per account. **That doesn't work with this data.** Sprint 0 profiling confirmed `subscriptions` rows per account are *concurrent* line items (e.g. one Basic + one Enterprise subscription open at the same time for one account), not a time-ordered version history of a single subscription being upgraded — there's no "prior period" to `LAG()` against, and we directly tested for a chained handoff pattern (row N's `end_date` lining up with row N+1's `start_date`) and found only 7 coincidental matches out of 5,000 rows.
> 
> **Use this instead — a labeled proxy, not a true MRR delta:**
> 
> ```sql
> SELECT
>     account_id,
>     subscription_id,
>     mrr_amount,
>     upgrade_flag,
>     downgrade_flag,
>     -- proxy only: treats the whole mrr_amount of an upgrade-flagged row
>     -- as "expansion," since we can't isolate the actual increase amount
>     CASE WHEN upgrade_flag = 1 THEN mrr_amount ELSE 0 END AS expansion_mrr_proxy,
>     CASE WHEN downgrade_flag = 1 THEN mrr_amount ELSE 0 END AS contraction_mrr_proxy
> INTO clean.subscription_activity
> FROM staging.subscriptions;
> ```
> 
> Before trusting this proxy for real reporting, check whether `mrr_amount = 0` rows cluster under `is_trial = 1` — we found a couple of zero-MRR, upgrade-flagged Enterprise rows in a sample and haven't yet confirmed if that's a trial artifact or a genuine data issue. Exclude trial rows from the proxy if so.

**Definition of Done**

- [ ] Every derived column implemented in SQL, not in Python or DAX
- [ ] Each transformation's logic documented (input → rule → output column)
- [ ] Spot-checked: 3–5 rows manually verified against source values
- [ ] Expansion/Contraction MRR explicitly documented as a proxy, not an exact figure, everywhere it's surfaced downstream (Python, Power BI, and any written insight)

---

## 14. Sprint 5 — Data Modeling (SQL Server)

**Goal:** Build the final star schema in the `mart` schema — this is what both Python and Power BI will connect to.

**Tasks**

1. Build dimension tables with surrogate keys:

   ```sql
   CREATE TABLE mart.dim_account (
       account_key INT IDENTITY(1,1) PRIMARY KEY,
       account_id NVARCHAR(50) UNIQUE,
       account_name NVARCHAR(200),
       industry NVARCHAR(100),
       country NVARCHAR(10)
   );

   CREATE TABLE mart.dim_plan (
       plan_key INT IDENTITY(1,1) PRIMARY KEY,
       plan_tier NVARCHAR(50) UNIQUE
   );

   CREATE TABLE mart.dim_channel (
       channel_key INT IDENTITY(1,1) PRIMARY KEY,
       referral_source NVARCHAR(50) UNIQUE
   );

   CREATE TABLE mart.dim_date (
       date_key DATE PRIMARY KEY,
       year INT, month INT, quarter INT
   );
   ```
2. Build the fact table, keyed against dimensions:

   ```sql
   CREATE TABLE mart.fact_subscription_activity (
       fact_id INT IDENTITY(1,1) PRIMARY KEY,
       account_key INT REFERENCES mart.dim_account(account_key),
       plan_key INT REFERENCES mart.dim_plan(plan_key),
       channel_key INT REFERENCES mart.dim_channel(channel_key),
       period_date_key DATE REFERENCES mart.dim_date(date_key),
       mrr_amount DECIMAL(10,2),
       is_active_flag BIT,
       is_churned_flag BIT,
       upgrade_flag BIT,
       downgrade_flag BIT,
       expansion_mrr_proxy DECIMAL(10,2),
       contraction_mrr_proxy DECIMAL(10,2),
       tenure_days INT
   );

   CREATE TABLE mart.fact_support_tickets (
       ticket_key INT IDENTITY(1,1) PRIMARY KEY,
       account_key INT REFERENCES mart.dim_account(account_key),
       opened_date_key DATE,
       resolved_date_key DATE,
       priority NVARCHAR(50),
       resolution_time_hours DECIMAL(10,2),
       satisfaction_score DECIMAL(3,1) NULL,
       escalation_flag BIT
   );
   ```
3. Populate dimensions and fact tables from `clean` schema.
4. Create a lightweight read-only SQL login/user for Python and Power BI to connect with (no write access to `raw`/`staging`/`clean`).

**Definition of Done**

- [ ] Star schema built with correct primary/foreign keys, no orphaned foreign keys
- [ ] Fact table grain explicitly documented (e.g. "one row per subscription line item per account, per period")
- [ ] Read-only credentials created for downstream tools

---

## 15. Sprint 6A — Python Track: Calculations & Visuals

**Goal:** Python connects only to `mart`, computes KPIs, and renders an interactive dashboard.

**Tasks**

1. **Connect and pull data:**

   ```python
   # python/calculations.py
   import pandas as pd
   from connection import get_connection

   def load_fact_table():
       conn = get_connection()
       query = """
           SELECT f.*, a.industry, a.country, p.plan_tier, ch.referral_source
           FROM mart.fact_subscription_activity f
           JOIN mart.dim_account a ON f.account_key = a.account_key
           JOIN mart.dim_plan p ON f.plan_key = p.plan_key
           JOIN mart.dim_channel ch ON f.channel_key = ch.channel_key
       """
       return pd.read_sql(query, conn)
   ```
2. **KPI calculations (mirror the DAX measures exactly — see §18 KPI Dictionary):**

   ```python
   def total_mrr(df):
       return df["mrr_amount"].sum()

   def churn_rate(df):
       return df["is_churned_flag"].sum() / df["account_key"].nunique()

   def expansion_mrr_proxy(df):
       # proxy, not a true delta — see Sprint 4 note
       return df["expansion_mrr_proxy"].sum()

   def churn_rate_by_channel(df):
       return df.groupby("referral_source").apply(
           lambda g: g["is_churned_flag"].sum() / g["account_key"].nunique()
       )
   ```
3. **Visuals:**

   ```python
   # python/visuals.py
   import plotly.express as px

   def mrr_trend_chart(df):
       trend = df.groupby("period_date_key")["mrr_amount"].sum().reset_index()
       return px.line(trend, x="period_date_key", y="mrr_amount", title="MRR Trend")

   def churn_by_channel_chart(df):
       data = churn_rate_by_channel(df).reset_index(name="churn_rate")
       return px.bar(data, x="referral_source", y="churn_rate", title="Churn Rate by Referral Source")
   ```
4. **Dashboard shell:**

   ```python
   # python/dashboard.py
   import streamlit as st
   from calculations import load_fact_table, total_mrr, churn_rate
   from visuals import mrr_trend_chart, churn_by_channel_chart

   df = load_fact_table()

   st.title("KPIScope — Python Dashboard")
   col1, col2 = st.columns(2)
   col1.metric("Total MRR", f"${total_mrr(df):,.2f}")
   col2.metric("Churn Rate", f"{churn_rate(df):.1%}")

   st.plotly_chart(mrr_trend_chart(df))
   st.plotly_chart(churn_by_channel_chart(df))
   ```
5. Run locally: `streamlit run python/dashboard.py`

**Definition of Done**

- [ ] Every KPI in §18's dictionary implemented as a Python function
- [ ] Dashboard runs and displays live data pulled from `mart`
- [ ] No cleaning/transformation logic present in Python — calculation only
- [ ] Any function built on the Expansion/Contraction MRR proxy is named/commented to say so

---

## 16. Sprint 6B — Power BI Track: Calculations & Visuals

**Goal:** Power BI connects only to `mart`, independently, and builds its own report using DAX.

**Tasks**

1. Get Data → SQL Server → point at `mart` schema tables only. Use Import mode.
2. Verify/correct relationships between `fact_subscription_activity` and each `dim_*` table (one-to-many).
3. Build the DAX measure library (identical logic to the Python calculations, different language):

   ```DAX
   Total MRR = SUM ( fact_subscription_activity[mrr_amount] )

   Churned Accounts =
   CALCULATE ( DISTINCTCOUNT ( fact_subscription_activity[account_key] ),
       fact_subscription_activity[is_churned_flag] = 1 )

   Account Churn Rate =
   DIVIDE ( [Churned Accounts], DISTINCTCOUNT ( fact_subscription_activity[account_key] ) )

   Expansion MRR (proxy) =
   SUM ( fact_subscription_activity[expansion_mrr_proxy] )

   Churn Rate by Channel =
   CALCULATE ( [Account Churn Rate], ALLEXCEPT ( dim_channel, dim_channel[referral_source] ) )
   ```
4. Build report pages: Executive Summary, Financial, Marketing/Acquisition, Operations.
5. Publish to Power BI Service once the underlying SQL Server database is cloud-hosted (see Sprint 7).

**Definition of Done**

- [ ] All relationships verified, no ambiguous filter paths
- [ ] Every DAX measure implemented and spot-checked against a raw `SUM()`/`COUNT()` SQL query
- [ ] Report pages built and visually consistent
- [ ] "Expansion MRR" and "Contraction MRR" measures are explicitly labeled `(proxy)` on the report, not presented as exact figures

---

## 17. Sprint 7 — Validation, Deployment & Insights

**Goal:** Prove both tracks agree, make the project accessible beyond your local machine, and write up findings.

**Tasks**

1. **Cross-track reconciliation:** pick 5 KPIs, compute each one in SQL directly, in Python, and in Power BI. All three numbers must match exactly. Log this in `Data_Quality_Report.md`.
2. **Deployment:** provision an Azure SQL Database (or equivalent cloud SQL Server), migrate the `mart` schema there, and repoint both the Python connection string and the Power BI data source to the cloud instance — this is what makes the project usable by anyone other than you.
3. **Insights:** write at least 5 insights using this structure, each tied to a specific KPI:

   ```
   Insight: [one-sentence discovery]
   Evidence: [the specific number/pattern from the model]
   Business Meaning: [why it matters]
   Recommendation: [what to do about it]
   ```
4. Push the full repository to GitHub with a clean README, screenshots of both dashboards, and a short write-up of the architecture.

**Definition of Done**

- [ ] All reconciled KPIs match across SQL, Python, and Power BI
- [ ] Database reachable from a cloud endpoint, not just localhost
- [ ] 5+ insights documented
- [ ] Repository published

---

## 18. KPI Dictionary (shared logic — implement identically in both tracks)

| KPI | Logic | Track A (Python) | Track B (Power BI) | Status |
| --- | --- | --- | --- | --- |
| Total MRR | Sum of `mrr_amount` | `df["mrr_amount"].sum()` | `SUM(fact[mrr_amount])` | ✅ Direct |
| Total ARR | Total MRR × 12, cross-checked against `arr_amount` | function | measure | ⚠️ Needs definition check — see §6/§19 |
| Churn Rate | Churned ÷ Total accounts | function | measure | ✅ Direct |
| Net Revenue Retention | (MRR − Churned MRR + Expansion MRR) ÷ MRR | function | measure | ⚠️ Proxy-based — see Sprint 4 (§13) |
| Expansion MRR | Sum of `mrr_amount` where `upgrade_flag = 1` | function | measure | ⚠️ Proxy, not a true delta |
| Contraction MRR | Sum of `mrr_amount` where `downgrade_flag = 1` | function | measure | ⚠️ Proxy, not a true delta |
| New Accounts by Referral Source | Distinct accounts grouped by `referral_source` | groupby | `ALLEXCEPT` measure | ✅ Direct — confirmed real column |
| Churn Rate by Referral Source | Churn rate grouped by `referral_source` | groupby | `ALLEXCEPT` measure | ✅ Direct — confirmed real column |
| Avg. Resolution Time | Avg hours between ticket opened/resolved (`resolution_time_hours`) | function | measure | ✅ Direct — already pre-computed in source data, in hours not days |

---

## 19. Business Questions (both dashboards should answer these)

1. What is the ARR trend over the period?
2. Is the business net-retaining revenue (NRR above or below 100%) — reported as an estimate, given the proxy basis?
3. Which acquisition channel (`referral_source`) brings the most new accounts, and which has the healthiest churn?
4. Which plan tier generates the most revenue, and is it also the most retained?
5. Is there a relationship between support ticket load and churn? (state as correlation, not causation)

---

## 20. Final Checklist

- [ ] `raw`, `staging`, `clean`, `mart` schemas all populated in SQL Server, in that order, with zero manual edits
- [ ] Python dashboard running against `mart`, all KPIs implemented, no cleaning logic in Python
- [ ] Power BI report running against `mart`, all DAX measures implemented, no cleaning logic in Power BI
- [ ] 5 KPIs reconciled and matching across SQL/Python/Power BI
- [ ] Database hosted on a reachable cloud endpoint
- [ ] Repository pushed to GitHub with README, screenshots, insights
- [ ] Every proxy-based metric (Expansion MRR, Contraction MRR, NRR) is labeled as a proxy everywhere it appears

---

## 21. Executive Scorecard Visual Design — 5×5 Tile Layout

This is the layout spec for the Power BI Executive Summary page. Build one "pillar" as a reusable visual group, then duplicate it across all five pillars.

> **Note:** the pillars below are mapped directly to the 5 Business Questions in §19 and the KPIs this dataset can actually support (§18) — not a generic sales-pipeline template. A scorecard pillar like "Outbound Meetings Booked" would need data KPIScope doesn't have (no CRM/sales-activity table exists in §6), so it's deliberately left out here.

**Grid: 5 columns × 5 rows**

- **Row 1 — Pillar header:** one colored banner per pillar, each a distinct pillar name (below). Colors differ per pillar purely for visual separation, not status.
- **Row 2 — Headline trend chart:** a line chart per pillar plotting **Goal vs. Actual** across 12 periods (weeks or months) — a smooth "Goal" line and a more volatile "Actual" line, so the gap between plan and reality is visible immediately.
- **Row 3 — Status bar:** a thin colored strip directly under each chart (green/yellow/red) as a traffic-light health indicator for that pillar overall.
- **Rows 4–5 — Supporting metric tiles:** 4 stacked boxes per pillar, each with a metric label and a large number value, each with its own thin colored underline for per-metric status.

**Pillar-to-metric mapping (grounded in §18's KPI Dictionary):**

| Pillar | Supporting metrics shown |
| --- | --- |
| Revenue Trend | Total MRR, Total ARR, MRR Growth Rate (period-over-period), Avg MRR per Account |
| Net Revenue Retention | NRR (proxy), Expansion MRR (proxy), Contraction MRR (proxy), Churn Rate |
| Referral Source Performance | New Accounts by Referral Source, Churn Rate by Referral Source, Avg Seats by Referral Source, Trial Conversion Rate by Referral Source |
| Plan Tier Performance | Revenue by Plan Tier, Churn Rate by Plan Tier, Avg Tenure by Plan Tier, Seats by Plan Tier |
| Support Load & Churn Risk | Escalation Rate, Avg. Resolution Time, Tickets per Account (at-risk threshold), Avg. Satisfaction Score (excluding non-responses) |

**Power BI build notes:**

- Each metric tile's colored underline should be driven by conditional formatting rules on the measure (e.g. green ≥ target, yellow = within 10% of target, red = below threshold).
- The Goal-vs-Actual line chart pairs a static/planned target measure against the live actual measure — build the "Goal" as either a flat target line or a cumulative plan curve depending on the KPI.
- Keep this page to exactly 5 pillars, matching the "5×5, don't overwhelm" principle — resist adding a 6th pillar or a 5th metric row.
- Any tile driven by a proxy metric (Expansion/Contraction MRR, NRR) should carry a visible "(proxy)" label on the tile itself, not just in documentation — the CEO reading the scorecard won't open this README.

---

## 22. Extended KPI Glossary (SaaS Churn, Retention & Growth Terms)

Supplementary terms to fold into the KPI Dictionary (§18) as they come up in modeling and reporting.

**Core Churn & Retention**

- **Churn Flag / Churn Rate** — binary status or overall percentage indicating an account that canceled or stopped its subscription.
- **Account Retention Rate** — percentage of accounts who continue paying and do not cancel over a given period.
- **At-Risk Accounts** — accounts displaying early warning behaviors (low usage, downgrades, negative support sentiment) likely to churn.
- **Reason Code** — categorical classification explaining why an account canceled (e.g. pricing, missing features, poor support).
- **Account Reactivation** — when a previously churned account returns and signs up for a new subscription.

**Revenue & Plan Expansion**

- **ARR (Annual Recurring Revenue)** — predictable yearly subscription value generated by active accounts.
- **Upgrade / Expansion** — when an existing account increases spend by upgrading tier or adding seats.
- **Downgrade / Contraction** — when an existing account reduces spend by moving to a lower tier or fewer seats.
- **Plan Tier** — the package level an account subscribes to (Basic/Pro/Enterprise), determining feature access and pricing.
- **Seats (License Count)** — number of paid/provisioned user licenses assigned to an account.

**Acquisition & Pipeline**

- **Referral Source** — acquisition channel through which an account found the platform (organic, ads, partner, event).
- **Trial / Trial Conversion** — an account currently evaluating the product before converting to paying.
- **Cohort Analysis** — grouping accounts by a shared characteristic (typically signup date/month) to track how retention, upgrades, or churn develop over time.

**Operations & Reporting Framework**

- **Leading Indicator** — early metrics that predict future events (e.g. recent downgrades predicting cancellation).
- **Lagging Indicator** — metrics reflecting past outcomes (e.g. total churned revenue last quarter).
- **KPI Ownership & Data Governance** — the standard protocols and assigned stakeholders ensuring data integrity, tracking accuracy, and consistent schema definitions across tables.