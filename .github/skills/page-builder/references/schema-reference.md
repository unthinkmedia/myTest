# PageSchema Reference

Complete reference for the `PageSchema` Pydantic model defined in `schemas/page.py`.

## Table of Contents
1. [Top-Level Structure](#top-level-structure)
2. [PageMeta](#pagemeta)
3. [ContainerType](#containertype)
4. [SideNavConfig](#sidenavconfig)
5. [TitleConfig](#titleconfig)
6. [EssentialsConfig](#essentialsconfig)
7. [CommandBar](#commandbar)
8. [Content Templates](#content-templates)
9. [StoryRef](#storyref)

---

## Top-Level Structure

```json
{
  "meta": { ... },           // PageMeta (required)
  "container": "azure",      // "azure" | "sre" (required)
  "sideNav": { ... },        // SideNavConfig | null
  "title": { ... },          // TitleConfig | null
  "essentials": { ... },     // EssentialsConfig | null
  "commandBar": { ... },     // CommandBar | null
  "template": { ... }        // ContentTemplate (required, discriminated by "kind")
}
```

## PageMeta

```json
{
  "title": "Page Name",                    // required, min 1 char
  "description": "What this page does",    // optional
  "route": "/resource/page",               // optional URL route
  "topics": ["topic1", "topic2"]           // optional
}
```

## ContainerType

- `"azure"` — Azure Portal shell (renders `AzureGlobalHeader`)
- `"sre"` — SRE Portal shell (renders `SREGlobalHeader`)

## SideNavConfig

```json
{
  "defaultSelected": "overview",     // key of initially selected item
  "collapsible": true,               // can collapse
  "closable": false,                 // show X button
  "width": 220,                      // 120–400px
  "entries": [                       // NavItem | NavGroup (discriminated by "kind")
    {
      "kind": "item",
      "key": "overview",
      "label": "Overview",
      "icon": "Info"                 // icon name from AzureServiceIcon
    },
    {
      "kind": "group",
      "label": "Settings",
      "items": [
        { "kind": "item", "key": "config", "label": "Configuration", "icon": "Settings" }
      ]
    }
  ]
}
```

**NavItem fields:**
- `kind`: `"item"` (literal)
- `key`: unique identifier (required)
- `label`: display text (required)
- `icon`: icon name for `AzureServiceIcon` (optional)
- `route`: navigation target (optional)

**NavGroup fields:**
- `kind`: `"group"` (literal)
- `label`: section header text (required)
- `items`: array of NavItem (min 1)

## TitleConfig

```json
{
  "resourceName": "coherence-preview",     // primary name (required)
  "pageName": "Overview",                  // sub-page after "|" (optional)
  "icon": "StaticApps",                    // AzureServiceIcon name (optional)
  "breadcrumbs": ["Home"],                 // trail (optional)
  "closable": false,                       // show X / pin button
  "moreActions": true                      // show "..." overflow menu
}
```

Rendered title: `"resourceName | pageName"` (or just `resourceName` if pageName is empty).

## EssentialsConfig

```json
{
  "fields": [
    {
      "label": "Resource group",
      "value": "my-rg",
      "copyable": false,
      "link": ""                          // if set, value renders as link
    }
  ],
  "expanded": true                        // starts open
}
```

**Note:** The `.tsx` component uses `EssentialsPanel` from `@azure-fluent-storybook/components` which has a richer API with `leftItems`, `rightItems`, and `actions`. When hand-building TSX for complex essentials (like the Static Web App page), use the component directly rather than relying on codegen.

## CommandBar

```json
{
  "items": [
    {
      "story": {
        "storyId": "components-button--subtle",
        "instanceId": "refresh-btn",
        "argOverrides": { "label": "Refresh", "icon": "ArrowSync" }
      },
      "isSeparator": false
    },
    {
      "story": null,
      "isSeparator": true
    }
  ]
}
```

**Validation rules:**
- Separators must have `story: null` and `isSeparator: true`
- Non-separators must have a `story` and `isSeparator: false`

**Icon mapping:** The `icon` in `argOverrides` maps to `@fluentui/react-icons` as `{Icon}20Regular` (e.g., `"ArrowSync"` → `ArrowSync20Regular`).

**CRITICAL — Icon names must be real:** Fluent icons use compound names. Simple English words like `Preview`, `Feedback`, `Refresh`, `Close`, `Monitor`, `Deploy`, `Dashboard` do NOT exist as icon names. Always consult `references/fluent-icon-reference.md` for verified names. The pipeline validates icons against the installed package and **blocks codegen** if any are invalid. Common corrections:
- `Preview` → `PreviewLink`
- `Feedback` → `PersonFeedback`
- `Refresh` → `ArrowSync`
- `Close` → `Dismiss`
- `Help` → `QuestionCircle`
- `Lock` → `LockClosed`

## Content Templates

### list-table

Data table with search, filters, and sortable columns.

```json
{
  "kind": "list-table",
  "description": "Optional text above the table",
  "columns": [
    {
      "key": "name",
      "header": "Name",
      "columnType": "link",          // "text" | "date" | "badge" | "link" | "toggle"
      "sortable": true,
      "filterable": false,
      "width": "",
      "truncate": false
    }
  ],
  "filters": {
    "searchable": true,
    "searchPlaceholder": "Search...",
    "addFilters": false
  },
  "pagination": true,
  "rowActions": []
}
```

### form

Create/edit form with labeled input fields.

```json
{
  "kind": "form",
  "description": "",
  "fields": [
    {
      "name": "resourceName",
      "label": "Resource name",
      "inputType": "text",           // "text" | "number" | "select" | "checkbox" | "textarea"
      "required": true,
      "placeholder": "Enter name",
      "options": []                  // for select/radio
    }
  ],
  "submitLabel": "Create",
  "cancelLabel": "Cancel"
}
```

### cards-grid

Grid of cards for dashboards or overviews.

```json
{
  "kind": "cards-grid",
  "description": "",
  "columns": 3,                     // 1–6
  "cards": [
    {
      "cardId": "card-1",
      "title": "Card Title",
      "description": "Card body text",
      "icon": "Database",
      "stories": []
    }
  ]
}
```

### detail

Property sheet with labeled sections.

```json
{
  "kind": "detail",
  "description": "",
  "sections": [
    {
      "sectionId": "overview",
      "label": "Overview",
      "stories": []
    }
  ]
}
```

### custom

Escape hatch for non-standard layouts. When using `custom`, the codegen produces minimal output — you'll hand-build the TSX.

```json
{
  "kind": "custom",
  "description": "Resource overview with tabs and mixed content",
  "stories": [
    {
      "storyId": "components-button--primary",
      "instanceId": "visit-site-btn",
      "argOverrides": { "label": "Visit your site" }
    }
  ]
}
```

## StoryRef

A pointer to a Storybook story variant with optional overrides.

```json
{
  "storyId": "components-button--subtle",       // Storybook story ID
  "instanceId": "save-btn",                     // unique within page
  "argOverrides": { "label": "Save" },          // override default args
  "cssOverrides": {},                           // CSS custom property overrides
  "slotChildren": {}                            // slot → child instance IDs
}
```
