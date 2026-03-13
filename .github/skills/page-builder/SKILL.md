---
name: page-builder
description: >
  Build Azure Portal pages from screenshots, descriptions, or design specs using the Pydantic PageSchema pipeline.
  Generates a validated .schema.json and .tsx page component, registers it in App.tsx, and produces a build report
  listing every component used, every component created from scratch, and the decisions made.
  Use this skill whenever the user asks to "create a page", "build a page", "generate a page", "make a page",
  "recreate this portal page", or provides a screenshot of an Azure Portal page and wants it built.
  Also triggers on: "build this", "create this", "make this look like the portal", "page from screenshot".
---

# Page Builder Skill

Build Azure Portal pages using the Pydantic PageSchema pipeline. This skill takes a user's intent (screenshot, description, or spec), produces a `.schema.json` conforming to the `PageSchema` Pydantic model, generates a React `.tsx` component, registers it in `App.tsx`, and finishes with a structured build report.

## Workspace Context

- **Workspace root:** The AzureBuilderPlayground project
- **Python schemas:** `schemas/page.py` (Pydantic models), `schemas/codegen.py` (TSX generator), `schemas/validator.py`, `schemas/loader.py`
- **Pipeline CLI:** `python pipeline.py schema.json` (parse → validate → generate)
- **Pages directory:** `src/pages/` — each page is a `<Name>.tsx` + `<Name>.schema.json` pair
- **App registry:** `src/App.tsx` — import and add to the `pages` record
- **Shared components & themes:** `@azure-fluent-storybook/components` (npm package — installed via `package.json`). Both components and themes are exported from this single package.
- **UI library:** `@fluentui/react-components` + `@fluentui/react-icons`

## Step-by-Step Workflow

Follow these steps in order. Do not skip steps.

### Step 0: Query Storybook MCP (MANDATORY — do this FIRST)

Before writing any component code, you MUST consult Storybook MCP to understand each component's API, variants, best practices, and gotchas:

1. Call `getComponentList` to see all available composed components and templates.
2. Identify which Storybook components match the page you're building (PageHeader, CommandBar, FilterBar, DataGrid, SideNavigation, Azure Container, Resource List Page template, etc.).
3. Call `getComponentsProps` for **every component you plan to use** — read the full Storybook documentation for each one. This tells you the correct props, available variants, do's and don'ts, and usage patterns. This is critical for greenfield builds and when modifying existing designs.
4. Import components **and themes** from `@azure-fluent-storybook/components` — this is a real npm package in the project dependencies. Both components and themes are exported from this single package.
5. **Only** drop to raw `@fluentui/react-components` for elements that have no equivalent in `@azure-fluent-storybook/components`.
6. The Storybook docs often contain helpful information about composition patterns, accessibility, and edge cases — always read them before writing code.

If Storybook MCP is not running, STOP and tell the user:
> "The Storybook MCP server isn't running. Open the Command Palette (`Cmd+Shift+P`), type **MCP: List Servers**, and click **Start** next to **storybook**."

### Step 0.5: Determine the Container (MANDATORY)

Before any other analysis, determine which Container the page needs:

1. **Azure Container** — Default for all Azure Portal pages. Uses `AzureGlobalHeader` + `azureLightTheme`.
2. **SRE Container** — For SRE Portal pages. Uses `SREGlobalHeader`.

Call `getComponentsProps` for the relevant container (`Container/Azure Container` or `Container/SRE Container`) in Storybook to verify you have the latest pattern. The container determines the page shell structure — header, theme, and layout scaffold.

**If unsure, default to Azure Container.** Only use SRE Container when the user explicitly requests an SRE page or the screenshot clearly shows the SRE header.

### Step 1: Analyze the Input

Determine what the user wants to build. Input can be:
- A **screenshot** of an Azure Portal page (most common)
- A **text description** of what the page should look like
- A **reference to an existing page** they want to replicate or modify

