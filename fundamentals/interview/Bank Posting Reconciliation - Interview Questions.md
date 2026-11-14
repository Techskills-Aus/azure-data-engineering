# Azure fundamentals | Interview questions

1. A developer created a storage account but cannot upload. Why? Management-plane rights and blob data-plane rights are separate. Follow-up: scope the upload role to the account or an existing container and check RBAC propagation.
2. A bank asks for five-minute freshness. Is streaming required? Compare source arrival patterns, latency targets, replay needs and operating cost. Five-minute micro-batches may meet the requirement. Follow-up: event-time late arrivals need a policy regardless of ingestion mode.
3. How can a replay be harmless? Retain immutable delivery IDs, use a stable posting key and apply only authoritative newer versions. Follow-up: quarantine conflicting same-version payloads.
4. What drives serverless SQL costs here? Bytes processed by the workload. Follow-up: limit file scope and use partitioned columnar files for repeated queries.
5. Does a private container imply a private endpoint? No. Data authorization and network reachability are separate controls. Follow-up: test DNS and routing from the execution environment as well as RBAC.
