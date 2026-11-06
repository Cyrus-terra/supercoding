# Styles, accessibility and UI regression

Apply to every page-functionality change, including buttons, filters, columns, validation messages and dialogs without new CSS. Reusing components still requires checking layout.

## Required: match the current page first

- Read neighboring areas and existing components. Identify design tokens, component libraries, styling conventions and supported widths; reuse typography, colors, spacing, density, radii, buttons and forms.
- Preserve visual hierarchy and action priority. New buttons, labels and explanations must not arbitrarily change primary actions or information hierarchy.
- Extend styles only for concrete requirements. Reuse suitable existing styles rather than adding nearly identical hard-coded values.
- Before choosing CSS, fonts or APIs, read project compatibility rules or an available specialist Skill when the browser/platform requires them. Do not change compatibility targets during ordinary business work.

## Required: control impact

- Scope new styles through framework scopes, modules or namespaces. Do not add unscoped `button`, `table`, `input` or component-library class overrides.
- When changing global tokens, resets or shared component styles, inspect relevant consumers and representative pages.
- Prefer public component properties, themes and slots. Scope necessary deep overrides to a specific container, explain non-obvious constraints and avoid unstable internal DOM dependencies.
- Investigate containers, box models, layout and stacking contexts before adding more `!important`, huge z-indexes, negative margins or absolute positioning.
- Fixed dimensions suit explicit design boundaries; content and filter regions need reasonable flexibility. Neither ban fixed sizes everywhere nor stretch everything unconditionally.

## Required: check additions against existing layout each time

Within the actual supported range, check:

1. New and existing actions: alignment, spacing, wrapping, hierarchy and obstruction of existing controls.
2. Forms and filters: labels, inputs, validation, multiline text and dynamic fields for crowding and shifts.
3. Content limits: long text, identifiers, large numbers, zero, missing values and translated copy for overflow.
4. Page sizes: typical and narrowest supported widths, zoom and larger text. Do not redesign for mobile without a mobile target.
5. Overlays: mounting, clipping, stacking, scrolling and focus for dialogs, dropdowns, date pickers and tooltips.
6. States: default, hover, focus, disabled, loading, error, empty and success, avoiding unnecessary shifts.
7. Existing interactions: pagination, fixed columns, sticky regions, scroll containers, shortcuts and navigation.

## Required: preserve basic accessibility

- Use semantic controls and understandable labels. Give icon buttons accessible names; do not communicate state through color alone.
- Preserve keyboard access and visible focus. Use existing dialog/drawer focus, dismissal and restoration behavior.
- Use established accessible patterns for loading, validation and async feedback. Avoid repeated interruptions or unexplained disabled states.
- Follow project contrast and target-size requirements. Respect reduced-motion preferences without unrelated animation dependencies.

## Conditional: performance and visual stability

- Reserve reasonable dimensions for images, skeletons and async regions. Size and format large images for their displayed use.
- Avoid repeated synchronous layout reads/writes during scrolling or animation. Add complex optimizations only for actual bottlenecks.
- Lazy content needs placeholders, error feedback and necessary retries. Keep critical initial text, images and actions timely.

## Decision contrast

Avoid making room for a new filter with an unscoped width override that breaks other pages. Prefer the existing filter layout and local wrapping rules; check the narrowest supported width, long labels, loading and failure/retry through the actual page.

## Verification and evidence

When runtime/browser tools are available, exercise the affected user journey, not just the new widget in isolation: reach it through the existing page, perform the action, observe results and failure/retry feedback, and confirm existing controls still work. Check representative states, inspecting screenshots or existing visual tests. Expand shared-style checks to representative consumers. Distinguish static inspection, current-browser checks and target-environment checks.

Without rendering the page, inspect style scope and layout risks, but state that actual visual verification was not performed. A successful build does not establish visual correctness.
