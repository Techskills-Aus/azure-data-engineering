#!/usr/bin/env bash
set -euo pipefail
: "${SUBSCRIPTION:?Set approved subscription ID}"
: "${RG:?Set dedicated lab resource group name}"
: "${ACCOUNT:?Set unique lowercase storage account name}"
: "${REGION:?Set an approved Azure region}"
: "${DATA:?Set path to generated CSV files}"
az account set --subscription "$SUBSCRIPTION"
az group create --name "$RG" --location "$REGION"
az storage account create -g "$RG" -n "$ACCOUNT" -l "$REGION" --sku Standard_LRS --kind StorageV2 --https-only true --allow-blob-public-access false --allow-shared-key-access false
# Before running this section, have an authorized administrator grant the signed-in
# identity Storage Blob Data Contributor on this account. Allow propagation.
az storage container create --account-name "$ACCOUNT" --name landing --auth-mode login
for batch in 01 02; do
  az storage blob upload --account-name "$ACCOUNT" --container-name landing --name "postings/batch_$batch.csv" --file "$DATA/batch_$batch.csv" --auth-mode login --overwrite false
done
az storage blob list --account-name "$ACCOUNT" --container-name landing --prefix postings/ --auth-mode login --query '[].name' -o tsv
