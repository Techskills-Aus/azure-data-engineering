# Data Engineering and Business Glossary

**137 terms for data engineers, data analysts, business analysts and business owners.**

Read the sections in order for a first pass. Start with how a business defines an outcome, then follow how records reach a governed report.

## Business and reporting

| Term | Meaning and use |
|---|---|
| **Business objective** | An outcome the organization wants to achieve, such as reducing dispatch delays. It gives the reporting team a reason to collect and measure data. |
| **Business process** | A repeatable sequence of business activities, such as receiving an order, collecting payment, and shipping goods. |
| **Business owner** | The person accountable for a business outcome or definition, such as the finance lead who approves how revenue is reported. |
| **Business analyst** | A practitioner who translates stakeholder needs and business rules into requirements and acceptance criteria. |
| **Data analyst** | A practitioner who explores data, validates measures and communicates findings that support decisions. |
| **Data engineer** | A practitioner who builds and operates systems that ingest, transform, validate and serve data. |
| **Analytics engineer** | A practitioner who turns source data into tested analytical models and reusable metrics for consumers. |
| **Stakeholder** | A person or group that supplies input, approves decisions, operates the process or relies on its results. |
| **Requirement** | A stated capability or constraint the solution must satisfy. A freshness requirement can specify when yesterday's results must be available. |
| **Acceptance criteria** | Observable conditions for approving a deliverable, such as matching source totals and publishing by 8 a.m. |
| **Business rule** | An agreed instruction for interpreting an event or calculating an outcome. A cancelled order may be excluded from fulfilled sales. |
| **Metric** | A quantitative measure defined by its calculation, unit, scope and time period. Order count requires a clear rule about order identity. |
| **KPI** | A metric explicitly tied to a business objective. On-time dispatch percentage becomes a KPI when the team uses it to track fulfilment performance. |
| **Target** | The desired level of a measure within a stated period, such as 98% on-time dispatch this quarter. |
| **Baseline** | A reference value used to compare later performance, such as the previous quarter's on-time rate. |
| **Variance** | The difference from a reference. Specify the reference and whether the result is expressed in units, percentages or percentage points. |
| **Denominator** | The population against which a rate is calculated. Excluding cancelled orders changes the denominator for an on-time dispatch rate. |
| **Gross sales** | Sales measured before the deductions specified in the reporting policy. Declare which prices, taxes and fees the definition includes. |
| **Net sales** | Gross sales less the deductions specified by the business, such as discounts and returns. Document how tax and late adjustments are handled. |
| **Refund** | A transfer of money back to a customer. A refund can happen on a different date from the sale or physical return. |
| **Business date** | The reporting date assigned under business time-zone and cutoff rules. It can differ from the UTC date of the event. |
| **Financial close** | A controlled period-end process that reconciles and approves results. Later adjustments follow the organization's accounting policy. |
| **Reconciliation** | Comparison of totals or individual records across agreed boundaries to explain differences. Match currencies and time windows before comparing. |
| **Dimension filter** | A selection that limits the population of an analytical result, such as looking only at orders fulfilled by one warehouse. |
| **Dashboard** | A collection of visuals and measures used to monitor or explore outcomes. Its validity depends on the definitions and freshness behind it. |

## Data and source systems

