# Page Examples

Real pages in the workspace that serve as reference implementations.

## Subscriptions (list-table with side nav)

**File:** `src/pages/Subscriptions.tsx`
**Template:** `list-table`
**Layout:** Side Panel

A Resource Manager subscriptions listing page. Demonstrates:
- Azure container with `AzureGlobalHeader`
- Breadcrumb: Home → Resource Manager
- PageHeader with pipe title: "Resource Manager | Subscriptions"
- Full side navigation with items and groups (Organization, Tools, Deployments, Help)
- CommandBar with 5 action buttons
- Description text above the table
- SearchBox + FilterPill filter row
- DataGrid with 5 columns (subscription name as link, ID, role, cost, score)
- Sample data rows

**Key pattern:** The side nav uses `children` arrays for groups, and `selected: true` on the active item.

## PreviewFeatures (list-table with side nav)

**File:** `src/pages/PreviewFeatures.tsx`
**Template:** `list-table`
**Layout:** Side Panel

Entra ID preview features page. Demonstrates:
- Breadcrumb: Home → Default Directory
- PageHeader: "Default Directory | Preview features"
- Side nav with a large "Manage" group (13 sub-items)
- CommandBar with Save, Discard, [separator], Got feedback?
- DataGrid with 6 columns including a Toggle column type
- Empty data array (placeholder)

## AzureSREAgent (list-table, no side nav, SRE container)

**File:** `src/pages/AzureSREAgent.tsx`
**Template:** `list-table`
**Layout:** Full Width

SRE Agent Spaces browse page. Demonstrates:
- SRE container with `SREGlobalHeader` instead of Azure
- No side navigation
- No breadcrumbs or page title bar
- Tab bar (Agent Spaces, Monitors, Incidents)
- CommandBar with Create, Refresh, Delete
- SearchBox filter
- Empty state with illustration SVG

**Key pattern:** Shows how to build a non-Azure page with the SRE shell.

## StaticWebApp (custom resource overview)

**File:** `src/pages/StaticWebApp.tsx`
**Template:** `custom` (hand-built)
**Layout:** Side Panel

Azure Static Web App resource overview. Demonstrates:
- Full essentials panel with left/right columns and action links
- PageTabs (Get started / Monitoring)
- Tab content with sections: "View your application", "Prepare for production", "Make the most of your Static Web App"
- MessageBar info banner
- Custom production checklist cards (built from scratch — not in shared library)
- CardButton horizontal variant for service feature cards
- Mix of shared components and custom-styled elements

**Key pattern:** The most complex page — essentials, tabs, multiple content sections, custom cards. Good reference for resource overview pages. Note that some elements (production cards with status dots) were created from scratch because no shared component existed.
