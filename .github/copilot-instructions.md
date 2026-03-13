# Copilot Instructions — Azure Builder Playground

## Pre-Flight Checks

Before doing any work on the user's first prompt, run these checks silently and fix anything missing:

### 1. Dependencies
Check if `node_modules/` exists. If not, run `npm install` automatically.

### 1b. Playwright Chromium
Check if Playwright's Chromium browser is installed by running `npx playwright install --dry-run chromium 2>&1`. If the output indicates Chromium is not installed (or the command fails), run `npx playwright install chromium` automatically to install it. This is required for visual verification, screenshots, and any browser automation tasks.

### 2. Dev Server
Check if the Vite dev server is running (port 5173). If not, start it with `npm run dev` in a background terminal.

### 3. Experiment Metadata
Check if `experiment.json` still has the default placeholder values (`"My Experiment"` / `"A playground for rapid prototyping"`). If so, infer a name and description from the user's first prompt and update the file automatically. For example:
- "Build me a VM overview page" → `{ "name": "Virtual Machine Overview", "description": "Azure VM resource overview page prototype" }`
- "Create a storage account browse page" → `{ "name": "Storage Account Browser", "description": "Browse and manage storage accounts" }`

### 3b. Keeping Experiment Metadata Current
After **every** build, edit, or significant change to the experiment, update `experiment.json`:
- **`description`**: Rewrite to accurately reflect the current state of the experiment (not just the initial prompt).
- **`tags`**: Maintain an array of lowercase, kebab-case tags covering three categories:
  - **UX patterns** — layout and interaction patterns used (e.g. `"resource-overview"`, `"command-bar"`, `"side-panel-nav"`, `"filter-bar"`, `"create-wizard"`, `"detail-page"`, `"browse-list"`, `"empty-state"`)
  - **Components** — key Storybook or Fluent components used (e.g. `"data-grid"`, `"page-header"`, `"kpi-card"`, `"tabs"`, `"message-bar"`, `"dialog"`)
  - **Jobs-to-be-done** — user tasks the experiment addresses (e.g. `"monitor-resources"`, `"manage-vms"`, `"configure-networking"`, `"review-costs"`, `"deploy-app"`)
- Tags help teammates discover experiments in the community hub. Be generous — include every relevant pattern, component, and job.
- Example:
  ```json
  {
    "name": "Virtual Machine Overview",
    "description": "Azure VM resource overview with monitoring KPIs, command bar actions, and properties panel",
    "tags": [
      "resource-overview", "side-panel-nav", "command-bar",
      "kpi-card", "data-grid", "page-header", "tabs",
      "monitor-resources", "manage-vms", "restart-vm", "view-properties"
    ]
  }
  ```