| Term | Meaning and use |
|---|---|
| **Source system** | The application, database or feed that provides data to a downstream consumer. |
| **System of record** | The designated authoritative system for a particular business fact. Different systems can own products, payments and shipments. |
| **ERP** | An enterprise resource planning system that supports coordinated operations such as purchasing, inventory and finance. |
| **CRM** | A customer relationship management system that records interactions such as accounts, sales opportunities and service cases. |
| **OLTP** | Online transaction processing supports frequent operational reads and writes, such as committing a new order and its lines. |
| **OLAP** | Online analytical processing supports analytical queries over many records, such as comparing monthly sales across regions. |
| **Database** | An organized collection of data managed for storage and access. A relational database models data using tables and relationships. |
| **Schema** | The agreed structure of data, including fields, types and constraints. In some databases the word also refers to a namespace for objects. |
| **Table** | A named structure containing rows and columns. Its intended grain explains what each row represents. |
| **Row** | One record in a table. A row in an order-line table represents one item line, even if quantity is greater than one. |
| **Column** | A named field holding the same kind of information across rows, such as currency code or order date. |
| **Data type** | A rule for representing a value and its operations. Decimal amounts, strings and timestamps have different valid values. |
| **Null** | A marker for a missing or unknown value. It has different semantics from zero, false or an empty string. |
| **Primary key** | A field or field combination that uniquely identifies a row within a table. |
| **Foreign key** | A field or field combination referring to an identifier in another table. An enforced constraint can prevent orphan references. |
| **Business key** | An identifier meaningful to the source process, such as order number and line number together. |
| **Surrogate key** | A generated identifier used internally by a model. It can distinguish historical versions of the same business entity. |
| **API** | A defined interface for software interaction. An API contract can specify request parameters, authentication and response shape. |
| **Pagination** | Fetching a collection in multiple responses using pages or continuation tokens. The extractor must follow the contract until the collection is exhausted. |
| **Rate limit** | A service restriction on the frequency or volume of requests. A client should respect retry instructions and avoid losing page progress. |
| **CSV** | A text format for tabular records. Delimiters, quoted values, encoding and date formats must be agreed for reliable parsing. |
| **JSON** | A text representation for values, objects and arrays. Nested structure works well for many APIs and event payloads. |
| **Parquet** | A typed columnar file format often used for analytics. Engines can read selected columns without scanning all fields. |
| **Encoding** | The mapping between text characters and bytes, such as UTF-8. A mismatch can corrupt names or cause parsing failures. |

## Pipeline execution and ingestion

| Term | Meaning and use |
|---|---|
| **Pipeline** | An ordered set of activities that turns source inputs into a defined output with traceable execution and validation. |
| **Ingestion** | Acquiring source data for downstream use. An ingestion design specifies what is read and how completeness is recorded. |
| **Orchestration** | Coordinating schedules, dependencies, parameters, retries and results across activities. |
| **Activity** | One unit of pipeline execution, such as copying a file, running a SQL statement or launching a notebook. |
| **Trigger** | A condition that starts a run, such as a clock schedule or an event indicating arrival of a file. |
| **Dependency** | A condition one step relies on before it can start. Validation may depend on successful creation of a complete landing manifest. |
| **Run ID** | An identifier for a particular execution. A retry can have a new run ID while processing the same logical batch. |
| **Batch ID** | An identifier for a bounded input delivery. Keep it stable when retrying the same intake window. |
| **Manifest** | A record of the files and metadata expected for a delivery, such as counts, checksums and source bounds. |
| **Full load** | Reading an entire source dataset for a defined scope. It may be useful for initialization or small reference tables. |
| **Incremental load** | Reading changes since a saved boundary. The boundary must account for ordering, retries and skipped records. |
| **Watermark** | A value used to delimit progress. An incremental extractor might store the last processed source sequence, while a streaming system may use event-time watermarks for completeness decisions. |
| **Checkpoint** | Durable state that lets work resume from a known position. Its contents depend on the engine and may include offsets and state references. |
| **Offset** | A position in an ordered sequence, such as a position within one stream partition. |
| **CDC** | Change data capture records source changes, potentially including inserts, updates and deletes. Consumers apply them with ordering and retention rules. |
| **Batch processing** | Processing a bounded group as a unit, such as a day's complete extract. |
| **Streaming** | Processing an ongoing sequence of events. The design must handle ordering, delivery retries and late arrival. |
| **Event time** | The time at which the business event occurred according to its source or agreed event contract. |
| **Ingestion time** | The time the platform received or persisted the input. It helps diagnose delays between event and availability. |
| **Late-arriving data** | Data received after the time window in which it was expected to be processed. Decide whether to reopen the period or handle it as an adjustment. |
| **Backfill** | Processing a historical range to populate missing coverage or rebuild it under revised rules. |
| **Replay** | Reprocessing previously captured inputs to recover or verify an output. Replay depends on retained inputs and known processing boundaries. |
| **Idempotency** | Applying the same logical operation again leaves the final business state unchanged. |
| **Retry** | A new attempt at an operation after a failure. Retrying a write requires knowing how repeated effects are prevented. |
| **Exponential backoff** | Increasing the wait between retries after repeated failures, commonly with randomness to spread simultaneous requests. |

