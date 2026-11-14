-- Synapse serverless SQL. Replace ACCOUNT and grant caller Blob Data Reader.
-- Run from a user database using Microsoft Entra authentication.
WITH ranked AS (
 SELECT *, ROW_NUMBER() OVER(PARTITION BY posting_id ORDER BY version DESC, arrival_batch DESC) AS rn
 FROM OPENROWSET(
  BULK 'https://ACCOUNT.blob.core.windows.net/landing/postings/bank-posting-reconciliation-batch-*.csv',
  FORMAT='CSV', PARSER_VERSION='2.0', HEADER_ROW=TRUE
 ) WITH (posting_id BIGINT, account_id BIGINT, branch VARCHAR(2),
  business_date DATE, amount_cents BIGINT, version INT, arrival_batch INT) AS src
)
SELECT branch,business_date,COUNT_BIG(*) AS posting_count,SUM(amount_cents) AS net_cents
FROM ranked WHERE rn=1 GROUP BY branch,business_date ORDER BY branch,business_date;
