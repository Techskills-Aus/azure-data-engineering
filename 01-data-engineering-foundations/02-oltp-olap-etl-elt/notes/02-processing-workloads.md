# Day 02 · OLTP, OLAP, ETL and ELT

## 1. Start with the two questions

At Harbourline Components, a parts distributor, the dispatch application must reserve stock when an order is confirmed. Meanwhile, operations wants to know which regions account for the most net merchandise sales last month. The first task changes the state of a few current records. The second reads many historical records and combines them according to a definition. This chapter teaches how to choose where these workloads run, how to move data between them, and how to prove that the published result is correct.

Review the [Foundations glossary](../../01-introduction-to-data-engineering/notes/00-glossary.md) if transaction, grain, fact or reconciliation is unfamiliar.

> **Reading guide** — First separate the checkout workload from the reporting workload. Then trace where each pipeline transforms data. Finish by reconciling the results and explaining your architecture choices.

## 2. OLTP protects a business operation

Online transaction processing (OLTP) supports operational actions such as placing an order, posting a payment or reserving stock. A single order might require creating a header, creating its lines and reducing available stock. Use a transaction when those writes must succeed together. If stock is insufficient, roll back the header and lines as well as the reservation attempt.

Atomicity groups changes into one outcome. Consistency means a committed transaction preserves the invariants enforced by the database and the application. Isolation controls how concurrent operations can observe and affect each other. Durability preserves committed changes within the engine's configured guarantees. An atomic transaction alone cannot make a flawed stock calculation correct. Two concurrent buyers can still compete for the last unit unless the reservation design enforces quantity at write time or uses suitable concurrency control.

Operational queries often use indexed keys to retrieve small sets of rows. Normalized tables can keep shared attributes in one place and make updates easier to reason about. Measure transaction latency and concurrent write behavior under representative load. Additional indexes can speed certain reads while increasing storage and write maintenance.

### Walk through a failed reservation

Assume the inventory table shows one unit for SKU P-184. The first order asks for one unit and the next order arrives before the first commit returns. The application can condition its inventory update on available quantity being at least the requested quantity. The winning transaction changes availability from one to zero. The other request checks the affected-row count, detects that the reservation failed and rolls back its order writes. In a real deployment, verify this behavior with simultaneous transactions and confirm how the engine reports lock timeouts or retryable conflicts.

> **Design check** — Give each order submission a stable request identifier so a retry after a lost response can discover an existing committed order. Stock protection and retry protection address different failure modes.

## 3. OLAP answers a question across history

Online analytical processing (OLAP) supports filtering, grouping and aggregating larger collections of data. A regional revenue query may read a month of order lines, group by region and join product attributes for a category breakdown. Its performance depends on the scanned data, selectivity, model shape, and concurrency. Analytical storage can use columnar layouts to read only selected columns and can partition data to skip irrelevant ranges when query predicates and engine behavior permit.

Define the grain before joining. In this scenario the fact is one order line. The order header stores order status and region, and one header may match many lines. An order-level shipping charge would repeat on each joined line. Keep shipping at order grain or distribute it according to a documented rule before reporting it at line grain.

| Decision | OLTP workload | OLAP workload |
|---|---|---|
| Primary responsibility | Commit a valid operational change | Answer a governed analytical question |
| Typical access | Small key-based reads and writes | Larger scans, joins and aggregates |
| What to measure | Transaction latency and contention | Query latency, scan volume and freshness |
| Typical data design | Tables organized around operational entities | Facts and dimensions shaped for analysis |

Separating workloads can protect operational responsiveness and support independent scaling. It also introduces data movement and a freshness boundary. A replica may offload some reads, but a replica alone does not settle analytical grain, business definitions, historical corrections or source reconciliation.

## 4. Separate the workload from the movement pattern

OLTP and OLAP describe what the system is doing. ETL and ELT describe where transformation happens relative to the designated analytical target. An operational SQL Server can feed an analytical target through either pattern. A single platform can also serve different workload types depending on the deployment and design.

### ETL · Extract, transform, load

Read a bounded source input. Parse, standardize, filter or redact it in a processing boundary. Load the approved result into the analytical target. The extract can be staged temporarily within an approved processing boundary. For example, a restricted integration job derives region and line amount while removing free-text order notes before loading the analytics environment. The reporting team receives the data it needs while the raw notes stay in the approved boundary.

