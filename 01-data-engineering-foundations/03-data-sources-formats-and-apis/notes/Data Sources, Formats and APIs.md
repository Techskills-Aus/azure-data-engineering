# Day 03 · Data Sources, Formats and APIs
**Author:** Madhur Mehta (professorofdata)

## 1. Start with the same order lines

The examples use two order lines from Harbourline Components. The grain is one line per order. The key is (order_id, line_id). Amounts use integer cents in AUD, timestamps in the API use UTC, and identifiers are strings so leading zeros survive ingestion.

| order_id | line_id | sku | qty | net_cents |
| --- | --- | --- | --- | --- |
| 00042 | 1 | P-184 | 2 | 125050 |
| 00042 | 2 | P-205 | 1 | 34950 |

> The two lines reconcile to 160,000 cents (AUD 1,600.00). Use this total to verify every conversion.

## 2. Structured, semi-structured and unstructured data

Structured data follows a defined model with fields, types and constraints. A SQL order-line table can enforce the composite key and require an integer quantity. CSV can represent structured records when a separate contract supplies field types.

Semi-structured data contains keys, tags or other markers, and records can vary in shape or nesting. A JSON order can contain a variable-length lines array. A JSON schema may still impose a strict contract.

Unstructured data lacks a predefined record model for its main content. A delivery photo, a scanned proof-of-delivery PDF or the free text of a complaint are examples. These objects can have structured metadata. Store the original object and extract searchable fields into a separate table.

| Class | Specimen | Ingestion decision |
| --- | --- | --- |
| Structured | SQL order lines with typed columns | Validate keys and types |
| Semi-structured | Order JSON with nested lines | Validate shape and flatten at line grain |
| Unstructured | Delivery photo and scanned receipt | Preserve binary file and extract fields if required |

## 3. CSV for a tabular handoff

CSV is a good fit for interchange with spreadsheet users, a partner export or a small manual audit. Document the encoding, header, field separator, quoting, date representation and null convention. Without a type contract, a reader may infer 00042 as the number 42. Embedded commas and newlines require CSV-aware parsing.

```
order_id,line_id,sku,qty,net_cents
00042,1,P-184,2,125050
00042,2,P-205,1,34950
```

```
orders = (spark.read.option("header", True)
          .schema(order_schema).csv("orders.csv"))
```

> CSV is convenient for inspection and bulk handoffs. Repeated analytical queries usually gain more from a typed columnar format.

## 4. JSON for nested records and APIs

An order-oriented endpoint can return one document per order. Use JSON when nested records, optional properties or application interoperability matter. Write down the differences between missing fields, explicit nulls and empty arrays. For newline-delimited JSON, write one complete document per line. Pretty-printed multiline JSON requires the appropriate reader option.

```
{"order_id":"00042","lines":[
  {"line_id":1,"sku":"P-184","qty":2,"net_cents":125050},
  {"line_id":2,"sku":"P-205","qty":1,"net_cents":34950}
]}
```

```
from pyspark.sql.functions import explode
nested = spark.read.option("multiLine", True).json("order.json")
lines = nested.select("order_id", explode("lines").alias("line"))
orders = lines.select("order_id", "line.*").selectExpr(
    "order_id", "cast(line_id as int) line_id", "sku",
    "cast(qty as int) qty", "cast(net_cents as bigint) net_cents")
```

> Exploding this document produces two rows. Keep order-level totals at order grain to avoid counting them twice.

## 5. Parquet for columnar analytics

Parquet stores values by column within row groups. Use it for lake storage when reports repeatedly select a few fields across many records. Readers can project needed columns and may skip row groups using statistics. Avoid excessive tiny files. Choose partition columns with the query workload and file volume in mind.

| Decoded column | Type | Values in row order |
| --- | --- | --- |
| order_id | string | 00042, 00042 |
| line_id | int32 | 1, 2 |
| sku | string | P-184, P-205 |
| qty | int32 | 2, 1 |
| net_cents | int64 | 125050, 34950 |

```
orders.write.mode("overwrite").parquet("out/orders_parquet")
decoded = spark.read.parquet("out/orders_parquet")
decoded.select("sku", "net_cents").show()
```