Extract these details from the input:
- **Container type (azure or sre)** — determined in Step 0.5
- Page name and resource type
- Whether it has a side navigation panel (resource pages do, browse/create pages don't)
- What's in the command bar (action buttons)
- Whether there's an Essentials accordion (resource overview pages)
- What the main content area shows (table, form, cards, detail sections, or custom)
- Breadcrumb trail

### Step 2: Determine the Layout

Read `references/layout-decision.md` for the layout decision guide.

Apply this rule:
- **Side Panel layout** → The user is viewing a specific deployed resource or service (overview, sub-page, detail)
- **Full Width layout** → Home page, create wizard, marketplace browse, all-resources list

### Step 3: Choose the Content Template

The PageSchema supports 5 content template types. Pick the right one:

| Template | When to Use |
|----------|-------------|
| `list-table` | Data tables, resource lists, browse pages with columns |
| `form` | Create/edit forms with input fields |
| `cards-grid` | Dashboard overviews, KPI cards, service tiles |
| `detail` | Property sheets, overview sections with subsections |
| `custom` | Anything that doesn't fit the above — compose freely |

If the page doesn't fit any standard template (e.g., it has tabs, cards, illustrations, and mixed content like a resource overview "Get started" tab), use `custom` as the template kind in the schema but **build the TSX by hand** — the codegen only handles structured templates.

### Step 4: Build the Schema JSON

Create `src/pages/<PageName>.schema.json` conforming to the `PageSchema` Pydantic model.

Read `references/schema-reference.md` for the full schema structure and field descriptions.
Read `references/fluent-icon-reference.md` for verified Fluent icon names — **never guess icon names**.

The schema answers 6 questions:
1. **Container** — `"azure"` or `"sre"`
2. **Side nav** — `SideNavConfig` with entries (NavItem/NavGroup), defaultSelected, width
3. **Title** — `TitleConfig` with resourceName, pageName, icon, breadcrumbs
4. **Command bar** — `CommandBar` with items (StoryRef-backed buttons)
5. **Template** — One of: `list-table`, `form`, `cards-grid`, `detail`, `custom`
6. **Essentials** — `EssentialsConfig` with key-value fields (or null)

For command bar items, use these StoryRef patterns:
```json
{
  "story": {
    "storyId": "components-button--subtle",
    "instanceId": "<unique-id>",
    "argOverrides": { "label": "Button Text", "icon": "IconName" }
  },
  "isSeparator": false
}
```

**CRITICAL — Fluent Icon Name Validation:**
The `icon` value in `argOverrides` is appended with `20Regular` to form a `@fluentui/react-icons` import (e.g., `"ArrowSync"` → `ArrowSync20Regular`). Fluent icons use **compound names** — simple English words almost never work. Before writing any icon name:

1. **Consult** `references/fluent-icon-reference.md` for verified icon names and common mistakes
2. **Never invent** names that seem logical — e.g., `Preview`, `Feedback`, `Refresh`, `Close`, `Monitor`, `Deploy`, `Dashboard`, `Activity`, `Endpoint`, `Tags` do NOT exist
3. **Use verified alternatives** — e.g., `PreviewLink` (not `Preview`), `PersonFeedback` (not `Feedback`), `ArrowSync` (not `Refresh`), `Dismiss` (not `Close`)
4. The pipeline validates icons against the installed package and **blocks codegen** if any are invalid
    "instanceId": "<unique-id>",
    "argOverrides": { "label": "Button Text", "icon": "IconName" }
  },
  "isSeparator": false
}
```

### Step 5: Generate or Hand-Build the TSX

**For standard templates** (`list-table`, `form`, `cards-grid`, `detail`):
First validate the schema (this catches invalid Fluent icon names **and** missing Azure service icons in `public/azure-icons/`):
```bash
python pipeline.py src/pages/<PageName>.schema.json --validate-only
```
If Fluent icon validation fails, fix the icon names in the schema using the corrections in `references/fluent-icon-reference.md`, then re-validate.

If Azure service icon validation fails (icon name not found in `public/azure-icons/`):
1. **Invoke the `iconcloud-browser` skill** to search IconCloud.design for the missing icon name
2. Download the SVG and save it to `public/azure-icons/<name>.svg` (lowercase, kebab-case)
3. Re-run `--validate-only` to confirm the icon now resolves
4. **Never skip** a missing Azure icon — it produces a broken `<img>` in the rendered page

Once validation passes, generate the TSX:
```bash
python pipeline.py src/pages/<PageName>.schema.json
```

**For custom/complex pages** (resource overviews with tabs, mixed content):
Build the TSX by hand, following the established patterns. Read existing pages in `src/pages/` as references.

Read `references/component-catalog.md` for the full list of available shared components and their props.

When building by hand:
- Import shared components from `@azure-fluent-storybook/components` — NEVER recreate what already exists
- Use `@fluentui/react-components` for standard UI primitives
- Use `makeStyles` + `tokens` for styling (never hardcode colors/fonts)
- Follow the page layout structure from existing pages

### Step 6: Register in App.tsx

Add the new page to `src/App.tsx`:
1. Add an import: `import <PageName> from './pages/<PageName>';`
2. Add to the `pages` record: `'<Display Name>': <PageName>,`

### Step 7: Verify

1. Check for TypeScript errors in the new file
2. Run `npx tsc --noEmit` and confirm no new errors from your page

### Step 8: Build Report

After completing the page, produce a structured build report. This is mandatory — it gives the user visibility into exactly what happened.

**Report format:**

```
## Build Report: <Page Name>

