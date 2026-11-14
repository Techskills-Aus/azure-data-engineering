# Azure fundamentals | Three banking labs

## 1. Define the landing zone
Identify tenant, subscription, resource group, region, storage account and container. Use a dedicated lab resource group and approved region. Storage is private at the container level. This starter lab assumes public service endpoints with Entra authorization. A production design would constrain network access separately and use managed identities. Have an administrator assign Storage Blob Data Contributor to your CLI identity on the lab account before container creation. Creating a resource does not automatically grant blob data access.

## 2. Land two incremental batches
Run `python code/run.py --output ./generated` from the topic folder. Read generated/validation.json. Open the smoke CSVs first and find a late posting, a replay and a correction. For Azure, sign in with `az login` and export SUBSCRIPTION, RG, ACCOUNT, REGION and DATA=./generated. Run `bash code/landing.sh`. If account creation succeeds but container creation returns 403, wait for RBAC propagation and rerun the container and upload commands only. On a partial upload, inspect the existing blob before retrying. Keep immutable files with batch IDs and verify content hashes before deciding whether an existing name is safe to reuse.

## 3. Query landed data
Open a user database in Synapse serverless SQL using an Entra identity with Storage Blob Data Reader on the source. Replace ACCOUNT in code/query.sql and run it. Compare branch/date totals against generated/branch_daily.csv. The local SQL uses SQLite UPSERT as a behavioral stand-in for incremental serving. The cloud query computes a fresh latest-version projection over immutable inputs, so its scanned bytes grow with history. For production, compact older data into partitioned Parquet and retain raw batches for replay. The sample assumes identical payloads for same-version replays. Reject conflicting versions in a production quality gate.

## Recovery and cleanup
If SQL returns access denied, check Entra login, data-plane role, network path and account name. If counts disagree, compare batch inventories and inspect duplicate versions before applying a correction. For production, update a checkpoint only after validated publication. Delete the dedicated lab resource group with `az group delete --name "$RG"` only if it contains solely your disposable lab resources. Remove any dedicated Synapse workspace separately if it was created outside that group. Local cleanup is removal of the generated directory.