> The table shows the decoded values. Parquet is binary and will look like unreadable bytes in a plain text editor.

## 6. Avro for schema-based record exchange

Avro object container files store records in blocks with the writer schema. Choose Avro for record-oriented exchange, event archives or ingestion handoffs when consumers often read the whole record. Some streaming systems use schema registries to carry schema identifiers with individual messages. That wire representation differs from an Avro object container file.

```
{"type":"record","name":"OrderLine","fields":[
  {"name":"order_id","type":"string"},
  {"name":"line_id","type":"int"},
  {"name":"sku","type":"string"},
  {"name":"qty","type":"int"},
  {"name":"net_cents","type":"long"}
]}
```

```
# Decoded record 1 shown as JSON for inspection
{"order_id":"00042","line_id":1,"sku":"P-184",
 "qty":2,"net_cents":125050}
```

```
orders.write.mode("overwrite").format("avro").save("out/orders_avro")
decoded = spark.read.format("avro").load("out/orders_avro")
decoded.orderBy("line_id").show()
```

> In Spark, install the matching spark-avro module if the runtime does not provide it. A reader schema can supply a default for a newly added field when reading older data. Test compatibility before changing an existing field type.

## 7. ORC for compatible warehouse and lake workloads

ORC is a binary columnar format organized into stripes. It stores column statistics and indexes that compatible engines can use to reduce scanning. Consider ORC for established Hive or Spark workloads where the surrounding catalog, tools and downstream readers already support it. Check interoperability when exporting to another engine.

| Decoded stripe view | Illustrative contents |
| --- | --- |
| Row count | 2 |
| order_id column | 00042, 00042 |
| line_id column | 1, 2 |
| net_cents column | 125050, 34950 |
| net_cents range | 34950 through 125050 |

```
orders.write.mode("overwrite").orc("out/orders_orc")
decoded = spark.read.orc("out/orders_orc")
decoded.filter("net_cents > 100000").show()
```

> This filter returns line 1. The two-row example demonstrates correctness. Use larger test data to measure any scan savings.

## 8. REST API for a paged source

REST describes the interface. JSON is the response format in this example. The following endpoint contract returns one row per page and a relative next link. A null next link ends the extract.

```
GET /v1/order-lines?limit=1
{
  "items":[{"order_id":"00042","line_id":1,"sku":"P-184",
            "qty":2,"net_cents":125050}],
  "next":"/v1/order-lines?limit=1&cursor=page2"
}
```

```
GET /v1/order-lines?limit=1&cursor=page2
{
  "items":[{"order_id":"00042","line_id":2,"sku":"P-205",
            "qty":1,"net_cents":34950}],
  "next":null
}
```

In Azure Data Factory, evaluate the REST Copy source with a response shaped as an object and a pagination rule that reads the next URL from the response body. For this contract, the next URL is at $.next. The ADF REST connector does not paginate responses whose top-level structure is an array. Map the items array to line records when writing a tabular sink, or land the raw bodies for replay.

Follow the producer's cursor contract. Cap page count, detect repeated cursors, apply bounded retries for transient errors, and honor Retry-After where supplied. Restrict next requests to the configured trusted API origin. Advance the durable checkpoint only after both pages land and the two rows reconcile.

> If page 2 fails, leave the checkpoint unchanged. Resume or replay under the same logical extraction window and merge by the composite business key.

## 9. Choose the format by who reads it

| Format | Choose when | Check before publishing |
| --- | --- | --- |
| CSV | A partner or analyst needs an easy tabular export | Quoting, nulls, encoding, inferred types |
| JSON | An API sends nested objects or variable properties | Record shape, missing values, array grain |
| Avro | Consumers exchange full typed records and evolve schemas | Writer and reader schema compatibility |
| Parquet | Analysts scan selected columns in a compatible lake engine | File sizes, partitioning, downstream reader |
| ORC | A compatible Hive or Spark estate prefers ORC | Catalog and cross-engine support |

## 10. Run the same-data exercise

