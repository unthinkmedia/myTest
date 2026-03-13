# Component Catalog

All shared components available for building pages. Always use these before creating custom UI.

## Container Pattern (MANDATORY)

**Every page MUST live inside a Container.** The Container section in Storybook (`Container/Azure Container`, `Container/SRE Container`) defines the canonical page shell. Always consult the Storybook Container docs before building any page.

### Azure Container
The standard Azure Portal page shell. Provides the correct theme, global header, and page structure.
```tsx
// Structure every Azure page must follow:
<div className={styles.page}>           {/* height: 100vh, flex column */}
  <AzureGlobalHeader />                 {/* ALWAYS first child */}
  {/* ... breadcrumb, page header, content below ... */}
</div>
```
The `FluentProvider` with `azureLightTheme` wraps the app at the root level (`src/main.tsx`).

### SRE Container
The SRE Portal page shell. Same structure, different header.
```tsx
<div className={styles.page}>
  <SREGlobalHeader />                   {/* ALWAYS first child */}
  {/* ... content below ... */}
</div>
```

**Decision rule:** The schema's `container` field (`"azure"` or `"sre"`) determines which Container pattern to use. This field is required — never omit it.

---

## @azure-fluent-storybook/components

These are imported from `@azure-fluent-storybook/components` (npm package — installed via `package.json`). Always call `getComponentsProps` from Storybook MCP to read the latest documentation before using any component.

### AzureGlobalHeader
Top-level Azure Portal navigation bar with search, notifications, user avatar.
```tsx
<AzureGlobalHeader />
```
No required props.

### SREGlobalHeader
Alternate top bar for SRE Portal pages.
```tsx
<SREGlobalHeader />
```

### AzureBreadcrumb
Breadcrumb trail above the page title.
```tsx
<AzureBreadcrumb items={[{ label: 'Home' }, { label: 'Resource', current: true }]} />
```
Props:
- `items: BreadcrumbPath[]` — `{ label: string; current?: boolean }`

### AzureServiceIcon
Renders Azure service icons from `public/azure-icons/`.
```tsx
<AzureServiceIcon name="staticapps" size={28} />
```
Props:
- `name: string` — icon file name (lowercase, matches files in `public/azure-icons/`)
- `size: number` — pixel size

### PageHeader
Title bar with icon, pin button, more-actions menu. Optionally includes `CopilotSuggestionsBar`.
```tsx
<PageHeader
  title="Resource | Page"
  subtitle="Static Web App"
  icon={<AzureServiceIcon name="staticapps" size={28} />}
  onPin={() => {}}
  onMore={() => {}}
/>
```
Props:
- `title: string` — rendered with `|` splitting bold/regular segments
- `subtitle?: string` — small text below title
- `icon?: ReactNode`
- `onPin?: () => void` — shows pin button
- `onMore?: () => void` — shows "..." button
- `copilotSuggestions?: CopilotSuggestionsBarProps`

### CommandBar
Toolbar with action buttons, grouped with dividers.
```tsx
<CommandBar
  items={[{ items: [{ key: 'refresh', label: 'Refresh', icon: <ArrowSync20Regular /> }] }]}
  farItems={[]}
  overflowItems={[]}
/>
```
Props:
- `items?: CommandBarGroup[]` — groups of `CommandBarItem` on the left
- `farItems?: CommandBarItem[]` — items pushed right
- `overflowItems?: CommandBarItem[]` — items in "..." overflow menu

`CommandBarItem`: `{ key, label, icon?, onClick?, disabled?, menuItems? }`

### SideNavigation
Left sidebar with collapsible nav items and groups.
```tsx
<SideNavigation items={navItems} />
```
Props:
- `items: NavItem[]` — `{ key, label, icon?, selected?, children?: NavItem[] }`

`NavItem` type: `{ key: string; label: string; icon?: ReactNode; selected?: boolean; children?: NavItem[] }`

### EssentialsPanel
Collapsible key-value accordion (used on resource overview pages).
```tsx
<EssentialsPanel
  leftItems={[{ label: 'Resource group', value: 'my-rg', isLink: true, labelAction: { text: 'move' } }]}
  rightItems={[{ label: 'URL', value: 'https://...', isLink: true }]}
  actions={[{ label: 'View Cost' }, { label: 'JSON View' }]}
  defaultExpanded
/>
```
Props:
- `leftItems: EssentialItem[]` — left column fields
- `rightItems?: EssentialItem[]` — right column fields
- `actions?: EssentialAction[]` — top-right action links
- `defaultExpanded?: boolean`

`EssentialItem`: `{ label, value, isLink?, onClick?, labelAction?: { text, onClick? } }`
`EssentialAction`: `{ label, onClick? }`

### PageTabs
Tab bar for switching content sections.
```tsx
<PageTabs
  tabs={[{ value: 'overview', label: 'Overview' }, { value: 'monitoring', label: 'Monitoring' }]}
  selectedValue={activeTab}
  onTabSelect={setActiveTab}
/>
```
Props:
- `tabs: PageTab[]` — `{ value, label, icon?, disabled? }`
- `selectedValue: string`
- `onTabSelect: (value: string) => void`

### FilterPill
Filter tag/chip used in filter rows.
```tsx
<FilterPill label="Status" value="Active" />
```
Props:
- `label: string`
- `value: string`

### CardButton
Clickable card in two variants.
```tsx
// Square (service shortcut)
<CardButton variant="square" icon="database" label="SQL Database" />

// Horizontal (resource card)
<CardButton
  variant="horizontal"
  icon="functionapp"
  label="Add a serverless backend"
  description="Link Azure Functions or Container App"
/>
```
Props:
- `label: string`
- `icon: string` — AzureServiceIcon name
- `variant?: 'square' | 'horizontal'` (default: square)
- `description?: string` (horizontal only)
- `external?: boolean` — show external link icon
- `tooltip?: string`
- `onClick?: () => void`

### WizardNav
Step wizard navigation for create flows.
```tsx
<WizardNav steps={[{ key: 'basics', label: 'Basics', status: 'current' }]} />
```

### ServiceFlyout
Flyout panel for service details.

---

## @fluentui/react-components

Standard Fluent UI v9 components. Commonly used:

| Component | Usage |
|-----------|-------|
| `DataGrid`, `DataGridHeader`, `DataGridBody`, `DataGridRow`, `DataGridCell`, `DataGridHeaderCell` | Data tables |
| `createTableColumn` | Column definitions |
| `Text` | Typography |
| `Link` | Hyperlinks |
| `Button` | Action buttons |
| `SearchBox` | Search inputs |
| `Input`, `Field` | Form inputs |
| `Switch` | Toggle switches |
| `Badge` | Status badges |
| `Tab`, `TabList` | Tab controls |
| `MessageBar`, `MessageBarBody` | Info/warning/error banners |
| `Card` | Content cards |
| `makeStyles` | Style definitions (CSS-in-JS) |
| `tokens` | Design tokens (colors, spacing, typography) |
| `mergeClasses` | Combine class names |

## @fluentui/react-icons

Icons follow the pattern `{Name}{Size}{Style}`:
- Size: `16`, `20`, `24`, `28`, `32`, `48`
- Style: `Regular`, `Filled`
- Common size for command bars: `20Regular`

Examples: `Add20Regular`, `Delete20Regular`, `ArrowSync20Regular`, `Save20Regular`, `Globe20Regular`
