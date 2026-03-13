---
name: page-review
description: >
  Post-build review and quality gate for generated pages. Audits token usage (no hardcoded colors,
  fonts, or spacing), validates that Storybook components were used where applicable (with justification
  for Fluent fallbacks), and runs a Playwright visual analysis to verify layout, icons, and overall
  appearance. Produces a prioritized action list (High / Medium / Low).
  Use this skill after building or editing a page, or when the user asks to "review my page",
  "check my page", "audit my build", "run quality check", "verify the page", or "visual review".
  Also triggers on: "does it look right", "check for hardcoded values", "token audit", "QA this".
---

# Page Review Skill

Post-build quality gate that runs three audit passes on a generated page and produces a single prioritized action list. This skill is invoked automatically at the end of the page-builder pipeline (after Step 8: Build Report) and can also be run independently on any existing page.

## When to Run

- **Automatically** — as the final step of the page-builder skill after a page is generated
- **On demand** — when the user asks to review, audit, or QA a page
- **After edits** — when existing pages are modified and need re-validation

## Inputs

- **Target file(s):** One or more `.tsx` page files to review. If not specified, review the most recently created/modified page in `src/main/` or `src/pages/`.
- **Schema file (optional):** The corresponding `.schema.json` if available, used to cross-check intent vs. output.

## Three-Pass Review

Execute all three passes in order. Each pass produces findings that feed into the final prioritized report.

---

### Pass 1: Token & Hardcoded Value Audit

Scan the target `.tsx` file(s) and any associated style files for hardcoded values that should use Fluent design tokens.

#### What to flag

| Category | Violation Pattern | Expected Fix |
|----------|------------------|--------------|
| **Colors** | Any hex value (`#fff`, `#1a1a1a`, `#0078d4`), `rgb()`, `rgba()`, `hsl()`, named CSS colors (`red`, `white`, `grey`) | Replace with `tokens.colorNeutral*`, `tokens.colorBrand*`, `tokens.colorPalette*`, etc. |
| **Font sizes** | Hardcoded `fontSize: "14px"`, `font-size: 12px`, `1rem`, `0.875em` | Replace with `tokens.fontSizeBase*` (200, 300, 400, 500, 600, 700) |
| **Font weights** | Hardcoded `fontWeight: 600`, `font-weight: bold` | Replace with `tokens.fontWeightRegular`, `tokens.fontWeightSemibold`, `tokens.fontWeightBold` |
| **Font families** | Hardcoded `fontFamily: "Segoe UI"`, `font-family: sans-serif` | Replace with `tokens.fontFamilyBase`, `tokens.fontFamilyMonospace`, `tokens.fontFamilyNumeric` |
| **Spacing** | Hardcoded `padding: "8px"`, `margin: 16px`, `gap: "12px"` — any px/rem/em literal | Replace with Fluent spacing tokens (`tokens.spacingHorizontalS`, `tokens.spacingVerticalM`, etc.) or established spacing scale (4/8/12/16/20/24/32px) |
| **Border radius** | Hardcoded `borderRadius: "4px"`, `border-radius: 8px` | Replace with `tokens.borderRadiusSmall`, `tokens.borderRadiusMedium`, `tokens.borderRadiusLarge`, etc. |
| **Shadows** | Hardcoded `boxShadow: "0 2px 4px..."` | Replace with `tokens.shadow2`, `tokens.shadow4`, `tokens.shadow8`, etc. |
| **Line heights** | Hardcoded `lineHeight: "20px"`, `1.5` | Replace with `tokens.lineHeightBase*` |
| **Z-index** | Hardcoded `zIndex: 1000` | Use Fluent layer utilities or document the reason |

#### How to scan

1. Read the full `.tsx` file content.
2. Search for regex patterns:
   - `#[0-9a-fA-F]{3,8}` — hex colors
   - `rgb\(|rgba\(|hsl\(|hsla\(` — color functions
   - `(?:fontSize|font-size)\s*[:=]\s*["']?\d+` — hardcoded font sizes
   - `(?:fontWeight|font-weight)\s*[:=]\s*["']?\d+|bold|normal` — hardcoded weights
   - `(?:padding|margin|gap|top|left|right|bottom|width|height)\s*[:=]\s*["']?\d+px` — hardcoded spacing
   - `(?:borderRadius|border-radius)\s*[:=]\s*["']?\d+` — hardcoded radius
   - `(?:boxShadow|box-shadow)\s*[:=]` — hardcoded shadows
3. For each match, record the line number, the value found, and the suggested token replacement.

#### Exceptions (do NOT flag these)

