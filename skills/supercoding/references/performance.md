# Performance, capacity and on-demand work

## Required: locate the cost first

- Define symptoms and goals: initial content, interaction, throughput, latency, memory, resource cost or build time. For small features, inspect directly introduced risks without mandating full benchmarks.
- Distinguish database work, remote calls, transfer, serialization, application computation, browser rendering and resource loading.
- For dedicated optimization, establish a reproducible baseline: environment, data size, cold/warm state, concurrency, latency distribution, request/query counts, transferred bytes or memory.
- Choose goal-relevant metrics such as p95, query count, initial-render metrics or peak task memory. One local average does not prove production benefit.
- Remove duplicate requests, queries, computation, unnecessary rendering and unused data before adding caching, concurrency or more complex designs.

## Required: bound growth and resources

- Bound lists, batch inputs, concurrency, queues, caches, logs, retries and temporary files, with release policies.
- Batch, paginate or stream large queries and traversal. Confirm no later stage collects the entire result into memory before output.
- Match data structures to access patterns; inspect searches inside loops and repeated traversal. A one-off small collection does not need multiple indexes for theoretical complexity.
- Run independent I/O with controlled concurrency. Choose batching, worker pools or background work for CPU tasks according to the language/runtime; async does not imply CPU parallelism.
- Set concurrency from connection pools, quotas, downstream capacity and memory. Do not start unbounded threads, coroutines or requests.

## Conditional: caching

Cache only reusable data with acceptable staleness and a clear benefit. Answer:

- Does the key include required filters, ordering, versions, user/tenant isolation?
- When does data expire or invalidate, and which reads refresh after writes?
- How is capacity bounded, and when are large objects released?
- Can concurrent misses cause duplicate loads, and are failures incorrectly cached?
- May sensitive data be stored in browser, process-shared or proxy caches?

Do not cache cheap, rarely reused data by default or use indefinite caching to hide slow queries. Verify isolation and post-update correctness when caching changes.

## Conditional: lazy loading and prefetching

Distinguish code loading, data fetching and rendering:

- Load noninitial routes, charts and editors on demand when bundle size and usage justify it, without excessive tiny requests.
- Fetch unopened tabs, drawer details, attachments and tree nodes when used; avoid pointless repeat loads through clear lifecycles.
- Defer long-content rendering while keeping critical initial content, images and actions timely.
- Provide loading, failure and recovery behavior so the first click is never silent.
- Use virtualization for actual DOM/rendering bottlenecks while preserving dynamic row heights, focus, selection and accessibility. It does not replace pagination.
- Prefetch likely next steps within limits, considering transfer cost and invalidation. Do not prefetch every module from the home page.

## Conditional: responsiveness and computation

- Choose debouncing, throttling and batched state updates according to interaction needs, preserving timely feedback.
- Use memoization, computed values and cached functions for actual repeated costs with correct dependencies/invalidation, not mechanically on every function.
- Check costs and framework semantics before addressing repeated full cloning, serialization or unbounded deep watchers on hot paths.
- Adjust image size/compression, dependency weight, duplicate bundles and blocking resources based on analysis; do not rewrite the build system merely to optimize.

## Verify benefits and costs

Compare before/after under similar conditions and verify functionality, data correctness, failure paths and resource peaks. Report speed changes and tradeoffs in memory or complexity. Without a usable baseline or execution, report measures taken and metrics still needed; never invent improvement percentages or claim best performance.
