# Day 01 | Introduction to Data Engineering — From First Principles to Architecture Decisions

> **Audience:** First-time learners progressing toward professional data engineering design.  
> **Scenario:** An Australian omnichannel retail reference scenario.
>
> **Prerequisites:** None.  
> **Outcome:** Explain why a pipeline exists, trace a record through it, and critique an Azure reference architecture.

## Learning path: three levels of understanding

| Stage | Learner can explain | Evidence |
|---|---|---|
| 1 — Understand | Why operational data cannot simply become a trustworthy dashboard | Draw a source-to-report flow and explain every stage |
| 2 — Apply | How ingestion, quality, modeling and orchestration work together | Design a daily sales pipeline and describe its data contract |
| 3 — Design | Why architecture includes recovery, access controls, monitoring and trade-offs | Defend choices for a realistic enterprise workload |

## 1. What data engineering means

**Definition.** Data engineering builds and operates the systems that collect, validate, transform and deliver data with a defined business meaning.

| Responsibility | Primary question | Typical output |
|---|---|---|
| Operational application | Was this sale recorded correctly? | A committed transaction |
| Data engineering pipeline | Can users reliably use sales from every store? | A validated, traceable sales dataset |
| Business analysis | What changed in sales and what explains it? | An interpretation based on agreed measures |

> **Worked example · Retail sales close** — A store records two units at AUD 35 each with a 10% discount. The pipeline retains the source line, validates the quantity and discount, and publishes AUD 63 as merchandise sales before tax or later refunds. Finance can trace that figure back to the source line and reproduce it by applying the same rule.

### Start with the business problem

Imagine a retail chain with 45 stores, an online shop and a warehouse. The point-of-sale application records purchases. The ecommerce application records web orders. The ERP system manages products and inventory. Finance asks: **What was yesterday's net revenue by store and product category?**

A dashboard cannot answer reliably by simply concatenating these systems. One application records timestamps in local time, another in UTC; the POS has voided sales; web orders may be cancelled; a product might have changed category; and late refunds can arrive after the original sale.

**Data engineering** is the discipline of building and operating systems that collect, preserve, check, transform and deliver data so that other people and systems can use it reliably. The goal is not just movement. It is **trusted, reproducible data with an agreed business meaning**.

### A beginner's analogy

Think of a commercial kitchen:

| Kitchen | Data engineering | Why it matters |
|---|---|---|
| Ingredients delivered | Source data acquired | Inputs arrive in different shapes and at different times |
| Goods-received register | Raw landing and metadata | You can trace what arrived and when |
| Hygiene and quality inspection | Validation | Bad inputs are flagged rather than silently accepted |
| Preparation and cooking | Transformation | Raw materials become standardized, usable outputs |
| Menu and plated meal | Curated model or data product | Consumers receive a defined, consistent result |
| Kitchen operations and safety | Monitoring, security, recovery | The process remains dependable every day |

The analogy is useful but incomplete: data pipelines also need historical replay, versioned schemas, access restrictions and automated recovery.

## 2. What happens to one sale?

**Example source event:** Store 014 sells 2 units of product P-482 at AUD 35 each, with a 10% discount, at 17:42 Australia/Sydney time.

1. **Capture the business event.** Preserve source order ID, line ID, product, quantity, price, discount, source timestamp and store.
2. **Ingest the record.** A scheduled extraction or CDC mechanism reads the source. Capture the run ID and source watermark or offset.
3. **Land raw evidence.** Keep the original representation plus source filename/table, ingestion time and batch ID. Do not silently overwrite raw history.
4. **Validate.** Check whether the order-line key is present, quantity is valid, price is numeric and the timestamp can be interpreted. Quarantine invalid records with a reason.
5. **Standardize.** Normalize the timestamp to UTC while preserving local business date; standardize product/store identifiers and currency semantics.
6. **Model.** Link the transaction to the agreed product and store dimensions. Decide whether the reporting grain is one order line, one order or a daily aggregate.
7. **Serve.** Publish a governed sales fact for Power BI or SQL users, with an explicit net-sales definition.
8. **Observe.** Reconcile row counts and amounts against source controls, measure freshness and alert on failed loads.