- `"100%"`, `"auto"`, `"0"` — these are layout values, not design tokens
- Values inside comments
- Values in `calc()` expressions that combine tokens with layout math
- `"1px"` for borders — `tokens.strokeWidthThin` exists but `1px` is acceptable
- Pixel values for `maxWidth`, `minWidth`, `maxHeight`, `minHeight` when they represent layout constraints (e.g., `maxWidth: "1200px"` for a container)
- Icon size props like `fontSize={20}` on Fluent icon components — these are icon size conventions, not design token candidates

---

### Pass 2: Component Coverage Audit

Verify that Storybook shared components from `@azure-fluent-storybook/components` were used wherever applicable. For any case where raw Fluent UI or custom elements were used instead, require a justification.

#### Procedure

1. **Check Container pattern (MANDATORY)** — Before any other checks, verify the page uses a proper Container:
   - The page must import either `AzureGlobalHeader` or `SREGlobalHeader` from `@azure-fluent-storybook/components`
   - The global header must be the **first child** inside the outermost page `<div>`
   - If neither header is present → flag as **High priority: Missing Container — page must be wrapped in Azure Container or SRE Container pattern**
   - If a `.schema.json` exists, verify the `container` field is present and set to `"azure"` or `"sre"`
2. **Load the Storybook component registry** — call `getComponentList` from Storybook MCP to get the current list of all available shared components.
2. **Read the target `.tsx` file** and extract:
   - All imports from `@azure-fluent-storybook/components` (what IS being used)
   - All imports from `@fluentui/react-components` (potential missed opportunities)
   - All custom JSX elements that aren't from either library
3. **Cross-reference** each Fluent UI import against the Storybook registry:
   - If a Storybook equivalent exists → flag as **should use Storybook version**
   - If no Storybook equivalent → mark as **justified Fluent fallback**
4. **Scan for custom HTML patterns** using the same detection table from the component-audit skill:
   - Custom `<div>` acting as toolbar → should be `CommandBar`
   - Custom `<div>` with key-value pairs → should be `EssentialsPanel`
   - Custom `<nav>` with links → should be `SideNavigation`
   - Custom tab implementation → should be `PageTabs`
   - Custom breadcrumb → should be `AzureBreadcrumb`
   - Custom card/tile → check for `CardButton`, `HealthStatusCard`, etc.
   - Custom empty state → should be `NullState`
5. **For each finding**, record:
   - What was used (the custom/Fluent element)
   - What should have been used (the Storybook component)
   - Whether there's a valid justification (customization not possible with Storybook component, component doesn't support needed variant, etc.)
6. **Validate Fluent icon imports** — check that every icon imported from `@fluentui/react-icons` actually exists. Fluent icons use compound names (e.g., `PreviewLink20Regular`, not `Preview20Regular`). If a `.schema.json` exists, run `python pipeline.py <schema> --validate-only` to catch bad icon names. Cross-reference against `.github/skills/page-builder/references/fluent-icon-reference.md`.
7. **Validate Azure service icons** — scan the `.tsx` file for every `<AzureServiceIcon name="..." />` usage and verify the `name` value has a matching `.svg` file in `public/azure-icons/`. Also scan for any `<img>` tags with `src` paths pointing to `azure-icons/` and verify those files exist. If a `.schema.json` exists, `python pipeline.py <schema> --validate-only` now also checks Azure icon names automatically. For each missing Azure icon:
   - **Flag as High priority** — a missing icon renders as a broken image
   - **Recovery:** Invoke the `iconcloud-browser` skill to search IconCloud.design for the missing icon name, download the SVG, and save it to `public/azure-icons/<name>.svg`
   - After downloading, re-run validation to confirm the icon now resolves

#### Valid justifications for NOT using a Storybook component

- The Storybook component doesn't support a required prop or variant
- The page needs a composition pattern that the Storybook component can't accommodate
- The element is a one-off layout piece (e.g., a custom illustration container) with no reusable equivalent
- The Storybook component is deprecated or has known issues documented in its Storybook page

If none of these apply, the finding is unjustified and should be flagged for replacement.

---

### Pass 3: Visual Analysis via Playwright

Take a screenshot of the rendered page and perform a visual inspection to catch layout issues, missing icons, alignment problems, and visual inconsistencies.

#### Prerequisites

- The Vite dev server must be running on port 5173
- Playwright MCP must be available

If Playwright MCP is not running, tell the user:
> "The Playwright MCP server isn't running. Open the Command Palette (`Cmd+Shift+P`), type **MCP: List Servers**, and click **Start** next to **playwright**."

If Playwright is unavailable, skip this pass and note it in the report as "Pass 3: Skipped — Playwright MCP unavailable".

#### Procedure

1. **Navigate** to `http://localhost:5173` using Playwright.
2. **Take a full-page screenshot** of the rendered page.
3. **Take a snapshot** (accessibility tree / DOM snapshot) for structural analysis.
4. **Analyze the screenshot** for these categories:

