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

## Knowledge checks with worked answers

### 1. Which timestamps matter when a refund arrives late?

Event time records when the underlying business event occurred. Arrival time records when the platform received its representation. Processing and publication times show when that representation was transformed and exposed. Suppose a sale occurred Monday in Sydney, its refund was issued Tuesday, and the refund reached Azure Wednesday. An event-date refund measure attributes it to Tuesday, while an original-sale restatement measure can adjust Monday under an explicit finance rule. Both can use the same source record. Preserve the separate timestamps and document which measure uses each date.

### 2. How do orchestration and transformation work together?

Azure Data Factory manages when the extraction runs, which source bounds it reads, and whether later activities may start. Databricks applies data rules such as parsing amounts, selecting the accepted version, and calculating net sales. For example, after ADF confirms that all Bronze files belong to a complete batch, it can launch a Databricks job with the batch identifier. The job reports quality counts and publication status. ADF can use those results when deciding whether to mark the batch complete. A green orchestration status is meaningful only when its success criteria include the required downstream checks.

### 3. How do you make retries safe when data was already written?

Keep a stable batch identity tied to the source bounds and a manifest for its immutable inputs. In the target, apply changes using the business key and source version. Reprocessing an already accepted version leaves the accepted state and totals unchanged. If a Gold write succeeded before the completion marker was saved, reconcile the target publication on restart and finish recording completion or safely replay the same batch. A same-key, same-version record whose payload differs belongs in quarantine because the source contract cannot determine which value is correct.

### 4. Where do monitoring and security belong in the architecture?

Each handoff has a different exposure and failure mode. The extraction identity needs read access to approved source objects. The ingestion identity needs write access in the landing area. The serving identity reads curated tables through the SQL endpoint. Monitor elapsed time, source coverage, rejected rows and published-through date so an operational alert can identify the failing stage. Logs should identify runs and policy failures without copying sensitive values into broadly accessible operational records.

### 5. Why is a successful ingestion job insufficient evidence for trusting a sales report?

Ingestion confirms that a read and write operation finished. It cannot establish that the extract covered the expected source window, that retries did not duplicate transactions, or that the sales measure applies the correct discount and refund rules. Validate three boundaries separately. Compare the source control counts against the Bronze manifest, reconcile accepted and quarantined records in Silver, and compare the Gold totals against a control total calculated using the same definitions and reporting period. A run can copy 100% of the rows it read and still miss an entire store when the source filter is wrong.

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
