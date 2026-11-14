# Day 02 · Interview questions and worked answers

[Return to the chapter](../)

### 1. What is the difference between OLTP and OLAP?

**Definition** — OLTP supports operational actions that read or modify business records. OLAP supports analysis across many records, often over time.

**Reasoning** — Identify the purpose, number of records touched, and performance expectation. Checkout needs responsive, correct changes and safe concurrent writes. Regional sales analysis needs consistent definitions, appropriate grain and efficient aggregation. The same source data can support both purposes.

**Example** — Reserving stock for one order is OLTP. Summing confirmed merchandise sales by region for a quarter is OLAP, even though those sales originated in operational orders.

### 2. Why should order creation and stock reservation be one transaction in this example?

**Definition** — A transaction groups operations under a defined commit or rollback outcome. Atomicity means the grouped changes take effect together.

**Reasoning** — If an order requires reserved stock to be valid, its header and lines should commit only when the reservation succeeds. Concurrency controls still matter. An unconditional stock update can produce the wrong business outcome even when it runs inside a transaction.

**Example** — With one unit left, a conditional update permits one buyer to reserve it. The competing request sees that no row was updated and rolls back its order changes.

### 3. How would you classify a query for one order, and what follow-up might an interviewer ask?

**Definition** — Workload classification describes the purpose and access pattern of an operation.

**Reasoning** — A keyed lookup for a current order supports an operational action. An interviewer might ask whether every read against an operational database counts as OLTP. Evaluate the work the query performs. Historical grouping across thousands of orders has analytical characteristics even when it runs against the operational database.

**Example** — A support agent checks order A101 by ID. A manager then asks for cancellation rates across all regions for a quarter. The two questions use the same status field but demand different work.

### 4. Why might a company separate checkout from historical reporting?

**Definition** — Workload isolation means allocating separate resources or environments to workloads with different operating needs.

**Reasoning** — Large scans and aggregations can compete with small operational reads and writes for compute and I/O. Separate analytical processing can protect checkout responsiveness. It also creates a data movement and freshness obligation. Decide how current the report needs to be before adopting the design.

**Example** — Checkout must respond promptly throughout the day, while finance can accept a validated report next morning. Processing the reporting batch independently supports both goals and makes the publication cutoff explicit.

### 5. What is the difference between ETL and ELT?

**Definition** — ETL extracts, transforms and then loads the designated analytical target. ELT extracts, loads approved input and transforms it within the analytical environment.

**Reasoning** — Identify the target boundary first. Then locate the transformations that make rows suitable for that target. Temporary staging by itself does not settle the classification. Also ask what evidence can be retained for recovery under each approach.

**Example** — Filtering cancellations and calculating net amounts before the analytical target receives the rows is ETL. Loading approved source-shaped rows and applying the same calculation on the analytical platform is ELT.

### 6. When would ETL be a reasonable choice, and when might ELT help?

**Definition** — ETL and ELT are placement choices for transformation relative to the analytical target.

**Reasoning** — ETL helps when certain fields must be excluded or transformed before data crosses an approved boundary. ELT can help when permitted history must be retained for changing rules and repeated analysis. Both choices require explicit source coverage, data quality checks and publication rules.

**Example** — Remove restricted order notes before transferring the extract. If finance later needs to recalculate sales categories, keep the permitted line and product history and run the revised classification on that approved input.

### 7. Why can a join overstate an order-level amount?

**Definition** — Grain defines what one record represents. Join cardinality describes how many records can match between the joined tables.

**Reasoning** — Amounts should be aggregated at the grain where they belong. Joining one order to several lines repeats its order-level fields on every line. Reporting at line grain requires an allocation rule if the measure is fundamentally order-level.

**Example** — A101 has two lines. A 500-cent shipping charge stored on the header appears twice after a direct join. Summing it yields 1,000 cents. Aggregate shipping separately or allocate amounts across the two lines that add up to 500.

### 8. How would you prove the ETL and ELT paths produced a correct result?

**Definition** — Parity checks compare outputs across implementations. Reconciliation tests the outputs against independently expected business totals.

**Reasoning** — Check both row identities and amounts because matching totals can hide offsetting errors. Compare each path with an independent example and explain exclusions. Both paths may share the same faulty filtering logic even if they agree exactly.

**Example** — The exercise starts with four lines and 33,500 gross cents. Exclude one cancelled line worth 9,000 cents, then deduct 2,500 cents of accepted discounts. Expect three distinct lines and 22,000 net cents, split into North 15,000 and South 7,000.

