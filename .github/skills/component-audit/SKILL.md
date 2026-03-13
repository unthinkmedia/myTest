---
name: component-audit
description: >
  Audit page files to find custom UI elements that could be replaced with existing shared
  components from the AzureStorybook library or Fluent UI. Use this skill whenever the user
  asks to "audit components", "find custom components", "check for missing shared components",
  "what components am I not using from storybook", or after building/editing a page to verify
  nothing was re-invented. Also use when the user says "component check", "storybook audit",
  or "what did I build that already exists".
---

# Component Audit

Scan page `.tsx` files for custom HTML/CSS patterns that duplicate functionality already
provided by the **@azure-fluent-storybook/components** shared component library or **Fluent UI v9**. The goal
is to surface every piece of hand-rolled UI that has a ready-made replacement so the
developer can decide whether to swap it in.

## When to run

- After building or significantly editing a page (post-build review step)
- On demand when the user asks to check component coverage
- As part of a broader UI verification pass

## How it works

### Step 1 — Load the component registry

Read the AzureStorybook component registry to get the authoritative list of shared
components and their capabilities. Call `getComponentList` and `getComponentsProps` from
Storybook MCP to get the latest component information.

Also reference the component catalog doc for props and usage patterns:

```
.github/skills/page-builder/references/component-catalog.md
```

### Step 2 — Read the target page file(s)

If the user specifies a file, audit that file. Otherwise, audit all `.tsx` files under
`src/pages/`.

For each file, extract:
1. **Imports** — which `@azure-fluent-storybook/components` and `@fluentui/react-components`
   are already being used
2. **Style definitions** — all keys inside `makeStyles({...})`
3. **JSX markup** — the rendered component tree

### Step 3 — Detect custom UI patterns

Look for these categories of re-invention:

#### A. Custom HTML elements that map to shared components

| Custom pattern | Likely replacement |
|---|---|
| `<button>` with icon + label styled as a card | `CardButton` |
| `<nav>` or `<div>` with list of links/items | `SideNavigation` |
| `<div>` with key-value pairs in two columns | `EssentialsPanel` |
| `<div>` acting as a toolbar with icon buttons | `CommandBar` |
| `<div>` styled as breadcrumbs with `>` separators | `AzureBreadcrumb` |
| `<div>` with title + icon + pin/star/more actions | `PageHeader` / `PageTitleBar` |
| `<div>` styled as tabs with click handlers | `PageTabs` (or Fluent `TabList`) |
| `<div>` styled as a tag/chip/pill | `FilterPill` (or Fluent `Badge`) |
| `<div>` styled as a step wizard | `WizardNav` |
| `<div>` styled as a flyout/panel overlay | `ServiceFlyout` (or Fluent `Dialog`) |
| `<div>` with metric/status card layout | `HealthStatusCard` |
| `<div>` with "no data" illustration + message | `NullState` |
| `<div>` with search box + hero banner | `SearchBanner` |
| `<img>` loading from `public/azure-icons/` directly | `AzureServiceIcon` |

#### B. Custom styles that duplicate Fluent UI capabilities

| Custom style pattern | Likely replacement |
|---|---|
| Hardcoded `color`, `background-color` hex values | Fluent `tokens.*` |
| Hardcoded `font-size`, `font-weight` values | Fluent typography tokens |
| Custom `box-shadow` values | Fluent shadow tokens |
| Custom border-radius values | Fluent `tokens.borderRadius*` |
| Manual `display: grid/flex` for data tables | Fluent `DataGrid` |
| Manual `display: flex` toggle/switch | Fluent `Switch` |
| Custom `<input>` styling | Fluent `Input` / `Field` |
| Custom `<a>` link styling | Fluent `Link` |

#### C. Inline styles on shared components

Look for `style={{...}}` props applied to shared components that override their
built-in styling. These often indicate the component isn't being used correctly, or
that a variant/prop exists for the desired behavior.

### Step 4 — Generate the audit report

Output a structured report in this format:

```
# Component Audit Report — [FileName]

## Summary
- Components from Storybook: N used
- Custom UI patterns found: N
- Potential replacements: N

## Custom Patterns Found

### 1. [Description of custom element]
- **Location:** Lines X–Y
- **What it does:** [brief description]
- **Suggested replacement:** `ComponentName` from `@azure-fluent-storybook/components`
- **Confidence:** High / Medium / Low
- **Notes:** [why this is or isn't a clear swap]

### 2. [Next pattern]
...

## Already Using (✓)
- `AzureGlobalHeader` — top nav
- `CardButton` — service shortcuts
- ...

## Not Applicable
List any Storybook components that exist but aren't relevant for this page type
(e.g., `WizardNav` isn't needed on a home page).
```

### Confidence levels

- **High** — The custom markup is a near-exact replica of what the shared component
  renders. Straightforward swap.
- **Medium** — The custom markup serves the same purpose but has minor differences
  (extra props, different layout). Would require checking the shared component's props
  to confirm feasibility.
- **Low** — The custom markup is in the same "family" but may be intentionally
  different. Flagged for awareness rather than as a hard recommendation.

## Important constraints

- Do NOT modify any files — this skill is read-only / diagnostic
- Do NOT suggest replacements that would lose functionality the custom code has
- Fluent UI v9 components (`@fluentui/react-components`) are also valid — not
  everything needs to come from AzureStorybook
- AzureStorybook wraps Fluent in many cases, so prefer AzureStorybook when both exist
  (e.g., prefer `PageTabs` over raw `TabList` if `PageTabs` covers the use case)
- If a custom component is genuinely novel (no shared equivalent exists), say so
  explicitly and suggest it as a candidate for extraction into AzureStorybook