```
order_schema = """order_id STRING, line_id INT, sku STRING,
                  qty INT, net_cents BIGINT"""
orders = spark.read.option("header", True).schema(order_schema).csv("orders.csv")
for fmt in ("avro", "parquet", "orc"):
    path = "out/orders_" + fmt
    orders.write.mode("overwrite").format(fmt).save(path)
    result = spark.read.format(fmt).load(path)
    assert result.count() == 2
    assert result.select("order_id", "line_id").distinct().count() == 2
    assert result.selectExpr("sum(net_cents)").first()[0] == 160000
    assert result.where("order_id = '00042'").count() == 2
```

Use a disposable local output directory because overwrite replaces existing outputs. Compare the decoded output with the original table. Try changing order_id to an inferred numeric field and observe why the final assertion matters.

## Source contracts and reconciliation

### Relational extracts

A transaction system maintains current operational state and may limit concurrent reporting queries. Extract only required columns, use an indexed filter where possible, and agree on a consistent snapshot or use a read replica if the owner provides one. Plan an initial full extract and define how later windows capture changes.
For order lines, use (order_id, line_id) as the business key. A watermark on updated_at requires a reliable source timestamp. Use a bounded extraction window and an overlap with deduplication when late visibility is possible. A timestamp filter alone misses hard deletes. Use a source delete feed, change log or periodic snapshot reconciliation.

### File deliveries

A file handoff needs a delivery contract. Agree on the expected path, file naming, encoding, completeness signal and late-file policy. A manifest recording each file, byte count and checksum makes partial deliveries distinguishable from complete ones. Write an immutable landing copy before parsing when replay is required.
Track the producer identity and file checksum separately from the ingestion run ID. On retry, the same delivery can be recognized under a new run. Row-level keys still matter because a reissued file can contain overlapping records or corrected values.

### Schema change and validation

Separate additive changes, such as a new optional field, from breaking changes, such as an identifier changing type. Preserve original data where policy permits. Promote new fields to the typed model deliberately. Validate required columns, uniqueness, decimal precision, time zones, allowed values and referential integrity before publishing.
Reconcile at a defined grain and cutoff. Compare input counts to accepted, rejected and suppressed duplicate counts. Use a common currency and scale for monetary totals. Record the batch status and validation totals so operators can compare results after a replay.

### Worked case: order fulfillment

Combine an ERP extract at order-line grain, warehouse status CSV at shipment-event grain and carrier REST JSON at tracking-event grain. Land them separately. Standardize timestamps to UTC, preserve original timestamps for traceability, and map carrier tracking IDs to shipment IDs. Build separate order-line and shipment-event tables before deriving fulfillment measures.
The ERP sends 1,250 records. Eight fail parsing, two are duplicate versions and 1,240 pass to the typed layer. Account for all 1,250 records in the run audit. If a carrier page fails, retain the completed landing pages and withhold the carrier checkpoint. Retry with the same logical window and deduplicate by tracking ID and event ID.

### Practice and glossary

Design a handoff for a daily inventory snapshot, hourly shipment status files and a carrier API. Specify grain, keys, parsing rules, raw landing, retry semantics and one reconciliation metric per source. Test your design against a duplicated file, a renamed source field and a carrier response that contains a repeated cursor.
Grain means what one record represents. A watermark is the saved boundary used to choose a later extraction window. A cursor is a producer-supplied continuation marker. A manifest lists the expected delivery objects and their metadata. Quarantine isolates rejected records for controlled correction and replay.

## References
- [Azure Data Factory Copy activity](https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-overview)
- [Azure Data Factory REST connector](https://learn.microsoft.com/en-us/azure/data-factory/connector-rest)
- [Apache Parquet file format](https://parquet.apache.org/docs/file-format/)
- [Apache Avro specification](https://avro.apache.org/docs/current/specification/)
- [Apache ORC specification](https://orc.apache.org/specification/ORCv1/)
- [Spark data sources](https://spark.apache.org/docs/latest/sql-data-sources.html)
- [Spark Avro module](https://spark.apache.org/docs/latest/sql-data-sources-avro.html)