### 4. Storybook MCP (Mandatory)
Storybook MCP is the primary documentation and discovery source for Azure Portal components. Before building any page or UI:
1. Verify Storybook MCP is running by calling `getComponentList`.
2. If it's not available, stop and tell the user (see below).
3. Call `getComponentsProps` for every component you plan to use — **read the Storybook documentation first** to understand props, variants, usage patterns, and best practices before writing any code. This is especially important for greenfield builds and when modifying existing designs.
4. Import components **and themes** from `@azure-fluent-storybook/components` (an npm package already in the project's dependencies). Both components and themes are exported from this single package.
5. Only drop to raw `@fluentui/react-components` for elements that have no equivalent in `@azure-fluent-storybook/components`.

### 5. MCP Server Availability
If you attempt to use Storybook MCP tools and they aren't available, tell the user:
> "The Storybook MCP server isn't running. Open the Command Palette (`Cmd+Shift+P`), type **MCP: List Servers**, and click **Start** next to **storybook**."

If you attempt to use Playwright MCP tools and they aren't available, tell the user:
> "The Playwright MCP server isn't running. Open the Command Palette (`Cmd+Shift+P`), type **MCP: List Servers**, and click **Start** next to **playwright**."

If the user's prompt involves a Figma URL or mentions Figma and the Figma MCP tools aren't available, tell the user:
> "The Figma MCP server isn't running. Open the Command Palette (`Cmd+Shift+P`), type **MCP: List Servers**, and click **Start** next to **figma**. You'll need a Figma API key — get one at figma.com/developers."

### 6. Page Creation Gate
When the user asks to "make this", "build this", "create a page", or provides a screenshot of a UI to recreate:
1. **STOP** — do NOT write any `.tsx` file directly.
2. Read the page-builder skill at `.github/skills/page-builder/SKILL.md`.
3. Follow its full pipeline: generate `.schema.json` first, validate it, then generate the component.
4. Skipping the schema step is never acceptable.

**WRONG — never do this:**
```
User: "Build me a VM overview page"
Agent: *immediately creates src/main/index.tsx with hand-written JSX*
```
```
User: "Make this" (attaches screenshot)
Agent: *writes a .tsx file without producing a .schema.json first*
```
```
User: "Create a storage account page"
Agent: *generates .schema.json but skips validation and jumps straight to .tsx*
```

**RIGHT — always do this:**
```
User: "Build me a VM overview page"
Agent:
  1. Reads .github/skills/page-builder/SKILL.md
  2. Queries Storybook MCP for component APIs
  3. Reads references/fluent-icon-reference.md for verified icon names
  4. Creates VmOverview.schema.json (using only verified icon names)
  5. Runs `python pipeline.py VmOverview.schema.json --validate-only` (catches bad icons)
  6. Generates VmOverview.tsx from the validated schema
  7. Runs page-review skill (token audit → component audit → visual analysis)
  8. Fixes all High-priority findings before presenting to user
```

**Icon naming:** Fluent icons use compound names — never invent simple names like `Preview`, `Feedback`, `Refresh`. Always consult `.github/skills/page-builder/references/fluent-icon-reference.md`.

## Workspace Conventions

- Each repo is a single experiment with one `src/main/` and optional `src/variations/`
- The shell (`src/shell/App.tsx`) auto-discovers all versions via `import.meta.glob` — never manually register pages
- **Container-first**: Every page MUST be wrapped in a Storybook Container (`Container/Azure Container` or `Container/SRE Container`). Before building any page, call `getComponentsProps` for the relevant container to verify the pattern. The Container ensures the page has the correct global header (`AzureGlobalHeader` or `SREGlobalHeader`) as its first child, proper theme, and layout scaffold. **Never build a page without a Container.**
- **Storybook-first**: Before writing any component code, call `getComponentList` and `getComponentsProps` from Storybook MCP. **Read the Storybook docs for each component** to understand its API, variants, best practices, and gotchas — then import the component from `@azure-fluent-storybook/components`. Use composed/template components (PageHeader, CommandBar, FilterBar, DataGrid, SideNavigation, Azure Container, Resource List Page, etc.) instead of building from raw Fluent primitives. Only drop to raw `@fluentui/react-components` for elements that have no Storybook equivalent.
- **Component imports**: `@azure-fluent-storybook/components` for shared Azure Portal components **and** themes — this is a real npm package installed via `package.json`
- Use `@fluentui/react-components` for UI primitives and `makeStyles` + `tokens` for styling
- Never hardcode colors, fonts, or spacing — always use Fluent tokens
- Variation names use kebab-case

## Azure URL Handling

When the user's prompt contains an Azure Portal URL (anything matching `portal.azure.com`, `azure.microsoft.com`, or similar Microsoft domains):

### Why Playwright, not VS Code's browser
VS Code's integrated browser blocks authentication flows from Microsoft/Entra ID accounts. Azure Portal pages require sign-in, so the built-in browser will fail. **Always use Playwright** to open Azure URLs.

### Procedure
1. **Launch Playwright in headed (non-headless) mode** so the user can see the browser window and authenticate.
2. Navigate to the Azure URL.
3. **Pause and tell the user:**
   > "A browser window has opened. Please sign in with your Azure account. Let me know once you're on the page you want me to capture."
4. **Wait for the user to confirm** they've signed in and the page has loaded.
5. Take a screenshot and/or snapshot of the page to use as the design reference.
6. Close the browser or keep it open if the user needs to navigate to additional pages.

### Important
- **Never** attempt to open Azure URLs in VS Code's integrated browser or an iframe.
- **Never** try to automate the Microsoft login flow — let the user authenticate manually in the headed browser.
- If Playwright MCP is not running, prompt the user to start it before proceeding.
- The user may need to navigate through the portal (click into a resource, switch tabs) before the page is ready to capture — wait for their confirmation.
