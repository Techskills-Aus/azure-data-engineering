# Introduction to Data Engineering and the Data Lifecycle

## Learning goals
Trace an order from a source application to a governed metric. Define the grain, contract, and freshness of the output. Explain how a pipeline recovers from duplicate deliveries, late corrections, and failed publication.

## Begin with the decision
At Southbank Retail, an Australian retailer, finance closes daily online sales and fulfilment managers monitor paid orders awaiting dispatch. Finance needs reproducible totals. Fulfilment needs fresher, provisional counts. A pipeline is the repeatable process that moves, validates and transforms source records into a trustworthy data product. A data product has an owner, consumers, a contract and measurable service expectations.

Think of a parcel depot. A label identifies the parcel, a receiving log preserves the handoff, and a sorting rule determines its destination. In a pipeline, those responsibilities translate to a stable key, immutable receipts, and tested transformations. A tracking update may arrive twice. Counting notifications as parcels inflates the result.

## Establish the contract before ingesting
The order application owns order status and item prices. The payment processor owns settlement, and the warehouse system owns dispatch events. Keep each separately accountable. For the sales mart, use one row per order line, identified by (order_id, line_id), with version supplied by the source. Include currency, source event timestamp, arrival timestamp and operation. Document how nulls and deletions are represented. Treat amounts as AUD cents and derive the reporting date in Australia/Sydney, including daylight saving.

| Responsibility | Control | Evidence |
|---|---|---|
| Source owner | Stable keys and ordered versions | Contract and sample events |
| Platform engineer | Durable capture and reproducible runs | Batch hashes and run manifest |
| Analytics engineer | Correct grain and reconciled measures | Unique-key and control-total checks |
| Business owner | Metric meaning and freshness target | Approved definitions and close policy |

## Follow one order through the lifecycle
1. Define the metric and publish time. Daily sales are the sum of settled line amounts net of refunds, with exclusions documented. The report covers the previous Sydney business day.
2. Extract bounded source changes. Capture the lower and upper source offsets. Land files and a manifest with batch ID, offsets, schema version and observed counts.
3. Preserve the receipt. Keep source payloads in a restricted raw zone and record arrival time. This enables replay when a transform fails.
4. Standardise and validate. Parse amounts and timestamps. Compare keys and versions, remove exact repeated deliveries, and quarantine conflicting same-version payloads.
5. Model and reconcile. Build a line-grain fact and join stable product and date dimensions. Aggregate by the agreed business date. Compare totals by source and currency before publication.
6. Serve and operate. Expose an approved semantic model, capture publication time, and alert on stale outputs or anomalous rejects. Retain lineage from the report to input batches.

## Work through a close correction
Order AU-104 has two settled lines, AUD 89.00 and AUD 31.00. A repeat delivery of the first line would inflate the naive total to AUD 209.00. The same key and version represent a replay, so the first accepted close is AUD 120.00. A newer version corrects the second line to AUD 25.00 and the revised close is AUD 114.00. Preserve both close versions if finance requires reproducibility. If refunds are supplied as separate economic events, keep their own refund keys and subtract them once. A correction and a distinct refund have different identities.

## Choose processing by workload
| Choice | Best fit | Design cost |
|---|---|---|
| Scheduled batch | Close, snapshots, explicit backfills | Freshness bounded by schedule and runtime |
| Streaming | Operational response within seconds or minutes | Checkpoints, event-time policy and incident recovery |
| Source CDC | Inserts, updates and deletes with source ordering | Retention and restart offsets must be managed |
| ETL | Transform or remove fields before target load | Reprocessing depends on available source evidence |
| ELT | Keep a raw record and transform in the platform | Raw access, retention and compute need controls |

CDC captures changes. Batch and streaming describe how changes are delivered or processed. A pipeline can process CDC in batches. A timestamp watermark may miss deletes or ties unless the source contract and query boundary handle them explicitly.

## Map the design to Azure
Azure Data Factory coordinates scheduled extraction and writes append-only landing batches to Azure Data Lake Storage Gen2. Azure Databricks reads those batches, validates and reconciles line versions, and writes curated Delta tables. Power BI reads the serving model through a configured SQL endpoint. The supplied architecture is a reference design. Its identity, networking and deployment choices require validation in the target tenant.