## Storage, transformation and modeling

| Term | Meaning and use |
|---|---|
| **Raw landing zone** | A controlled location that retains received payloads and metadata for traceability and replay. |
| **Data lake** | A repository designed to keep structured and less structured data in shared storage for multiple processing engines. |
| **Data warehouse** | A system organized for governed analytical querying over integrated models. |
| **Lakehouse** | An architecture that adds managed analytical table capabilities to lake storage. |
| **Medallion architecture** | A design pattern that organizes data into progressively refined Bronze, Silver and Gold layers. |
| **Bronze** | A layer focused on preserving received source evidence and intake metadata. |
| **Silver** | A layer focused on validated and conformed records with explicit keys and standardized representations. |
| **Gold** | A layer shaped for governed consumption, such as a reconciled sales fact or finance reporting mart. |
| **ETL** | Extract, transform and load. Transformation happens before data is loaded into the designated analytical target. |
| **ELT** | Extract, load and transform. Data lands in the analytical platform before the platform's compute applies transformations. |
| **Transformation** | An operation that changes data structure, representation or meaning, such as parsing dates or converting currency. |
| **Standardization** | Representing equivalent values consistently. Store codes arriving with different capitalization can be mapped to one agreed form. |
| **Deduplication** | Resolving repeated representations of the same intended record. An explicit identity and version policy determines which copies agree. |
| **Upsert** | An operation that inserts a missing key and updates a matching key under specified rules. |
| **Partition** | A subdivision of data used for storage or processing. Date-based partitions can help engines avoid reading irrelevant periods. |
| **Grain** | The meaning of one row. A daily store summary and an order line represent different grains and cannot be summed interchangeably. |
| **Fact table** | A table of observations or business events at a defined grain, often containing numeric measures and dimension references. |
| **Dimension table** | A table of descriptive context used for filtering and grouping, such as product or store. |
| **Star schema** | A model with a central fact table connected to descriptive dimensions at well-defined keys. |
| **Slowly changing dimension** | A dimension whose attributes evolve over time. The design specifies whether to overwrite attributes or preserve their history. |
| **Snapshot** | Data captured as of a point in time or over an agreed period, such as closing inventory at each warehouse. |
| **Semantic model** | A governed representation of relationships, measures and reusable business meaning for analytical consumers. |
| **Data mart** | A curated analytical model for a subject or user group, such as an inventory operations mart. |
| **Join cardinality** | The number of matches expected between rows on each side of a join. Unexpected many-to-many matches can multiply amounts. |

## Quality, governance and operations

