# Azure Builder Playground

A rapid prototyping environment for building Azure Portal page experiments using React, Fluent UI, and a shared Azure component library. Each repo is a **single experiment** — describe what you want to Copilot, and it builds the page for you. No coding experience required.

> **Open in VS Code, ask Copilot anything — it handles the rest.**

---

## Getting Started (Step by Step)

### Step 1: Get your own copy of this project

1. Go to [github.com/unthinkmedia/AzureBuilderPlayground](https://github.com/unthinkmedia/AzureBuilderPlayground)
2. Click the green **"Use this template"** button (top right)
3. Click **"Create a new repository"**
4. Pick **your GitHub account** as the Owner
5. Give it a name (e.g., `my-azure-experiment`)
6. Click **"Create repository"**

You now have your own copy on GitHub. The original is not affected.

### Step 2: Choose a folder on your computer

Create a folder wherever you want your project to live (e.g., on your Desktop, in Documents, etc.). Then open **Terminal** and navigate to it:

- **Option A — Drag and drop:** Open Terminal, type `cd ` (with a space after it), then **drag the folder from Finder into the Terminal window**. It fills in the path for you. Press Enter.
- **Option B — Type it manually:**
  ```bash
  cd ~/Desktop/my-projects
  ```

### Step 3: Copy the repo URL and clone it

1. Go to **your new repo** on GitHub (the one you just created from the template)
2. Click the green **"<> Code"** button
3. Make sure **HTTPS** is selected
4. Click the **copy icon** (📋) to copy the URL — it will look like `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git`

Now go back to your Terminal (which should be in the folder from Step 2) and run:

```bash
# Paste the URL you just copied after "git clone"
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Move into the project folder
cd YOUR_REPO_NAME

# Open it in VS Code Insiders
code-insiders .
```

> **Prerequisite — install the `code-insiders` (or `code`) shell command:**
> If running `code-insiders .` gives you "command not found", you need to install the shell command first:
> 1. Open **VS Code Insiders** (or VS Code) normally (from your Applications folder / Start Menu)
> 2. Open the **Command Palette** (`Cmd+Shift+P` on Mac, `Ctrl+Shift+P` on Windows)
> 3. Type **"Shell Command: Install"** and select **"Shell Command: Install 'code-insiders' command in PATH"** (or **"Install 'code' command in PATH"** for regular VS Code)
> 4. Restart your Terminal — the command should now work

> **Example:** If your repo URL is `https://github.com/jsmith/my-azure-experiment.git`:
> ```bash
> git clone https://github.com/jsmith/my-azure-experiment.git
> cd my-azure-experiment
> code-insiders .
> ```

### Step 4: Start the MCP servers

The project comes with pre-configured MCP servers that give Copilot extra capabilities. Start them from VS Code:

1. Open the **Command Palette** (`Cmd+Shift+P` on Mac, `Ctrl+Shift+P` on Windows)
2. Type **"MCP: List Servers"** and select it
3. Start each server you need:

| Server | Required? | What it does |
|--------|-----------|-------------|
| **storybook** | Yes | Gives Copilot access to the shared Azure component library — components, props, and usage examples |
| **playwright** | Yes | Lets Copilot automate a browser — take screenshots, navigate pages, capture reference designs |
| **figma** | Optional | Connects Copilot to Figma for reading designs directly. You'll be prompted for a Figma API key on first start (get one at [figma.com/developers](https://www.figma.com/developers/api#access-tokens)) |

All servers are already configured in `.vscode/mcp.json` — just click **"Start"** next to each one. You only need to start them once per session.

> **Don't worry if you forget** — if Copilot needs a server that isn't running, it will remind you which one to start and how.

### Step 5: Start prompting!

That's it — just ask Copilot to build something. **You don't need to run any commands.** On your very first prompt, Copilot automatically:

- **Installs dependencies** — runs `npm install` to set up the shared Azure component library and all packages
- **Starts the dev server** — runs `npm run dev` so you can preview your page instantly
- **Names your experiment** — fills in `experiment.json` based on what you ask for

You can describe what you want in plain text, or give Copilot a visual reference to work from:

| Input | How to use it |
|-------|--------------|
| **Text description** | Just describe the page you want in your prompt |
| **Screenshot** | Paste or attach a screenshot of an Azure Portal page and say "recreate this" |
| **URL to an Azure page** | Paste a URL and Copilot will use Playwright to capture and analyze the live page |
| **Figma link** | Paste a Figma file/frame URL and Copilot will pull the design directly (requires the Figma MCP server) |

**Example prompts:**

```
Build me an Azure Virtual Machines overview page
```

```
Create a Storage Account browse page with a table
```

```
Recreate this portal page (+ attach a screenshot)
```

```
Build this page: https://portal.azure.com/#view/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade
```

```
Build a page from this Figma design: https://www.figma.com/design/abc123/My-Design
```

---

## Quick Start (for manual setup)

If you prefer to set things up yourself instead of letting Copilot handle it:

```bash
# Install dependencies (includes the shared Azure component library)
npm install

# Start the dev server
npm run dev

# Build for production
npm run build
```

The app runs at `http://localhost:5173` and hot-reloads on changes.

> **Note:** If you're using Copilot, you don't need to run these commands — Copilot does it automatically on your first prompt.

---

## Project Structure

```
experiment.json                 ← Experiment name & description
pipeline.py                     ← Schema → Validate → Code CLI
schemas/                        ← Pydantic models & codegen
src/
  main.tsx                      ← React entrypoint
  shell/
    App.tsx                     ← Auto-discovers main + variations, renders picker
  main/
    index.tsx                   ← Canonical version of the experiment
    <ScreenName>.tsx            ← Additional screens (multi-screen flows)
    flow.json                   ← Optional: screen order for flows
  variations/
    <variation-name>/
      meta.json                 ← { "description": "..." }
      index.tsx                 ← Variation's version
      <ScreenName>.tsx          ← Additional screens
      flow.json                 ← Optional: screen order
.github/skills/                 ← Copilot skills (page-builder, etc.)
public/azure-icons/             ← Azure service icon SVGs
```

---

## How Experiments Work

An experiment is a self-contained prototype of an Azure Portal page (or multi-page flow). The shell (`App.tsx`) automatically discovers all versions using Vite's `import.meta.glob` — no manual registration needed.

### experiment.json

The root `experiment.json` defines metadata:

```json
{
  "name": "My Experiment",
  "description": "A playground for rapid prototyping",
  "tags": []
}
```

### Single-Screen vs Multi-Screen

- **Single-screen:** Only `index.tsx` in the folder.
- **Multi-screen flow:** Multiple `.tsx` files + a `flow.json` that defines the screen order.

```json
// flow.json
["Overview", "Create", "Review"]
```

Values are filenames without `.tsx`. The shell renders step navigation (tabs) when `flow.json` is present.

---

## Creating an Experiment

### Option 1: Ask Copilot to build a page

Use natural language to describe or provide a screenshot of an Azure Portal page. Copilot uses the **page-builder** skill to generate a validated schema and React component.

**Prompt examples:**

```
Build me an Azure Virtual Machines overview page
```

```
Create a page that looks like the Azure Storage Account browse page with a table of storage accounts
```

```
Build a resource group overview page with essentials panel, activity log, and deployments tab
```

```
Make a page that shows a Kubernetes cluster overview with node pools, workloads, and monitoring sections
```

```
Create an Azure SQL Database create wizard with basics, networking, security, and review steps
```

```
Recreate this portal page
(attach a screenshot)
```

The page-builder skill will:

1. Analyze your input (screenshot or description)
2. Determine layout (side panel vs full width)
3. Choose a content template (`list-table`, `form`, `cards-grid`, `detail`, or `custom`)
4. Generate a `.schema.json` and `.tsx` component
5. Produce a build report listing all components used

The shell (`App.tsx`) auto-discovers new pages — no manual registration needed.

### Option 2: Build manually

Create `src/main/index.tsx` with a default-exported React component:

```tsx
import React from 'react';
import { makeStyles, tokens, Text } from '@fluentui/react-components';

const useStyles = makeStyles({
  root: { padding: '24px' },
});

const MyPage: React.FC = () => {
  const styles = useStyles();
  return (
    <div className={styles.root}>
      <Text size={800} weight="semibold">My Page</Text>
    </div>
  );
};

export default MyPage;
```

### Option 3: Use the schema pipeline

Write a `.schema.json` file conforming to the `PageSchema` model, then run:

```bash
python pipeline.py MyPage.schema.json
python pipeline.py MyPage.schema.json --output src/main/index.tsx
python pipeline.py MyPage.schema.json --validate-only
```

The schema answers 6 questions:

| # | Question | Values |
|---|----------|--------|
| 1 | What container? | `azure` or `sre` |
| 2 | Side nav? | `SideNavConfig` or `null` |
| 3 | Page title? | `TitleConfig` with resource name, icon, breadcrumbs |
| 4 | Breadcrumbs? | Array inside `TitleConfig` |
| 5 | Body template? | `list-table`, `form`, `cards-grid`, `detail`, `custom` |
| 6 | Essentials accordion? | `EssentialsConfig` or `null` |

---

## Variations

Variations let you explore alternative designs without touching your main version. The shell auto-discovers them and renders a dropdown picker to switch between versions.

### Creating a Variation

**Prompt examples:**

```
Make a variation that uses cards instead of a table
```

```
Create a variation with a compact toolbar and fewer columns
```

```
Try a different version that uses tabs instead of a sidebar
```

```
New variant with a dark theme command bar
```

```
Make a variation that adds a monitoring dashboard tab
```

What happens:

1. A kebab-case folder name is derived from your description (e.g., `card-layout`)
2. All files from `src/main/` are copied to `src/variations/<name>/`
3. A `meta.json` is created with the variation description
4. The requested changes are applied to the variation copy
5. The shell auto-discovers and shows it in the picker — no registration needed

**Rules:**
- `src/main/` is never modified when creating a variation
- Each variation is a full standalone copy (no imports from main)
- Variation names use kebab-case
- If main has a `flow.json`, it gets copied too

### Deleting a Variation

```
Delete the card-layout variation
```

```
Remove the compact-toolbar variant
```

You'll be asked to confirm before deletion. The main version cannot be deleted.

### Promoting a Variation to Main

```
Make card-layout the main version
```

```
Promote compact-toolbar to main
```

```
Swap main with the dark-toolbar variation
```

What happens:

1. Current `src/main/` moves to `src/variations/previous-main/`
2. The promoted variation moves to `src/main/`
3. `meta.json` is removed from the new main, added to `previous-main`

### Listing Variations

```
What variations exist?
```

```
Show me all the variants
```

Returns a table of all versions with their descriptions.

---

## Features & Copilot Skills

### Page Builder

Build Azure Portal pages from descriptions or screenshots.

| Prompt | What it does |
|--------|-------------|
| `Build a page for Azure App Service overview` | Creates a resource overview with side nav, essentials, tabs |
| `Create a Storage Accounts browse page` | Full-width page with data table, filters, command bar |
| `Make a Create VM wizard` | Multi-step form with basics, disks, networking, review |
| `Build a resource group page with deployments` | Side-panel detail page with sub-pages |
| `Create a dashboard with KPI cards` | Cards-grid layout with health metrics |
| `Recreate this portal page` + screenshot | Pixel-faithful reproduction from a screenshot |

### Component Audit

After building a page, check for custom UI that could use shared components.

```
Audit my page for missing shared components
```

```
What components am I not using from storybook?
```

```
Component check on the overview page
```

Detects custom HTML/CSS patterns that duplicate existing `@azure-fluent-storybook/components` or Fluent UI components and suggests replacements.

### IconCloud Browser

Browse and download icons from Microsoft's IconCloud repository (Azure Icons, Fluent System Library, Visual Studio Icons, etc.).

```
Find me an icon for Virtual Machine
```

```
Get the Azure icon for Storage Account
```

```
Search for networking icons
```

Opens a visual icon browser to search 10,000+ Microsoft icons across multiple libraries.

### Experiment Helper

Manage variations directly through natural language.

```
Make a variation that uses a grid layout
```

```
Delete the sidebar variation
```

```
Promote compact-toolbar to main
```

```
What variations exist?
```

### Skill Creator

Create new Copilot skills for this workspace.

```
Create a skill that generates mock data for tables
```

```
Write a skill for accessibility testing
```

---

## Multi-Screen Flows

For create wizards, onboarding flows, or any multi-step experience:

1. Create named `.tsx` files for each screen (e.g., `Basics.tsx`, `Networking.tsx`, `Review.tsx`)
2. Add a `flow.json` with the screen order
3. The shell renders tab/step navigation automatically

```
Build me a Create VM wizard with Basics, Disks, Networking, and Review + Create steps
```

Variations of multi-screen flows can modify any subset of screens, add new screens, remove screens, or reorder `flow.json`.

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Fluent UI v9** | Microsoft's design system primitives |
| **@azure-fluent-storybook/components** | Pre-built Azure Portal components and themes (PageHeader, CommandBar, FilterBar, DataGrid, SideNavigation, etc.) — installed automatically via `npm install` |
| **Vite** | Build tool & dev server |
| **TypeScript** | Type safety |
| **Pydantic** | Schema validation (Python pipeline) |

---

## Content Templates

The schema pipeline supports 5 content template types:

| Template | Use Case | Example |
|----------|----------|---------|
| `list-table` | Data tables, resource lists, browse pages | Storage Accounts list, VM instances |
| `form` | Create/edit forms with fields | Create VM wizard steps |
| `cards-grid` | Dashboard overviews, KPI tiles | Resource group overview, health dashboard |
| `detail` | Property sheets, overview sections | Resource properties, configuration details |
| `custom` | Mixed content, tabs + cards + charts | Resource overview "Get started" tab |

---

## Layout Types

| Layout | When to Use | Characteristics |
|--------|-------------|-----------------|
| **Side Panel** | Resource overview, sub-pages, detail pages | 220px nav + `SideNavigation` left of content |
| **Full Width** | Home, create wizard, marketplace, browse | Content fills the full area |

**Decision rule:** "Am I looking at a specific deployed resource?" → Side Panel. Otherwise → Full Width.

---

## Prompt Cheat Sheet

### Building Pages

```
Build me an Azure [service] overview page
Create a [service] browse page with [columns]
Make a create [resource] wizard with [steps]
Build a dashboard with [metrics/KPIs]
Recreate this portal page (+ screenshot)
Build a [service] detail page with [sections]
Create a resource list page for [resource type]
```

### Managing Variations

```
Make a variation that [change description]
Create a variation with [feature]
Try a different version that [approach]
Delete the [name] variation
Promote [name] to main
Make [name] the main version
What variations exist?
Show me the variants
```

### Post-Build

```
Audit components on this page
Check for missing shared components
Find me an icon for [service/concept]
Run a component check
```

### Utilities

```
Create a skill that [capability]
Dump the schema prompt context
Validate my schema file
```