### A subtle but important distinction: business time versus processing time

The sale happened at 17:42 local time. The data might be ingested at 18:05 and corrected the next morning. Event time, ingestion time and processing time are different. A daily sales report needs a documented rule for late changes and which time zone defines a business day.

## 3. The responsibilities inside a pipeline

### 3.1 Source ownership and ingestion

A source system owns some part of the business record. The point-of-sale system owns the sale and the ERP owns product attributes. An ingestion job copies selected source evidence into the analytical environment. It must record the source identity, the bounds of the read, and its completion status. If two systems both supply a product category, the design must identify which system is authoritative for which reporting period. Otherwise a reliable copy can still produce inconsistent reporting.

### 3.2 Raw landing and the data contract

The raw layer preserves source payloads with enough context to replay them. A data contract explains how to interpret those payloads. It specifies the schema, business keys, version ordering, null and delete behavior, expected delivery cadence, and who approves breaking changes. For the retail feed, require an order ID, line ID, currency, source version and event timestamp. If a record loses its line ID, the platform cannot safely deduplicate or update it. Keep its original payload and rejection reason and route it for correction.

### 3.3 Transformation and quality

A transformation changes shape, representation or meaning. Parsing a timestamp changes representation. Applying an agreed Sydney business-date rule changes how that timestamp is used by the report. A quality check then verifies a stated expectation, such as every accepted order line having a valid monetary amount, or every repeated version having the same payload. Track accepted, repeated and quarantined records independently so a control-total discrepancy can be traced to a particular decision.

### 3.4 Modeling, grain and serving

A data model specifies entities, relationships and what one row represents. At order-line grain, the quantity and net amount belong to the line. The product and store dimensions provide attributes used to group those measures. When the business needs historical category reporting, agree whether to use the category in effect at the sale or the current category. Power BI can then define the measure once against a governed model and use the same definition across reports.

### 3.5 Orchestration, idempotency and lineage

Orchestration controls the order and conditions of work. It starts validation after ingestion has finalized its manifest, and schedules serving refresh after the validated Gold publication. Idempotency gives an operator a predictable outcome when a stage is repeated. Applying an already accepted version preserves the accepted values and totals. Lineage connects a visible result back through the fact row, the transform run and the raw batch. Keep these identifiers where the operator can find them during reconciliation.

### 3.6 Ownership and service expectations

Treat published sales data as a product with identified consumers, an owner, and a documented meaning. Agree what freshness means for each consumer. Finance may require an accepted close by a specific local time, while fulfilment may prefer provisional updates throughout the day. Expose freshness and acceptance explicitly and define who acts when the agreement is missed.

## 4. From simple flow to a real architecture

### Stage A — Conceptual architecture

**Operational systems → Ingestion → Raw evidence → Validation and transformation → Curated datasets → Reporting and analytics**

This diagram answers *what must happen*. It does not yet select vendors, regions or compute engines. That is intentional: beginners should understand responsibilities before learning brand names.

### Stage B — Logical architecture

Split responsibilities into distinct components:

- **Sources:** POS SQL Server, ecommerce API, ERP product master.
- **Acquisition:** Scheduled extracts for stable daily files; incremental reads or supported CDC for changing transactions.
- **Raw storage:** Partition by source and ingestion date, retain source identifiers and ingest metadata.
- **Processing:** Validate schema, deduplicate by stable business key, normalize time zones and build conformed entities.
- **Curated model:** Sales fact with explicit grain, plus product, store and date dimensions.
- **Consumption:** Governed SQL and Power BI semantic model.
- **Cross-cutting controls:** Identity, secrets, network access, lineage, quality, observability, retention and cost.

This diagram answers *which capabilities must exist and how they interact*.

### Stage C — Illustrative Azure implementation

