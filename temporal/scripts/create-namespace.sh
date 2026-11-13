#!/bin/sh
# Wait for the Temporal server and create the default namespace (idempotent). Runs in the admin-tools image.
# Shell on purpose: it runs inside the temporalio/admin-tools image, which ships no Python.
set -eu

NAMESPACE="${DEFAULT_NAMESPACE:-default}"
ADDRESS="${TEMPORAL_ADDRESS:-temporal:7233}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-30}"
SLEEP_SECONDS="${SLEEP_SECONDS:-3}"

attempt=1
until temporal operator cluster health --address "${ADDRESS}" >/dev/null 2>&1; do
    if [ "${attempt}" -ge "${MAX_ATTEMPTS}" ]; then
        echo "Temporal at ${ADDRESS} not healthy after ${MAX_ATTEMPTS} attempts" >&2
        exit 1
    fi
    echo "Waiting for Temporal (${attempt}/${MAX_ATTEMPTS})..."
    attempt=$((attempt + 1))
    sleep "${SLEEP_SECONDS}"
done

attempt=1
while :; do
    if temporal operator namespace describe -n "${NAMESPACE}" --address "${ADDRESS}" >/dev/null 2>&1; then
        echo "Namespace '${NAMESPACE}' exists"
        exit 0
    fi
    if temporal operator namespace create -n "${NAMESPACE}" --address "${ADDRESS}" >/dev/null 2>&1; then
        echo "Namespace '${NAMESPACE}' created"
        exit 0
    fi
    if [ "${attempt}" -ge "${MAX_ATTEMPTS}" ]; then
        echo "Could not create namespace '${NAMESPACE}'" >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep "${SLEEP_SECONDS}"
done
