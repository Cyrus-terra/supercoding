# Async state, concurrency and resource lifetimes

## Required: communicate operation state

Match feedback to the interaction scope instead of covering the whole screen for every request.

| Scenario | Default approach |
| --- | --- |
| Initial main-content load | Main-region loading or a dimensionally stable skeleton |
| Filtering or pagination | Table-local loading; clearly mark retained content as refreshing |
| Save or submit | Pending state on the relevant button, duplicate prevention, success/failure feedback |
| Row action | Row- or action-level state without locking unrelated rows |
| Background refresh | Preserve usable content; do not disguise failure as empty data |
| Independent regions loading concurrently | Independent feedback and failure recovery |
| Background batch job | Submission feedback and, as needed, progress, status or a result entry |

Design empty, error, cancellation and retry states together with loading. Existing patterns may delay short-wait indicators to reduce flicker, but must not hide long-running work.

## Required: define state ownership and finalization

- Give each request or operation an explicit state lifecycle. Prefer the existing request library over duplicate derived state.
- Finalize success, failure, cancellation and disposal paths. `finally` is often appropriate, but an old request's `finally` must not clear a newer request's loading state.
- Multiple in-flight operations cannot arbitrarily share one boolean. Represent concurrency by key, operation instance, count or library-provided state.
- When retaining old data, make its relationship to labels and filters clear. A failure must not silently appear as a successful new query.
- Preserve user input on submission failure. Roll back optimistic updates when needed and communicate the outcome.

## Required: handle races and duplicates

- For latest-criteria reads, use query keys, request versions or equivalent guards to reject stale responses. Also cancel unnecessary requests when supported.
- Preserve stale-write protection even when cancellation fails or is unsupported. Debouncing and throttling do not replace it.
- Prevent duplicate submissions through buttons, Enter and shortcuts. Cross-request deduplication requires server idempotency rather than only disabling a button.
- Use optimistic updates only with explicit rollback and concurrency policies.
- For multiple writers, use business-appropriate versions, locks, atomic operations or transactions rather than relying on client request order.

## Required: give work and resources an endpoint

- Bound concurrency, queues and retries by downstream capacity. Batch large workloads and apply backpressure instead of submitting every promise, thread or coroutine at once.
- Stop unnecessary requests, polling and computation after navigation, criteria changes or cancellation. Release shared work only when its last consumer leaves.
- Release timers, listeners, subscriptions, connections, cursors, file handles, temporary objects and large references according to their lifetimes.
- Prevent duplicate listeners and polls after remounts, reconnects and resumes. Polling needs an interval, failure policy and stop condition.
- Use idiomatic language/framework mechanisms for timeouts, cancellation, process exit and cleanup. Do not swallow cancellation signals.

## Decision contrast

Avoid a global loading boolean finalized by every request: an older completion can hide a newer wait. Prefer operation-owned state and latest-request guards; verify both stale successes and stale failures, even if cancellation is unavailable.

## Key verification

For relevant changes, simulate an older slow request finishing last, two rapid criteria changes, failure, completion after cancellation, double submission and repeated page entry/exit. Check current data, loading, errors, listeners and connection counts. Run only scenarios relevant to the task.
