# Day 01 · Interview questions and worked answers

[Return to the chapter](../)

### 1. What does a data engineer do in the data lifecycle?

**Definition** — Data engineering is the work of building and operating reliable systems that turn source records into usable data.

**Reasoning** — Start by agreeing what the consumer needs and which system owns each source fact. Design a repeatable path that captures inputs, preserves evidence, validates records and publishes a defined result. Operations continues after publication because inputs can arrive late and rules can change.

**Example** — A retail engineer captures order lines, checks missing keys and publishes daily sales by store. A business owner approves the measure, while the engineer makes it reproducible and exposes its freshness.

### 2. How do event time, ingestion time and business date differ?

**Definition** — Event time describes when an event happened. Ingestion time describes when the platform received it. Business date applies the organization's reporting calendar and cutoff.

**Reasoning** — Keep these values separately because they answer different questions. Arrival time diagnoses delivery delay. Reporting date determines the period affected under the business rule. Choosing arrival date by default can shift late transactions into the wrong day.

**Example** — An order placed Monday in Sydney arrives Tuesday. It counts on Monday under an event-date sales definition, while the operations team records its Tuesday arrival and investigates the delay.

### 3. Why define grain before transforming sales?

**Definition** — Grain states what one output row represents.

**Reasoning** — Write the grain in business language and find the key that enforces it. Check uniqueness at that grain after joins. When a related process has multiple records for the same key, join only after aggregating to the required grain or model it separately.

**Example** — A sales fact holds one row per order line. If a line ships in two parcels, joining parcel records directly produces two rows and repeats the line amount. A separate shipment table can preserve both parcel records without inflating sales.

### 4. Why preserve original source records?

**Definition** — A raw layer retains the received payload and enough metadata to trace and replay it.

**Reasoning** — Preserve which batch delivered the record, when it arrived, and how it was interpreted. When transformation logic changes, support can identify the affected inputs and rebuild the corresponding output. The required retention period depends on how far back recovery must work.

**Example** — If a date parser assigns a Sydney sale to the wrong day, the original timestamp allows the team to recompute the business date and reconcile the changed daily totals.

### 5. How are orchestration and transformation different?

**Definition** — Orchestration coordinates the order and conditions of work. Transformation applies rules that reshape or interpret the records.

**Reasoning** — An orchestration step can wait for a complete input manifest and launch validation. The transformation checks keys, standardizes values and calculates amounts. A failed validation must be visible to orchestration so the next step can wait and the previous publication can remain available.

**Example** — The intake finishes copying a retail batch, but validation finds an invalid order-line key. The workflow records the failed quality check and withholds publication while the affected records are investigated.

### 6. What makes a pipeline retry idempotent?

**Definition** — A processing operation is idempotent when applying the same logical input again leaves the accepted business state unchanged.

**Reasoning** — Use a stable identity for the delivered batch and a stable key and version for the business record. Reapplying an accepted version leaves its amount unchanged. If identical keys and versions carry conflicting values, investigate the source contract before choosing a result.

**Example** — The AUD 89 line of AU-104 arrives twice. Both receipts can remain available for audit, but the accepted sales fact counts the line once. A later authoritative version of a different line legitimately changes the total.

### 7. How can you tell whether a published result is ready?

**Definition** — Publication is the handoff of a validated result to its consumers. Reconciliation compares results against agreed independent checks.

**Reasoning** — Check the expected input coverage, explain how records were accepted or excluded, and compare the published amount against a control total with the same scope. Verify the freshness of the result consumers can see. A completed file copy provides evidence for only one stage.

**Example** — Two accepted lines total AUD 120 after removing a repeated delivery. A newer version adjusts one line by AUD 6. The revised total is AUD 114, and the previous and revised amounts can be traced to their source batches.

### 8. What should a data contract say about keys and missing fields?

**Definition** — A data contract records the structure, business meaning and delivery expectations shared between a producer and its consumers.

**Reasoning** — Document required identifiers, how versions are ordered, and whether missing fields are allowed. Specify the action when an input breaks the contract. Rejecting or isolating the affected record preserves the evidence needed to resolve the failure.

**Example** — An order line arrives without a line ID. The team cannot determine whether it is a new sale or a correction. The input is isolated with its batch ID and a rejection reason so the source owner can address it.

