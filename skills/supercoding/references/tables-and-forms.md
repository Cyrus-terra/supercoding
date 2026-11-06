# Tables, filters and forms

## Required: keep list-query semantics consistent

- Paginate, filter and sort growing datasets on the server. Small, explicitly bounded local data may be processed on the client. Do not sort only the current page while implying global ordering.
- Return to a valid page after filter, search or page-size changes according to product behavior. Drive pagination, ordering and filters from clear state; avoid duplicate requests from handlers and watchers.
- Debounce searches when appropriate. Define reset, Enter and immediate-filter behavior, and protect against stale responses.
- Use stable business row keys rather than array indexes for selection, editing and cache state.
- After deleting the final item on the last page, return to a valid page without duplicate refreshes or oscillating page numbers.

## Required: define selection and action scope

- Specify whether selection persists across pages. Distinguish selecting the current page from all filtered results.
- Clear or revalidate selection after criteria changes according to the contract, preventing operations on old result sets.
- Validate permissions, current record states and batch limits. Report partial success, partial failure and recoverable results.
- Give row actions independent pending states; confirm destructive actions where necessary and prevent mutually exclusive operations on the same row.
- Keep permissions, disabled reasons and business state consistent. Hidden frontend buttons do not replace backend authorization.

## Required: readable information and stable layout

- Reuse the project's table component, density, spacing, headers and alignment.
- Format numbers, dates, money and missing values consistently. Preserve valid `0` and `false`; truthiness does not establish absence.
- Wrap or truncate long text with an accessible way to inspect it fully. Size identifier, monetary and action columns for their content.
- Check many filters, long button labels, narrow widths, horizontal scrolling, fixed columns/headers and overlay obstruction.
- Distinguish initial loading, refreshing, no data, no filter matches and failure. Do not use empty states to conceal errors.
- Consider virtualization for measured rendering problems from many rows or complex cells. It does not replace server data limits; preserve keyboard access, dynamic heights and selection.

## Required: complete form data and lifecycles

- Provide timely UI validation and revalidate on the server or trust boundary. Keep validation aligned with API contracts.
- Distinguish create, edit and view modes. Reused dialogs and record changes must not retain stale values, validation or requests.
- Prevent duplicate pending submissions. Preserve input on failure and locate errors by field or region. Refresh relevant data and manage focus after success according to the contract.
- Explicitly convert numbers, booleans, dates, time zones, empty strings and nulls. Do not infer submission formats from display formatting.
- Remote options and dependent fields need loading, errors, dependency resets and stale-response protection. Search or paginate large option sets on demand.
- Warn about unsaved work according to product requirements without adding frequent unsolicited confirmations.

## Conditional: import and export

- Specify whether export covers the current page, selected records or all filtered results, retaining filter and ordering contracts.
- Use background jobs or streaming for large exports according to capacity. Do not download all records into the browser before generating a file.
- Validate import format, size and content; make batch failures traceable. Address spreadsheet formula injection where applicable.
- Follow target-environment requirements for filenames, encoding, downloads and printing. Passing on a development browser is not compatibility evidence.

## Relevant verification

Select checks for pagination after filtering, rapid searches, empty results, failures, last-page deletion, cross-page selection, switching form records and impact on existing layout. Do not mechanically run every scenario.
