# Layout Decision Guide

Use this guide to determine whether a page needs a side panel navigation or should be full width.

## Decision Rule

Ask: **"Is the user looking at a specific deployed resource or service?"**

### YES → Side Panel Layout
The page has a `SideNavigation` component on the left (220px) with the content area on the right.

**Examples:**
- Resource overview (e.g., Static Web App overview, Storage Account overview)
- Resource sub-page (e.g., Subscriptions page under Resource Manager)
- Service detail page (e.g., Entra ID → Preview features)
- Any page where a left nav lets you switch between sub-sections of the same resource

**Structure:**
```
┌─────────────────────────────────────────────────┐
│ AzureGlobalHeader                               │
├─────────────────────────────────────────────────┤
│ Breadcrumb                                      │
│ PageHeader (title, icon, pin, more)             │
├──────────┬──────────────────────────────────────┤
│ SideNav  │ CommandBar                           │
│          │ Content (table, detail, cards, etc.)  │
│          │                                      │
└──────────┴──────────────────────────────────────┘
```

### NO → Full Width Layout
The page fills the entire width. No side navigation.

**Examples:**
- Home page
- Create wizard / form
- Marketplace browse
- All-resources list
- Browse / empty-state pages

**Structure:**
```
┌─────────────────────────────────────────────────┐
│ AzureGlobalHeader                               │
├─────────────────────────────────────────────────┤
│ CommandBar                                      │
│ Content (full width)                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Important Notes

- Content sidebars (e.g., category filters, list panels) are NOT the same as side navigation — they go inside the content area of a full-width layout
- Multi-page flows can mix layouts: Browse (full) → Create (full) → Detail (side panel)
- The side nav uses `SideNavigation` from `@azure-fluent-storybook/components` with `NavItem[]`