Use separate identities for ingestion, transformation and consumption. Scope write permissions to the output paths each role owns. Define network access independently from authorization, including DNS when private endpoints are selected. Azure Monitor receives diagnostics where enabled. Microsoft Purview can catalog assets and lineage where supported and configured. Audit the lineage coverage rather than assuming all transformations are automatically mapped.

## Decide what happens on failure
If the orchestrator retries after storage has accepted a file, compare batch identity and content before reusing it. If a quality gate fails, preserve the last published close, quarantine the bad data and alert the owner. Commit the checkpoint after successful validated publication, or make publication and replay idempotent across a checkpoint failure. Replaying the same input range must preserve row counts and totals. A dashboard refresh alone cannot confirm this.

## Review questions with worked answers

### 1. How do event time, ingestion time and business date differ?

**Definition** — Event time describes when an event happened. Ingestion time describes when the platform received it. Business date applies the organization's reporting calendar and cutoff.

**Reasoning** — Keep these values separately because they answer different questions. Arrival time diagnoses delivery delay. Reporting date determines the period affected under the business rule. Choosing arrival date by default can shift late transactions into the wrong day.

**Example** — An order placed Monday in Sydney arrives Tuesday. It counts on Monday under an event-date sales definition, while the operations team records its Tuesday arrival and investigates the delay.

### 2. How are orchestration and transformation different?

**Definition** — Orchestration coordinates the order and conditions of work. Transformation applies rules that reshape or interpret the records.

**Reasoning** — An orchestration step can wait for a complete input manifest and launch validation. The transformation checks keys, standardizes values and calculates amounts. A failed validation must be visible to orchestration so the next step can wait and the previous publication can remain available.

**Example** — The intake finishes copying a retail batch, but validation finds an invalid order-line key. The workflow records the failed quality check and withholds publication while the affected records are investigated.

### 3. What makes a pipeline retry idempotent?

**Definition** — A processing operation is idempotent when applying the same logical input again leaves the accepted business state unchanged.

**Reasoning** — Use a stable identity for the delivered batch and a stable key and version for the business record. Reapplying an accepted version leaves its amount unchanged. If identical keys and versions carry conflicting values, investigate the source contract before choosing a result.

**Example** — The AUD 89 line of AU-104 arrives twice. Both receipts can remain available for audit, but the accepted sales fact counts the line once. A later authoritative version of a different line legitimately changes the total.

### 4. How can you tell whether a published result is ready?

**Definition** — Publication is the handoff of a validated result to its consumers. Reconciliation compares results against agreed independent checks.

**Reasoning** — Check the expected input coverage, explain how records were accepted or excluded, and compare the published amount against a control total with the same scope. Verify the freshness of the result consumers can see. A completed file copy provides evidence for only one stage.

**Example** — Two accepted lines total AUD 120 after removing a repeated delivery. A newer version adjusts one line by AUD 6. The revised total is AUD 114, and the previous and revised amounts can be traced to their source batches.

### 5. What should a data contract say about keys and missing fields?

**Definition** — A data contract records the structure, business meaning and delivery expectations shared between a producer and its consumers.

**Reasoning** — Document required identifiers, how versions are ordered, and whether missing fields are allowed. Specify the action when an input breaks the contract. Rejecting or isolating the affected record preserves the evidence needed to resolve the failure.

**Example** — An order line arrives without a line ID. The team cannot determine whether it is a new sale or a correction. The input is isolated with its batch ID and a rejection reason so the source owner can address it.

## Glossary
**Grain** means what one row represents. **Watermark** is a boundary used to resume incremental processing. **Lineage** is traceability through transformations. **Semantic model** defines governed business measures and relationships for consumption. **Quarantine** isolates suspect records for review. **Freshness** measures how current the published data is relative to an agreed business time.

## References
- [Microsoft Azure Databricks modern analytics architecture](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-databricks-modern-analytics-architecture)
- [Azure Data Factory introduction](https://learn.microsoft.com/en-us/azure/data-factory/introduction)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)

## Architecture reading guide
- ARCH-001 | Data lifecycle | architecture PDF page 1.
- ARCH-002 | ETL and ELT | architecture PDF page 2.
- ARCH-003 | Batch, streaming and CDC | architecture PDF page 3.
- ARCH-004 | Azure retail architecture | architecture PDF page 4.