One possible Azure implementation uses **Azure Data Factory** to orchestrate ingestion, **Azure Data Lake Storage Gen2** to store raw and curated data, **Azure Databricks** for transformations, and **Power BI** for governed consumption. **Azure Monitor** provides observability; **Microsoft Entra ID** and **Azure Key Vault** support identity and secret-management patterns.

These are **illustrative service choices**, not the only valid architecture. In some organizations, Microsoft Fabric or an Azure SQL-centered warehouse may be simpler. Selecting Databricks just because it appears in a diagram is not architecture reasoning.

## 5. How to read an architecture diagram

Read from left to right: **where data originates**, **which service moves it**, **where it is persisted**, **which component changes its meaning**, and **how it is consumed**. Then inspect the boundaries: which resources are in Azure, what is external, where credentials are stored, and where monitoring and governance apply.

Every arrow should answer a question. Does it represent a file copy, an API call, a CDC stream, a table read, a transformation output or a dashboard query? A line with no defined meaning is not sufficient for a production design.

A professional architecture should also explain **failure paths**. If ingestion fails halfway through, does a rerun duplicate records? If the product dimension arrives late, does the sales fact become incorrect? If a schema adds a new field, does the pipeline fail safely or silently lose it?

## 6. Batch, streaming and CDC — introductory comparison

| Pattern | Trigger | Example | Main engineering concern |
|---|---|---|---|
| Batch | A schedule or bounded request | Every morning, extract yesterday's orders | Windows, retries, late postings |
| Streaming | Continuous arrival of events | Device telemetry or clickstream | Ordering, checkpoints, event time |
| Change data capture | Source inserts/updates/deletes | Replicate changed order rows | Deletes, offsets, retention, target merge |

**CDC is a change-capture technique**, not a synonym for streaming analytics. An architecture can capture changes continuously but process them into reporting tables every 15 minutes.

## 7. ETL, ELT and storage choices

**ETL:** Extract, transform in a processing stage, then load the target. **ELT:** Extract, load to the analytical platform, then transform using that platform's compute. Both require security, validation and operational discipline.

A **data lake** accommodates diverse raw and refined formats. A **warehouse** prioritizes structured analytical querying and governed relational models. A **lakehouse** combines lake-style storage with transactional table capabilities. The best choice depends on source diversity, workloads, SQL/Spark needs, governance, cost and team capability—not a universal ranking.

Microsoft describes bronze, silver and gold as progressive quality layers: raw source fidelity, validated/conformed data, and business-ready consumption. These layers are a design pattern, not three mandatory Azure products.

## 8. Reliability and operational design

### Source contract example

| Field | Requirement |
|---|---|
| Dataset | `pos_order_lines` |
| Grain | One source order line |
| Primary business key | `source_system + order_id + line_id` |
| Cadence | Hourly incremental |
| Freshness target | Within 90 minutes of source commit |
| Expected change behavior | Inserts, updates and cancellations |
| Sensitive fields | No direct cardholder data permitted |
| Owner | Retail transaction platform team |
| Recovery | Reprocess a source window without duplicate business rows |

### What production teams must decide

**Quality:** Should a missing product key fail the entire batch, quarantine individual rows or create an unknown-member record? The answer depends on business impact.

**Recovery:** Keep durable checkpoints and stable deduplication keys. A successful retry should not double-count sales.

**Security:** Use least-privilege access and managed identity where supported; do not hard-code passwords in notebooks or pipeline JSON.

**Observability:** Track source-to-target counts, rejected records, freshness, run duration and cost. A green pipeline status is not proof that the numbers are correct.

**Governance:** Define retention, ownership, access and lineage before making a data product widely available.

## 9. A guided architecture decision

**Requirement:** Finance wants final daily net sales at 08:00; store operations wants provisional hourly sales.

A reasonable starting design uses a single trusted ingestion foundation with different downstream refresh expectations. Raw records preserve late changes. Silver reconciles duplicates and cancellations. Gold exposes an hourly provisional metric and a daily finalized metric with distinct definitions.

