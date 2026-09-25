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