Recovery depends on the inputs the organization retains. If a transformation rule was wrong and only transformed output exists, the team may need to re-extract older records. That can be impossible after source history expires. Decide what evidence can be retained, where, and for how long before selecting the path.

### ELT · Extract, load, transform

Read a bounded source input and land an approved raw representation in the analytical platform. Then use that platform's compute to validate and model it. On Azure, an illustrative implementation uses Data Factory to copy into restricted ADLS Gen2 storage and Azure Databricks to transform data into Delta tables. A Databricks SQL warehouse can serve published tables to a Power BI semantic model. Loading an approved raw extract is separate from exposing published data to report users.

ELT is useful when a team needs to reprocess historical inputs or support multiple downstream designs. It also requires careful access, retention, compute and schema controls. If sensitive source fields cannot enter the lake, remove them in an approved boundary and apply the remaining modeling logic after landing. This hybrid uses different boundaries for policy and analytical transformation.

| Design question | ETL choice | ELT choice |
|---|---|---|
| Where do the main transformations run? | Processing layer before target load | Compute associated with the loaded analytical platform |
| What enters the target first? | Approved transformed records | Approved raw records, before curated layers are built |
| How do teams replay? | Use approved staging or repeat the source extract | Reprocess retained inputs within the access policy |
| What limits the design? | Processing capacity and replay evidence | Raw-data policy, target compute and retention |

### Choose a path using concrete constraints

| Constraint | Plausible design | Evidence to ask for |
|---|---|---|
| Raw free-text fields must remain inside the source boundary | Filter or redact before loading the analytical target | Approved field list and a sample of both output schema and values |
| Finance changes classification rules after the period closes | Retain governed historical inputs, then rebuild affected periods under versioned rules | Retention window, input lineage and the allowed restatement process |
| Source load slows checkout | Extract a bounded change range or read from an approved replica where supported | Checkout latency, replication lag and batch completeness |
| Several reporting teams share the same metric | Publish a governed fact and semantic measure with an identified owner | Grain, measure definition and reconciliation totals |

> **Architecture decision** — Document where the approved raw boundary sits before comparing tools. A platform can support both ETL and ELT, so the relevant question is which records each environment may receive and where the required processing runs.

## 5. Calculate and reconcile a concrete result

Order A101 in the North region has a 12,000-cent line with a 2,000-cent discount and a 5,000-cent line with no discount. Order A102 is cancelled and has a 9,000-cent line. Order A103 in the South has a 7,500-cent line with a 500-cent discount. Define this exercise's measure as confirmed merchandise amount after line discounts, excluding cancellations and excluding tax, shipping and refunds. The expected result is North 15,000 cents across two accepted lines and South 7,000 cents across one accepted line.

The first reconciliation is four source lines = three accepted + one cancelled exclusion. The second is 33,500 source gross cents = 24,500 accepted gross cents + 9,000 excluded gross cents. The third is 24,500 accepted gross cents − 2,500 discounts = 22,000 net cents. Comparing net published sales directly to source gross would flag an expected difference without explaining it.

### Design the publication boundary

Capture a stable source range and count its expected records. If order headers and lines can change during extraction, use a consistent source view or a supported change boundary with documented ordering. Validate unique keys and missing references before aggregating. Publish only after reconciliation succeeds, then advance progress according to the recovery design. If publication succeeds and checkpointing fails, retry the same batch using deterministic keys and reconcile its existing publication before reporting success.

### Diagnose a mismatched output

If North reports 24,000 instead of 15,000 cents, filter the published rows back to their order keys. The 9,000-cent difference matches cancelled A102. Confirm whether the source snapshot recorded the cancellation and whether the transform applied the status filter. If a result is exactly twice the expected amount, inspect join cardinality and the number of fact rows per order-line key. If both paths produce the same wrong result, parity was necessary but insufficient. Compare the output against an independently calculated fixture and the documented business rule.

## 6. Guided practice

Run the [local SQL exercise](../sql/retail-processing.sql) as described in the chapter README. The SQL models normalized operational tables and two analytical paths. Both use the same business rule so you can compare results independently of the engine. Read the supplied output before changing the rules. Then mark A102 confirmed before the ETL insert and rebuild both paths. North should become 24,000 cents across three lines, South stays at 7,000 cents, and total net becomes 31,000 cents. Restore the cancellation before comparing with the original result.