**Why not make everything streaming?** Streaming introduces state, checkpoints and operational complexity. If the consumer accepts hourly or daily freshness, batch or micro-batch may meet the requirement at lower cost and with simpler support.

**Why not report directly from POS?** It could affect operational performance and would not reconcile ERP product data, ecommerce cancellations or historical corrections.

**What could change the design?** Multi-region data residency, near-real-time fraud detection, source CDC limitations, strict recovery objectives, existing enterprise platform investments or highly sensitive information.

## 10. Worked recovery example

### Walk through one batch from source to Power BI

The source emits two order lines, AU-104/1 at AUD 89 and AU-104/2 at AUD 31, each at version 1. A retry delivers the first line again. Bronze retains all three receipts. The manifest records three rows because it describes what arrived. Silver accepts two keys because it describes the current business state. The repeated receipt contributes zero to Gold. The initial amount is AUD 120 for two accepted lines. These differences are expected and should be visible in the reconciliation.

A later batch delivers version 2 of AU-104/2 with AUD 25. Silver replaces the accepted value for that line. Gold recomputes the affected Sydney reporting date and records the new total of AUD 114. Finance can see the AUD 6 adjustment and trace it to the new source version. An exact replay leaves the total at AUD 114. If the same source key and version 2 later claim AUD 27, record the conflict and withhold the affected publication until the discrepancy is resolved under the source contract.

If the job stops after Gold is written, the next attempt checks which batch produced the current Gold state. A matching publication can be reconciled and marked complete. If there is no accepted publication, the job reads the same Bronze batch and applies the same merge and validation rules. Power BI refreshes only from a validated publication. The last accepted reporting date stays visible while the recovery is in progress.

## 11. What to study next

Day 02 deepens OLTP versus OLAP and ETL versus ELT. Day 03 introduces file formats, databases and APIs. Day 04 examines batch, streaming, incremental loads and CDC in depth. Day 05 assembles a complete modern Azure data platform architecture.

## References — official documentation first

