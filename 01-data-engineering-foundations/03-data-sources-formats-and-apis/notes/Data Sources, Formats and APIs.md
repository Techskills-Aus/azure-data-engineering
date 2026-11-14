# Data Sources, Formats and APIs

Module 01 · Day 03

**Author:** Madhur Mehta (professorofdata)

## Source, format and interface

A source owns the data. An interface exposes it. A format represents it. An order might originate in SQL Server, arrive through a REST endpoint as JSON, and be stored in the analytics lake as Parquet. Separating these decisions lets you change the analytics layout without changing the producer contract.

Document the contract before selecting a connector. Name the owner, access route, row grain, key, time zone, refresh window, schema version and reconciliation method. Specify how updates and deletes are represented. A daily delivery schedule does not tell you whether the file is a snapshot or a set of changes.

## Relational extracts

A transaction system maintains current operational state and may limit concurrent reporting queries. Extract only required columns, use an indexed filter where possible, and agree on a consistent snapshot or use a read replica if the owner provides one. Plan an initial full extract and define how later windows capture changes.

For order lines, use (order_id, line_id) as the business key. A watermark on updated_at requires a reliable source timestamp. Use a bounded extraction window and an overlap with deduplication when late visibility is possible. A timestamp filter alone misses hard deletes. Use a source delete feed, change log or periodic snapshot reconciliation.

## File deliveries

A file handoff needs a delivery contract. Agree on the expected path, file naming, encoding, completeness signal and late-file policy. A manifest recording each file, byte count and checksum makes partial deliveries distinguishable from complete ones. Write an immutable landing copy before parsing when replay is required.

Track the producer identity and file checksum separately from the ingestion run ID. On retry, the same delivery can be recognized under a new run. Row-level keys still matter because a reissued file can contain overlapping records or corrected values.

## Delimited text and CSV

CSV is approachable for exports and manual inspection. Specify header presence, delimiter, quoting, encoding and null conventions. Read identifiers as text so 00042 remains 00042. Parse amounts into decimal with an agreed scale, and parse dates according to the agreed date pattern rather than relying on locale inference.

Given the record 00042,"Gurugram, Haryana",1250.50, a delimiter split returns four tokens. A CSV parser returns three fields. Reject malformed rows to a controlled quarantine location and include the file name, row locator and validation reason in the audit record.

## JSON and record grain

JSON preserves nested objects and arrays. A document with one order and three line items represents one order record and three line records after flattening. Keep order measures at order grain. Joining order totals to each line and summing them multiplies the order total by the number of lines.

Distinguish an absent property from an explicit null when the producer uses them differently. A JSON array is one document. Newline-delimited JSON is a sequence of separate JSON values and supports record-oriented reads. Confirm the expected document shape in the connector before production.

## Parquet and analytical reads

Parquet stores columns in a binary layout and carries physical and logical type information. An analytical reader can project only the columns needed for a query. Row-group statistics may also let a compatible reader skip groups that cannot match a filter. Benefits depend on the reader and on how the files were written.

Parquet remains a file format. If you need atomic commits across multiple files, table-level schema rules or versioned snapshots, choose a table format and compatible engine separately. Keep repeated analytics reads in typed files with appropriate file sizes. Excessive tiny files can dominate query planning and listing time.

## Avro and sequential records

Avro object container files carry the writer schema and store records in blocks. A compatible reader schema can interpret older records according to resolution rules, such as supplying a reader default for a newly introduced field. An incompatible type change still needs coordination and often a new contract version.

For an analytics query reading a few fields across many rows, prefer a column-oriented layout when the engine supports it. For a record exchange that usually reads the full record, a row-oriented layout can fit the access pattern. Confirm compatibility at both ends before adopting a format.

## REST pagination

An endpoint can return 100 orders at a time with a next link in the response body. Follow the documented link or cursor exactly and stop at the documented terminal signal. For the Azure Data Factory REST connector, a top-level JSON array does not support its pagination feature. An object containing items and a next link is a suitable shape to evaluate.

Capture page numbers and request identifiers without logging credentials. Test an empty response, a single page, multiple pages and a repeated cursor. If the API lacks a stable snapshot, offset pagination can omit or repeat rows as records change. Use an endpoint snapshot or stable cursor when available and reconcile returned business keys.

## API retries and security

When the API returns HTTP 429, honor a valid Retry-After header where supplied and bound the number and duration of retries. Retry transient failures with backoff and jitter. Handle repeated 401 or 403 responses as an authentication or authorization issue and alert the owner. Keep credentials in a managed secret store or use identity-based authentication where supported.

Store the response together with run ID, request window and page identity, subject to retention and data classification. Advance the durable checkpoint after all pages and downstream validation succeed. A crash before that point may replay data, so make the destination write repeatable by key and version.

## Schema change and validation

Separate additive changes, such as a new optional field, from breaking changes, such as an identifier changing type. Preserve original data where policy permits. Promote new fields to the typed model deliberately. Validate required columns, uniqueness, decimal precision, time zones, allowed values and referential integrity before publishing.

Reconcile at a defined grain and cutoff. Compare input counts to accepted, rejected and suppressed duplicate counts. Use a common currency and scale for monetary totals. Record the batch status and validation totals so operators can compare results after a replay.

## Worked case: order fulfillment

Combine an ERP extract at order-line grain, warehouse status CSV at shipment-event grain and carrier REST JSON at tracking-event grain. Land them separately. Standardize timestamps to UTC, preserve original timestamps for traceability, and map carrier tracking IDs to shipment IDs. Build separate order-line and shipment-event tables before deriving fulfillment measures.

The ERP sends 1,250 records. Eight fail parsing, two are duplicate versions and 1,240 pass to the typed layer. Account for all 1,250 records in the run audit. If a carrier page fails, retain the completed landing pages and withhold the carrier checkpoint. Retry with the same logical window and deduplicate by tracking ID and event ID.

## Practice and glossary

Design a handoff for a daily inventory snapshot, hourly shipment status files and a carrier API. Specify grain, keys, parsing rules, raw landing, retry semantics and one reconciliation metric per source. Test your design against a duplicated file, a renamed source field and a carrier response that contains a repeated cursor.

Grain means what one record represents. A watermark is the saved boundary used to choose a later extraction window. A cursor is a producer-supplied continuation marker. A manifest lists the expected delivery objects and their metadata. Quarantine isolates rejected records for controlled correction and replay.

## References

- [Azure Data Factory Copy activity](https://learn.microsoft.com/en-us/azure/data-factory/copy-activity-overview)

- [Azure Data Factory REST connector](https://learn.microsoft.com/en-us/azure/data-factory/connector-rest)

- [Apache Parquet file format](https://parquet.apache.org/docs/file-format/)

- [Apache Avro specification](https://avro.apache.org/docs/current/specification/)