| Term | Meaning and use |
|---|---|
| **Data contract** | An agreement about fields, keys, behavior, delivery, ownership and how changes are communicated between producer and consumer. |
| **Schema evolution** | Controlled change to data structure over time. Adding an optional field is usually easier to absorb than changing an existing field's meaning. |
| **Schema drift** | A mismatch between the structure arriving and the structure previously expected. The consumer needs a rule for accepting, rejecting or routing changes. |
| **Completeness** | Coverage of expected records or values. Check whether the expected stores arrived separately from whether existing rows contain required fields. |
| **Validity** | Conformance to accepted ranges, allowed values, formats or constraints. |
| **Uniqueness** | The property that an agreed key identifies no more than one accepted row at its defined grain. |
| **Referential integrity** | A guarantee or quality check that references resolve to valid records, such as each fact's product key resolving to a dimension. |
| **Quarantine** | An isolated location or status for records requiring investigation, with enough context to understand and correct each failure. |
| **Control total** | An independently expected count or amount used to check a delivery or report. |
| **Freshness** | Whether the published data covers the expected period as of an agreed time. A successful run can still expose stale data if its source arrived late. |
| **Latency** | The time between two defined points, such as order creation and availability in the report. |
| **Throughput** | The amount processed per unit of time. State the unit, such as records per second or gigabytes per hour. |
| **SLA** | A formal service-level agreement that defines a commitment and its conditions. |
| **SLO** | A measurable service-level objective for a defined indicator, such as publishing 99% of closes by the agreed deadline over a quarter. |
| **Observability** | The ability to understand pipeline behavior from signals such as logs, metrics, execution identifiers and traces. |
| **Lineage** | Traceability from a downstream field or dataset back to its inputs and transformations. |
| **Data catalog** | An inventory of data assets and metadata that supports discovery, ownership and governance. |
| **Data steward** | A person who supports agreed definitions, quality and governance activities for a data domain. |
| **Data retention** | Rules governing how long data is kept and when it is removed or archived. |
| **PII** | Information that identifies a person directly or can identify them in combination with other information. Apply the applicable classification rules. |
| **Least privilege** | Granting each identity only the permissions needed for its assigned responsibilities. |
| **RBAC** | Role-based access control assigns permissions through roles at defined scopes. |
| **RLS** | Row-level security limits which records a user is allowed to see, such as transactions assigned to the user's region. |
| **Runbook** | An operational guide for detecting, diagnosing and resolving a known condition with actionable steps and ownership. |

## Azure platform vocabulary

| Term | Meaning and use |
|---|---|
| **Azure Data Factory** | A managed data integration service commonly used to orchestrate pipelines and move data between supported systems. |
| **Integration runtime** | The computing infrastructure that Data Factory activities use for data movement, activity dispatch or supported transformations. |
| **Linked service** | A Data Factory connection definition for a data store or compute service. |
| **Data Factory dataset** | A reusable reference describing the data an activity reads or writes, such as a table or file location. |
| **ADLS Gen2** | Azure Blob Storage capabilities for analytics with a hierarchical namespace, including directory-oriented operations and access controls. |
| **Azure Databricks** | A managed data and analytics platform used for workloads such as Spark transformations, Delta processing and SQL serving. |
| **Delta Lake** | A table format and storage layer that uses a transaction log to manage table state over data files. |
| **Databricks SQL warehouse** | Compute that executes SQL workloads and can provide a serving path for analytical clients. |
| **Power BI semantic model** | A Power BI model that provides relationships, measures and security for reports and other consumers. |
| **Microsoft Fabric** | An analytics platform bringing data integration, engineering, warehousing and reporting workloads into a shared experience. |
| **OneLake** | The logical data lake used across Microsoft Fabric workloads and workspaces. |
| **Managed identity** | An identity for supported Azure resources that can obtain Microsoft Entra tokens without application-owned secrets. |
| **Azure Key Vault** | A service for storing and controlling access to secrets, keys and certificates. |
| **Azure Monitor** | A monitoring service that collects and analyzes configured operational signals and can trigger alerts. |
| **Microsoft Purview** | A family of governance, security and compliance capabilities. Catalog and lineage coverage depend on supported sources and configuration. |

## Follow the terms in a retail example

1. A business owner defines net sales and an acceptance criterion for the daily close. The analyst agrees the denominator and the treatment of refunds with finance.
2. The source system records an order line at an event time. Ingestion writes its original payload to Bronze together with a manifest and a batch ID.
3. A version-aware Silver merge applies the change. A replay tests idempotency, and a control total checks the accepted Gold publication.
4. The semantic model exposes an agreed measure. The published-through date shows freshness and lineage lets an operator trace the metric back to the source batch.

[Return to Day 01](../)

**Author** Madhur Mehta (professorofdata)