| Category | What to Check |
|----------|---------------|
| **Layout** | Does the page fill the viewport correctly? Is the side nav (if expected) visible and properly sized? Is content clipped or overflowing? Are there unexpected scrollbars? |
| **Spacing** | Are elements visually evenly spaced? Are there areas where content is too cramped or too far apart? Do sections have consistent padding? |
| **Icons** | Are all icons rendering (no broken image placeholders, no empty squares)? Are icon sizes consistent? Do icons match their intended meaning? |
| **Broken images** | Use Playwright to check for broken `<img>` elements: run `document.querySelectorAll('img')` and check each image's `naturalWidth === 0` or `complete === false`. Any broken image is a **High priority** finding. If the broken image src contains `azure-icons/`, invoke the `iconcloud-browser` skill to download the missing SVG from IconCloud.design and save it to `public/azure-icons/`. |
| **Typography** | Is text readable? Are headings visually distinct from body text? Are there inconsistent font sizes in similar elements? |
| **Colors** | Does the page use a consistent color palette? Are there jarring color mismatches? Does it look like a standard Azure Portal page? |
| **Command bar** | Is it present if expected? Are buttons aligned and properly spaced? |
| **Empty states** | If tables/lists are empty, is there a proper empty state illustration? |
| **Alignment** | Are elements in columns/rows properly aligned? Are labels and values aligned in key-value pairs? |
| **Responsiveness** | Does the layout handle the current viewport without breaking? |

5. **If the user provided a reference screenshot** (from the original page-builder request), compare the output against it and note any significant visual differences.

---

## Output: Prioritized Action List

After completing all three passes, consolidate findings into a single prioritized list. Group by severity:

### Priority Definitions

| Priority | Criteria | Examples |
|----------|----------|---------|
| **High** | Violations that break visual consistency, accessibility, or use completely wrong components | Hardcoded brand colors, missing Storybook component with direct equivalent, broken layout, missing icons, text not readable |
| **Medium** | Suboptimal choices that work but don't follow best practices | Hardcoded neutral colors that happen to match the token value, using Fluent when Storybook exists but the difference is minor, spacing inconsistencies |
| **Low** | Nitpicks and polish opportunities | Could use a more specific token variant, minor alignment tweaks, style consolidation opportunities |

### Report Format

```
## Page Review Report — [PageName]

### Summary
- **Pass 1 (Tokens):** N findings (X high, Y medium, Z low)
- **Pass 2 (Components):** N findings (X high, Y medium, Z low)
- **Pass 3 (Visual):** N findings (X high, Y medium, Z low)
- **Total actions:** N

---

### 🔴 High Priority

#### H1. [Short title]
- **Pass:** 1 — Token Audit
- **Location:** `src/pages/PageName.tsx` line 45
- **Issue:** Hardcoded color `#0078d4` used for primary button background
- **Fix:** Replace with `tokens.colorBrandBackground`
- **Impact:** Brand color won't update with theme changes

#### H2. [Short title]
- **Pass:** 2 — Component Audit
- **Location:** `src/pages/PageName.tsx` lines 120–145
- **Issue:** Custom `<div className={styles.commandBar}>` with 5 icon buttons — `CommandBar` from Storybook does exactly this
- **Fix:** Replace with `<CommandBar items={[...]} />`
- **Impact:** Missing keyboard navigation, overflow handling, and consistent styling

#### H3. [Short title]
- **Pass:** 3 — Visual Analysis
- **Issue:** Side navigation panel not visible — content fills full width but schema specifies side-panel layout
- **Fix:** Check that SideNavigation component is rendered and has proper width
- **Impact:** Page layout doesn't match intended design

---

### 🟡 Medium Priority

#### M1. [Short title]
...

---

### 🟢 Low Priority

#### L1. [Short title]
...

---

### ✅ Passing Checks
- Token usage: N/M values use proper tokens (X%)
- Storybook components: N/M available components used (X%)
- Visual: Layout renders correctly at default viewport
- Visual: All icons render without errors
```

## Important Rules

- **Run ALL three passes.** Do not skip any pass unless a required tool (Playwright) is unavailable.
- **Be specific with line numbers.** Every code-level finding must include the exact file and line number.
- **Provide the fix, not just the problem.** Every finding must include a concrete fix with the exact token name, component name, or code change needed.
- **Justify Fluent fallbacks.** If a Fluent component is used instead of Storybook, require a reason. "I didn't know it existed" is not valid.
- **Don't flag exceptions.** Review the exceptions list in Pass 1 before flagging spacing/size values.
- **Cross-reference the schema.** If a `.schema.json` exists, compare the rendered output against the schema intent — flag any drift.
- **The action list is the deliverable.** The user should be able to work through the list top-to-bottom and fix everything.