1. [Microsoft Azure Architecture Center — data lake scenarios](https://learn.microsoft.com/en-us/azure/architecture/data-guide/scenarios/data-lake)
2. [Microsoft Azure Architecture Center — modern analytics with Azure Databricks](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-databricks-modern-analytics-architecture)
3. [Microsoft Azure Architecture Center — official Azure icons](https://learn.microsoft.com/en-us/azure/architecture/icons/)
4. [Azure Databricks — medallion lakehouse architecture](https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion)
5. [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
6. [Azure Data Factory overview](https://learn.microsoft.com/en-us/azure/data-factory/introduction)

*This is original teaching material informed by linked Microsoft documentation, not a copy of Microsoft's diagrams or tutorials.*

**Madhur Mehta( professorofdata)**


## The engineering system behind a metric

A dashboard value is the last step in a chain of decisions. Start with the question its reader will act on, identify the event that represents the business fact, and state the row grain before selecting a service. For the paid-order example, an order-line sale and a payment settlement are different facts: one describes a commercial commitment; the other confirms the transfer of money. Joining either event to a many-row status history without first selecting the appropriate version causes fan-out and overstatement.

A useful data contract specifies: producer and owner; record key and grain; field types and meanings; update and delete semantics; event timestamp and time zone; expected delivery frequency; allowed lateness; schema-change process; sensitivity classification; and controls for counts and monetary totals. The consumer contract adds published-through time, metric definitions, availability target, correction policy, and support ownership. These contracts are versioned documents, not merely inferred schemas.

| Layer | Input and responsibility | Output and evidence |
|---|---|---|
| Source | Application writes business events under its own transaction rules | Stable identifiers, timestamps, source versions |
| Ingestion | Capture a bounded set of records without silently dropping changes | Durable batch or offset manifest and source counts |
| Storage | Preserve controlled raw evidence for replay and audit | Immutable receipt, access policy, retention rule |
| Transformation | Standardize, deduplicate, validate and model at declared grains | Rejected-record reason codes and tested tables |
| Serving | Publish governed measures to an agreed audience | Versioned data product, freshness and reconciliation |
| Operations | Detect drift, failure and cost anomalies, then recover safely | Run log, alerts, ownership and replay procedure |

### Define the business outcome before the pipeline

Southbank Retail has two consumers. The fulfilment team needs a near-current count of paid orders not dispatched. Finance needs a reproducible daily close after settlement and returns have had time to arrive. One table can support both only if it exposes status, currency, event time, published-through time and whether the value is provisional. If it hides late corrections, finance cannot reproduce yesterday's published total. If it waits for finance close, operations sees stale data. The design should make those distinct service expectations explicit.

For a daily net-settled-sales measure, define the formula as settled line amounts minus posted line-level refunds. Specify exclusions: test orders, failed settlements, non-AUD currency unless converted under a documented rate, and cancelled lines with no settlement. A delivery fee allocated to lines needs its own allocation rule; adding the order-level fee after a line join counts it once per line. These are modeling decisions before they are SQL decisions.

### Distinguish the clocks

| Clock | Meaning | Typical use |
|---|---|---|
| Event time | When the business activity occurred | Business date and event ordering |
| Source commit time | When the source recorded the change | CDC ordering and source audit |
| Arrival time | When the platform received it | Lateness and ingestion SLA |
| Processing time | When a transform handled it | Run diagnostics |
| Publication time | When consumers could see the result | Data-product freshness |

A correction received on Tuesday for a Sunday sale belongs to Sunday's business date while appearing in Tuesday's ingestion run. Store both timestamps. Sydney daylight-saving transitions mean a local date is not safely derived by adding a fixed UTC offset. Keep UTC instants plus the named business time zone.

## Architecture reading: logical responsibilities before products

The same design can be expressed without Azure services: producers → durable receipt → quality and standardization → modeled facts → governed consumption, with security and observability spanning every stage. Products are selected afterward. ADF is suitable for scheduled coordination and copy; ADLS Gen2 holds landed files; Databricks can transform large or complex datasets into Delta tables; Power BI serves approved metrics. These are illustrative component assignments, not a claim that every workload needs every service.

In the four-page architecture file, page ARCH-001 is the logical lifecycle, ARCH-002 compares ETL and ELT, ARCH-003 separates delivery mode from change capture, and ARCH-004 maps a retail workload onto Azure. Read arrows as data or control dependencies according to their labels. A retry arrow should return to a durable checkpoint, not imply a new business event. The companion PDF must be checked against the editable source before it is published.

### Explain the Azure implementation boundary

The order application remains the system of record for order status. ADF reads a bounded extract using an identity authorized only for required source objects and writes a uniquely identified landing batch. The landing manifest records lower and upper boundaries, row count, schema version, file hashes, and run ID. ADLS permissions restrict raw customer fields; downstream consumers do not receive broad raw access. Databricks validates source versions and builds line-grain tables. Power BI reads an approved serving endpoint or semantic model. Azure Monitor can collect supported platform diagnostics, but business controls such as settlement totals still need explicit checks. Purview discovery or lineage coverage must be tested for each integrated asset and transformation.

Private network access, authorization and encryption solve different problems. A private endpoint changes the network route and DNS requirements; it does not grant data-plane permissions. A managed identity supplies workload credentials; it still needs scoped roles or ACLs. Sensitive fields should be minimized and classified, with access and retention determined by policy. Never put connection secrets in a diagram, repository or notebook.

### Failure and replay walkthrough

Suppose batch B17 contains 10,000 source rows and lands successfully, but the transformation stops after writing 6,000 candidate rows. Restart from B17's manifest rather than moving the source watermark forward. The transform should write to a run-scoped staging area, validate expected keys and totals, and publish an accepted version atomically where the chosen table format supports it. A repeated B17 delivery should leave the accepted row set unchanged. If two records share a business key and version but have different payloads, quarantine both or follow an explicit source-authorized resolution rule; choosing the latest arrival is not a reliable business rule.

The source extract and the downstream commit are not one distributed transaction. Therefore document a recovery invariant: every committed source boundary is represented exactly once in the published table state, and an uncommitted boundary remains replayable. A control table can track batch states such as discovered, landed, validated, published and failed, but state transitions must be checked against the actual files and tables. A successful scheduler status alone does not prove the monetary result.

### Design decisions and tradeoffs

| Decision | Advantage | Cost or risk | Choose when |
|---|---|---|---|
| Keep immutable raw receipts | Enables replay and investigation | Storage, privacy and retention obligations | Corrections or audits matter |
| Transform before landing | Limits sensitive raw exposure | Harder to reprocess lost detail | Policy forbids retaining source payload |
| Schedule daily batch | Simple close boundary and cost control | Higher latency | Consumer accepts next-day data |
| Process events continuously | Faster operational response | Checkpoints, ordering and on-call burden | Freshness requirement justifies it |
| Maintain separate provisional and closed views | Preserves both operational speed and finance reproducibility | Additional definitions and governance | Consumers have distinct close policies |

Evaluate decisions against the Azure Well-Architected pillars: reliability, security, cost optimization, operational excellence and performance efficiency. A service diagram alone is not an architecture specification. Record requirements, data contracts, failure behavior, access boundaries, monitoring signals, rejected alternatives and rollback procedure. The design should be clear enough for an engineer to implement and an operator to recover.

## Practice: review a proposed design

A team proposes a daily extract filtered by `updated_at > last_success_time`, appends every row to a sales fact, and refreshes Power BI when the ADF run turns green. Review it in this order:

1. Confirm the fact grain and how source updates, deletes, refunds and replays are represented.
2. Examine the boundary: equal timestamps can be skipped, and an application timestamp may not expose deletes. Ask whether source CDC or a composite watermark is available.
3. Verify batch landing before acknowledging the boundary. Record a manifest and keep enough source evidence to replay.
4. Replace blind append with a version-aware merge or an immutable event model plus a derived current view.
5. Compare source and target counts at the correct grain, reject count, and settled/refund totals by currency and business date.
6. Publish a tested result and expose published-through time. Trigger an alert if expected files or controls are missing, even when infrastructure activity reports success.

**Expected reasoning:** The proposed job can omit tied or deleted changes, double-count retries, and show an apparently fresh dashboard with incorrect totals. The fix is a contract and state model, not merely a different refresh schedule.

## Common misconceptions and operational questions

- **“Exactly once delivery” means exactly once business effect.** Transport may retry. Define stable event identity and idempotent application of a change.
- **A green pipeline run proves the metric.** It proves only the checks the run actually made. Add business reconciliation and freshness controls.
- **The latest arrival is the latest business version.** Network and batch delays can reorder arrivals. Prefer source commit sequence or an explicit version.
- **Raw data is safe because it is internal.** Raw may contain sensitive fields and needs its own access, retention and audit policy.
- **CDC means real-time processing.** CDC is a capture method; changes can be delivered in scheduled batches.

If a dashboard is stale, inspect the last successful source boundary, landing manifest, transform acceptance and semantic-model refresh separately. If totals changed after close, locate the correction's business date and version, compare old and new accepted states, and follow the finance restatement policy. If costs spike, measure scanned volume, retries and warehouse/cluster uptime before changing service sizes.

## Further official reading (checked 14 November 2026)

- [Azure architecture design specification](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-design-specification): document business goals, design decisions, operations, tests and alternatives.
- [Azure architecture icons](https://learn.microsoft.com/en-us/azure/architecture/icons/): official artwork and usage guidance for Azure diagrams.
- [Modern analytics architecture with Azure Databricks](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-databricks-modern-analytics-architecture): a current solution idea, to be adapted to workload requirements.