For a design exercise, assume free-text order notes may not leave the operational boundary. Identify the allowed columns, define which control totals the destination can calculate, and describe how you would replay a late correction. Your design must identify the last accepted publication and the source bounds used to build it.

## 7. Topic questions with worked answers

### 1. A dashboard runs a 12-month aggregation during checkout hours. What would you measure first?

Compare checkout p95 latency and database CPU, I/O and waits before and during the dashboard query. Check actual query duration and concurrency. A move to separate analytical compute can isolate large scans, but it also creates a replication or extraction delay. Agree whether the dashboard needs seconds, minutes or next-day freshness before selecting an integration path.

### 2. Which workload is a query for one customer's order status?

It typically supports an operational action and reads a small set of records by key, so it fits an OLTP access pattern. The same order status becomes analytical input when a report calculates cancellation rates for every region over a quarter. Classify the workload by the query and purpose, even when the source field is the same.

### 3. A tool extracts records into a temporary folder, masks them, and loads a warehouse. Is this ETL or ELT?

Relative to the warehouse, it is ETL because the masking happens before the designated target receives the rows. A temporary intermediate copy does not change the classification. Identify the target and the transformation boundary before classifying any design.

### 4. Which design would you choose if analysts must reclassify three years of history?

ELT can support recategorization when permitted historical inputs are retained and can be replayed. Confirm the historical keys and category history exist and compute costs are acceptable. An ETL design can also support reprocessing if an approved staging area preserves the necessary evidence. Describe retention and replay explicitly instead of relying on the label.

### 5. Why did a shipping charge double after joining orders to lines?

The charge belongs to the order, while the joined result has one row per line. Order A101 appears twice because it contains two lines, so a header charge appears twice. Aggregate shipping at order grain or allocate it using a documented rule that sums back to the original charge.

### 6. Every source row was copied. Why might reported revenue still be wrong?

Copy counts verify transportation within the selected source scope. Revenue can still be wrong if cancellations are mishandled, a join multiplies facts or a source window cuts through a business day. Verify delivery completeness, accepted grain, business rules and totals as separate checks. The exercise's three count and amount reconciliations show how to isolate those failures.

### 7. Can staging data in ADLS be sufficient evidence that a report is ready?

An accepted delivery tells you that inputs arrived. The report also depends on transformations, reconciliation and the serving refresh. Use a publication record to mark the accepted target version and expose its data-through time. A batch can be ready for transformation while the last accepted report remains unchanged.

### 8. The source invalidates a line after it was reported. What should the pipeline do?

Capture the correction as a new authoritative version or operation. Apply it to the affected business key and recompute the applicable historical period under the reporting policy. Validate the delta against the prior publication, preserve audit evidence and expose the new accepted version. Replaying the correction should preserve the same final balance.

### 9. A transaction commits, but the client times out. Is another submission safe?

The timeout does not reveal whether the database committed. An immediate submission with a new identity can create a second order. Use the original request identifier to look up the committed result or retry through a uniqueness rule on that identifier. Verify that the order, lines and inventory reservation still correspond to exactly one successful request.

### 10. ETL and ELT agree, but their output is 9,000 cents too high. What test is missing?

Both paths may share the same cancellation rule and therefore share the same bug. Check the source status and the independent reconciliation. Four input lines should yield three accepted lines and one cancelled exclusion, with 9,000 gross cents explained by that exclusion. Comparing the paths tests implementation agreement. Comparing each path against a business fixture tests correctness.

## 8. References

- [Microsoft Learn · Online transaction processing](https://learn.microsoft.com/azure/architecture/data-guide/relational-data/online-transaction-processing)
- [Microsoft Learn · Data models and workload choices](https://learn.microsoft.com/azure/architecture/data-guide/technology-choices/understand-data-store-models)
- [Microsoft Learn · ETL and ELT](https://learn.microsoft.com/azure/architecture/data-guide/relational-data/etl)
- [Microsoft Azure Well-Architected Framework · Optimize data performance](https://learn.microsoft.com/azure/well-architected/performance-efficiency/optimize-data-performance)
