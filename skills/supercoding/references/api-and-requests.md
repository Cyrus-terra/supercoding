# APIs and requests

## Required: define contracts and data volume

- Specify inputs, necessary fields, responses, errors, authorization, nulls, ordering, and time/money units. Prefer existing contracts.
- Paginate growing lists on the server or use bounded cursors. Limit page size and batch IDs; do not fetch everything and slice it in application memory.
- Return summaries needed for the current list. Fetch details, attachments, large fields and history when actually used.
- Counts can be expensive. Choose exact totals, approximations or `hasMore` according to the interaction, label them accurately and never fabricate totals.
- Make ordering deterministic, adding a unique key when necessary. For frequently changing data, choose snapshots or cursors based on consistency needs rather than assuming offset pagination is always stable.

## Conditional: split or aggregate endpoints

Choose granularity based on usage timing, data volume, change frequency, consistency and failure isolation.

- Separate list summaries from large details and unopened records when appropriate.
- Aggregate statistics that always appear together initially when cost is controlled.
- Do not replace excess fields with dozens of sequential requests. Use bounded batches or server aggregation for related remote reads.
- Keep atomic writes in a trusted server transaction or established consistency protocol; do not replace them with chained frontend writes.
- Compare request count, payload size and query cost. Smaller transfers do not necessarily mean faster queries.

## Required: reuse request infrastructure

Distinguish transport infrastructure from domain APIs. Reuse existing framework loaders, network clients or query libraries instead of building competing infrastructure.

- Centralize authentication, base address, timeouts, normalized errors and necessary tracing in the transport layer; expose cancellation where supported.
- Organize business APIs by domain. Avoid duplicate URLs, authentication and error parsing scattered through pages. Simple scripts should reuse existing clients without mandatory multilayer frameworks.
- Delegate caching, deduplication and refresh to existing mechanisms. Do not maintain competing caches in both pages and request libraries.
- Business APIs return business data or explicit errors by default, without hidden dialogs, navigation, page closing or global loading changes.
- Parse business success using the actual backend contract; HTTP success may not imply business success. Do not catch errors and return empty arrays as fake success.

## Required: control failures and retries

- Set connection or overall timeouts according to the external operation. Confirm whether timeout or cancellation stops underlying execution; do not promise it without evidence.
- Distinguish cancellation, timeout, authentication, validation, authorization and service failure. Avoid duplicate notifications from interceptors and pages.
- When authentication refresh is needed, avoid concurrent refresh storms and terminate failure loops.
- Retry only suitable transient failures, with limits, backoff, jitter and server rate-limit hints as appropriate.
- Retried writes require idempotency. A timeout does not prove the server did not execute the operation.
- Never log access tokens, private parameters or complete sensitive responses.

## Scenario checks

Changing searches: cancel or enforce response versions. Debouncing reduces requests but does not guarantee response order.

Page initialization: run independent reads concurrently and dependent reads in order, within downstream capacity.

Frontend-only scope: without backend authorization or source, explain the need for server pagination. Client-side slicing does not solve an unbounded server query.