### Files Created
- `src/pages/<Name>.schema.json` — Page schema definition
- `src/pages/<Name>.tsx` — React page component

### Files Modified
- `src/App.tsx` — Registered page as "<Display Name>"

### Shared Components Used
List every component imported from `@azure-fluent-storybook/components`:
- `AzureGlobalHeader` — Top application bar
- `PageHeader` — Title with icon, pin, more-actions
- (etc.)

### Fluent UI Components Used
List every component from `@fluentui/react-components`:
- `DataGrid` — Data table
- `Text` — Typography
- (etc.)

### Fluent Icons Used
- `ArrowSync20Regular` — Refresh action (verified in @fluentui/react-icons)
- (etc. — all icon names must be verified, never invented)

### Custom Components Created
List any UI elements you built from scratch that don't exist in the shared library:
- `ProductionCard` — Checklist card with icon, title, description, status dot
- (etc.)
If none, state: "None — all UI composed from shared components."

### Layout Decisions
- Layout type: Side Panel / Full Width
- Template type: list-table / form / cards-grid / detail / custom
- Rationale: (why this layout and template were chosen)

### Schema Summary (6 Questions)
1. Container: azure / sre
2. Side nav: Yes/No (N items, M groups)
3. Title: "<title string>"
4. Breadcrumbs: Home > ...
5. Template: <kind>
6. Essentials: Yes/No
```

### Step 9: Post-Build Review (MANDATORY)

After the build report is complete, run the **page-review** skill to validate quality.

1. Read the page-review skill at `.github/skills/page-review/SKILL.md`.
2. Execute all three passes against the page you just built:
   - **Pass 1 — Token Audit:** Scan for hardcoded colors, fonts, spacing, shadows, and border radii.
   - **Pass 2 — Component Audit:** Verify Storybook components were used where applicable; justify any Fluent fallbacks.
   - **Pass 3 — Visual Analysis:** Use Playwright to screenshot the rendered page and check layout, icons, alignment, and overall appearance.
3. Present the prioritized action list (High → Medium → Low) to the user.
4. **Fix all High-priority items** before considering the page complete.
5. Medium and Low items should be presented to the user for decision.

Do NOT skip this step. The page is not considered finished until the review passes.

## Important Rules

- **EVERY page MUST use a Container pattern.** Every generated page must be wrapped in a Storybook Container — either `Azure Container` or `SRE Container`. The Container pattern means:
  1. The outermost page `<div>` uses `display: flex; flexDirection: column; height: 100vh; backgroundColor: tokens.colorNeutralBackground1`
  2. The **first child** is always `<AzureGlobalHeader />` (for Azure) or `<SREGlobalHeader />` (for SRE) — never omit the global header
  3. The `FluentProvider` with the correct theme (`azureLightTheme` for Azure, `azureDarkTheme` for dark mode) wraps the app in `src/main.tsx`
  4. Before writing ANY page, call `getComponentsProps` for `Container/Azure Container` or `Container/SRE Container` in Storybook to verify you're following the latest pattern
  5. The `container` field in the schema is **required** — the pipeline will reject schemas without it
  6. For hand-built (custom template) pages, manually verify the Container pattern is present — the codegen handles this automatically for standard templates, but custom pages must follow the same structure
  - **Containers available in Storybook:** `Container/Azure Container`, `Container/SRE Container` — always consult these before building

- **NEVER recreate shared components.** Before building any custom UI element, check if `@azure-fluent-storybook/components` already provides it. Call `getComponentList` from Storybook MCP to verify. Read `references/component-catalog.md`.
- **NEVER hardcode colors or fonts.** Always use Fluent `tokens.*` values.
- **NEVER skip the build report.** The report is the final deliverable alongside the code.
- **Use `makeStyles`** for all styling. No inline CSS objects except for truly dynamic values.
- **Match the exact portal look.** If the user provides a screenshot, replicate it faithfully — icons, text, layout, spacing.
- **Page background is always white** (`tokens.colorNeutralBackground1`). Do not use grey or tinted backgrounds for the page body unless the user explicitly requests dark mode.
- **ALWAYS use the `iconcloud-browser` skill for icons.** When you need to find, search for, or download an icon (Azure service icon, Fluent icon, or any Microsoft icon), invoke the `iconcloud-browser` skill. Do NOT guess icon names, suggest icons from memory, or provide a text-based list of icon suggestions. The skill browses IconCloud.design to find the correct icon with its exact name, collection, and SVG. This applies to page icons, nav icons, command bar icons, and any other icon needed during page building.
