# Backend services, data access and background jobs

## Required: inspect access volume first

- Trace query counts, returned rows, scanned volume and remote calls. Avoid per-record database/service calls in loops that create N+1 behavior.
- Fetch necessary fields in reasonable batches with bounded parameters. Use parameterized queries or safe ORM operations, never interpolated user input.
- Paginate growing lists at the database/source. Assess cursors, indexes or product changes for costly deep pagination, counts and broad sorting.
- Choose indexes from filters, joins, ordering and query plans, accounting for write/storage cost. Do not change production indexes without authorization and an appropriate environment.
- Prefer existing monitoring, slow-query logs and query plans in safe environments. Do not run unknown expensive production analysis to prove a guess.

## Required: keep consistency and authorization at trusted boundaries

- Validate identity, permissions, ownership and tenant isolation on the server rather than trusting hidden fields or disabled controls.
- Restrict writable fields against arbitrary overwrites. Validate external input format, range, size and required business conditions.
- Use necessary transactions for atomic business operations, defining commit, rollback and conflicts. Keep transactions short and avoid waiting on slow external calls while holding locks.
- A local transaction does not cover all cross-service side effects. Reuse established idempotency, compensation, messaging and consistency strategies without introducing unsupported distributed architectures.
- Handle retries, concurrent updates, duplicate messages and callbacks according to business needs. Make post-timeout state queryable or reconcilable.
- Check other callers, existing data and deployment order when changing API fields or database schemas. Compilation does not replace migration verification.

## Conditional: background and batch processing

- Use background jobs or streaming for lengthy exports, imports and computation according to capacity. Define job ownership and result permissions.
- Provide necessary states, timeouts, cancellation, failure reasons and cleanup. Bound retries and make them idempotent.
- Choose transaction batches, checkpoints and resumption according to actual rerun cost. Small scripts do not automatically need queues.
- Bound queue capacity and concurrency, apply backpressure and isolate poison messages through existing mechanisms rather than blocking/retrying indefinitely.
- Process large files in chunks, limit upload/decompression size and release files and temporary resources promptly.
- Account for reentrancy, overlapping runs and multiple deployment instances in scheduled jobs. Choose scheduling or locking according to task semantics.

## Required: diagnose without excessive logging

- Preserve useful context for important failures through existing correlation IDs, structured logs and monitoring. Do not log full large objects for every record.
- Exclude credentials, private fields and raw sensitive data. Redact and bound logs/traces.
- Distinguish validation, authorization, dependency timeouts and internal errors. Do not expose internal stacks externally.
- Reuse connection pools, clients and resource-management conventions. Do not create a connection for every record or enlarge pools without bounds.

## Verification signals

Select checks for pagination volume, query counts, rollback, isolation, repeated execution and concurrent conflicts. Data migrations and production actions also follow project authorization and release constraints; this Skill does not authorize them.
