# Day 01 | Introduction to Data Engineering — From First Principles to Architecture Decisions

> **Audience:** First-time learners progressing toward professional data engineering design.  
> **Scenario:** A fictional Australian omnichannel retailer.  
> **Prerequisites:** None.  
> **Outcome:** Explain why a pipeline exists, trace a record through it, and critique an Azure reference architecture.

## Learning path: three levels of understanding

| Stage | Learner can explain | Evidence |
|---|---|---|
| 1 — Understand | Why operational data cannot simply become a trustworthy dashboard | Draw a source-to-report flow and explain every stage |
| 2 — Apply | How ingestion, quality, modeling and orchestration work together | Design a daily sales pipeline and describe its data contract |
| 3 — Design | Why architecture includes recovery, access controls, monitoring and trade-offs | Defend choices for a realistic enterprise workload |

## 1. Start with the business problem, not Azure services

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

## 3. Pipeline vocabulary, with exact responsibilities

- **Source system:** An operational system that originates or owns data. It is not necessarily optimized for analytics.
- **Ingestion:** Moving or acquiring source data into the analytical environment. Common methods include files, database extracts, APIs, CDC and event streams.
- **Landing/raw layer:** A replayable copy of source data, with sufficient metadata to trace origin.
- **Transformation:** Cleaning, parsing, joining, enriching, deduplicating or applying business logic.
- **Data model:** An intentional structure that expresses entities, relationships, grain and metrics for consumers.
- **Orchestration:** Coordinating dependencies, schedules, parameters, retries and execution status. It is not the same as doing every transformation itself.
- **Data contract:** Agreed schema, keys, meaning, expected cadence, owner and change-management expectations between producer and consumer.
- **Data quality:** Evidence that data meets agreed fitness-for-use requirements, including completeness, validity, consistency, uniqueness and timeliness.
- **Data lineage:** Traceability from source through transformations to downstream outputs.
- **Idempotency:** Repeating the same logical processing operation does not create duplicate business results.
- **Data product:** A discoverable, governed and usable dataset or service with ownership and a defined purpose.

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

## 10. Knowledge checks

1. Why is a successful ingestion job not enough to trust a sales report?
2. Explain the difference between source event time and ingestion time.
3. What is the difference between orchestration and transformation?
4. Why preserve a raw layer if the final consumer needs only a gold table?
5. When is CDC preferable to a nightly full extract?
6. What does the *grain* of a sales fact mean?
7. How would you prevent double-counting after a retry?
8. Why should security and monitoring appear across the entire architecture?
9. Give one reason to choose a warehouse and one reason to choose a lakehouse.
10. Describe the difference between an architecture diagram and an implementation runbook.

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
