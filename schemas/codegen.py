"""Generate a plain React .tsx page component from a validated PageSchema.

Maps the six PageSchema questions to actual React component code using
the shared component library (AzureGlobalHeader, SREGlobalHeader,
PageHeader, SideNavigation, CommandBar, EssentialsPanel, etc.).
"""

from __future__ import annotations

from schemas.page import (
    PageSchema, ContainerType,
    ListTableTemplate, FormTemplate, CardsGridTemplate,
    DetailTemplate, CustomTemplate,
)

COMPONENT_ROOT = "@azure-fluent-storybook/components"


def _js_str(value: str) -> str:
    """Escape single quotes so the value is safe inside a JS '…' string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _indent(text: str, level: int = 1) -> str:
    """Indent each line by `level` × 2 spaces."""
    prefix = "  " * level
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())


def _nav_items_code(nav) -> str:
    """Generate NavItem[] literal from SideNavConfig."""
    lines: list[str] = []
    for entry in nav.entries:
        if entry.kind == "group":
            children = ", ".join(
                f"{{ key: '{_js_str(i.key)}', label: '{_js_str(i.label)}'{f', icon: <AzureServiceIcon name=\"{i.icon.lower()}\" size={{18}} />' if i.icon else ''} }}"
                for i in entry.items
            )
            lines.append(
                f"{{ key: '{_js_str(entry.label.lower().replace(' ', '-'))}', label: '{_js_str(entry.label)}', children: [{children}] }}"
            )
        else:
            selected = ", selected: true" if entry.key == nav.default_selected else ""
            icon_part = f", icon: <AzureServiceIcon name=\"{entry.icon.lower()}\" size={{18}} />" if entry.icon else ""
            lines.append(f"{{ key: '{_js_str(entry.key)}', label: '{_js_str(entry.label)}'{icon_part}{selected} }}")
    return "[\n" + ",\n".join(f"    {l}" for l in lines) + ",\n  ]"


def _command_bar_code(cmd_bar) -> str:
    """Generate CommandBar items prop from CommandBar schema."""
    groups: list[list[str]] = [[]]
    for item in cmd_bar.items:
        if item.is_separator:
            groups.append([])
        else:
            ref = item.story
            overrides = ref.arg_overrides
            label = overrides.get("label", overrides.get("text", "Action"))
            icon = overrides.get("icon", "")
            icon_part = f", icon: <{icon}20Regular />" if icon else ""
            groups[-1].append(f"{{ key: '{_js_str(ref.instance_id)}', label: '{_js_str(label)}'{icon_part} }}")

    group_strs = []
    for g in groups:
        items = ", ".join(g)
        group_strs.append(f"{{ items: [{items}] }}")
    return "[" + ", ".join(group_strs) + "]"


def _icon_imports(page: PageSchema) -> set[str]:
    """Collect Fluent icon imports needed by the command bar."""
    icons: set[str] = set()
    if page.command_bar:
        for item in page.command_bar.items:
            if item.story:
                icon = item.story.arg_overrides.get("icon", "")
                if icon:
                    icons.add(f"{icon}20Regular")
    return icons


def _essentials_code(ess) -> str:
    """Generate EssentialsPanel props from EssentialsConfig."""
    items = []
    for f in ess.fields:
        parts = [f"label: '{_js_str(f.label)}'", f"value: '{_js_str(f.value)}'"]
        if f.link:
            parts.append("isLink: true")
        items.append("{ " + ", ".join(parts) + " }")
    return ", ".join(items)


def _table_columns_code(tpl: ListTableTemplate) -> str:
    """Generate column definitions for a DataGrid."""
    cols = []
    for col in tpl.columns:
        render = {
            "text": f"(item) => <Text>{{item.{col.key}}}</Text>",
            "date": f"(item) => <Text>{{item.{col.key}}}</Text>",
            "badge": f"(item) => <Text>{{item.{col.key}}}</Text>",
            "link": f"(item) => <Link>{{item.{col.key}}}</Link>",
            "toggle": f"(item) => item.{col.key} === 'On' ? <Switch checked /> : <Text>{{item.{col.key}}}</Text>",
        }.get(col.column_type.value, f"(item) => <Text>{{item.{col.key}}}</Text>")

        cols.append(
            f"createTableColumn({{\n"
            f"      columnId: '{_js_str(col.key)}',\n"
            f"      renderHeaderCell: () => '{_js_str(col.header)}',\n"
            f"      renderCell: {render},\n"
            f"    }})"
        )
    return "[\n    " + ",\n    ".join(cols) + ",\n  ]"


def _template_body(tpl) -> list[str]:
    """Generate the content area JSX lines for the template (zero-indent)."""
    lines: list[str] = []

    if isinstance(tpl, ListTableTemplate):
        if tpl.description:
            lines.append(f'<Text className={{styles.description}}>{tpl.description}</Text>')

        if tpl.filters.searchable or tpl.filters.add_filters:
            lines.append('<div className={styles.filterRow}>')
            if tpl.filters.searchable:
                lines.append(
                    f'  <SearchBox placeholder="{tpl.filters.search_placeholder}" '
                    f'style={{{{ minWidth: 200 }}}} />'
                )
            if tpl.filters.add_filters:
                lines.append('  <FilterPill />')
            lines.append('</div>')

        lines.extend([
            '<div className={styles.gridWrapper}>',
            '  <DataGrid',
            '    items={items}',
            '    columns={columns}',
            '    sortable',
            '    getRowId={(item) => item.id}',
            '  >',
            '    <DataGridHeader>',
            '      <DataGridRow>',
            '        {({ renderHeaderCell }) => <DataGridHeaderCell>{renderHeaderCell()}</DataGridHeaderCell>}',
            '      </DataGridRow>',
            '    </DataGridHeader>',
            '    <DataGridBody<Item>>',
            '      {({ item, rowId }) => (',
            '        <DataGridRow<Item> key={rowId}>',
            '          {({ renderCell }) => <DataGridCell>{renderCell(item)}</DataGridCell>}',
            '        </DataGridRow>',
            '      )}',
            '    </DataGridBody>',
            '  </DataGrid>',
            '</div>',
        ])

    elif isinstance(tpl, CardsGridTemplate):
        lines.append('<div className={styles.cardsGrid}>')
        for card in tpl.cards:
            lines.extend([
                '  <Card style={{ padding: 16 }}>',
                f'    <Text weight="semibold">{card.title}</Text>',
                f'    <Text>{card.description}</Text>',
                '  </Card>',
            ])
        lines.append('</div>')

    elif isinstance(tpl, DetailTemplate):
        for section in tpl.sections:
            lines.extend([
                '<div className={styles.section}>',
                f'  <Text weight="semibold" size={{400}}>{section.label}</Text>',
                '</div>',
            ])

    elif isinstance(tpl, FormTemplate):
        lines.append('<form className={styles.form}>')
        for field in tpl.fields:
            lines.extend([
                f'  <Field label="{field.label}" required={{{str(field.required).lower()}}}>',
                f'    <Input placeholder="{field.placeholder}" />',
                '  </Field>',
            ])
        lines.append(f'  <Button appearance="primary">{tpl.submit_label}</Button>')
        lines.append('</form>')

    else:
        lines.append('<Text>Custom content area</Text>')

    return lines


def generate_page(page: PageSchema, component_name: str = "GeneratedPage") -> str:
    """
    Generate a complete React .tsx page component from a PageSchema.

    Returns the full file content as a string.
    """
    meta_title = page.meta.title or component_name

    # Determine global header
    if page.container == ContainerType.AZURE:
        header_import = "AzureGlobalHeader"
        header_jsx = "<AzureGlobalHeader />"
    else:
        header_import = "SREGlobalHeader"
        header_jsx = "<SREGlobalHeader />"

    # Collect imports
    component_imports = {header_import}
    fluent_imports = {"makeStyles", "tokens", "Text"}
    icon_imports = _icon_imports(page)

    if page.title:
        component_imports.add("PageHeader")
        component_imports.add("AzureServiceIcon")
    if page.side_nav:
        component_imports.add("SideNavigation")
    if page.command_bar:
        component_imports.add("CommandBar")
    if page.essentials:
        component_imports.add("EssentialsPanel")

    if page.title and page.title.breadcrumbs:
        component_imports.add("AzureBreadcrumb")

    tpl = page.template
    if isinstance(tpl, ListTableTemplate):
        fluent_imports.update({
            "DataGrid", "DataGridHeader", "DataGridHeaderCell",
            "DataGridBody", "DataGridRow", "DataGridCell",
            "createTableColumn",
        })
        if tpl.filters.searchable:
            fluent_imports.add("SearchBox")
        if tpl.filters.add_filters:
            component_imports.add("FilterPill")
        if any(c.column_type.value == "link" for c in tpl.columns):
            fluent_imports.add("Link")
        if any(c.column_type.value == "toggle" for c in tpl.columns):
            fluent_imports.add("Switch")
    if isinstance(tpl, FormTemplate):
        fluent_imports.update({"Input", "Button", "Field"})

    # Build the render body — separate header parts from content parts.
    # Header: breadcrumb, page title, essentials (full-width, above side nav).
    # Content: command bar, template (inside side nav scrollable area).
    header_lines: list[str] = []
    content_lines: list[str] = []

    # Breadcrumb → header
    if page.title and page.title.breadcrumbs:
        crumbs = ", ".join(
            f"{{ label: '{_js_str(b)}'{', current: true' if i == len(page.title.breadcrumbs) - 1 else ''} }}"
            for i, b in enumerate(page.title.breadcrumbs)
        )
        header_lines.append(f"<AzureBreadcrumb items={{[{crumbs}]}} />")

    # Page header → header
    if page.title:
        title_str = page.title.resource_name
        if page.title.page_name:
            title_str += f" | {page.title.page_name}"
        icon_jsx = f'icon={{<AzureServiceIcon name="{page.title.icon.lower()}" size={{28}} />}}' if page.title.icon else ""
        more_jsx = "onMore={() => {}}" if page.title.more_actions else ""
        pin_jsx = "onPin={() => {}}" if page.title.closable else ""
        props = [f'title="{title_str}"']
        if icon_jsx:
            props.append(icon_jsx)
        if pin_jsx:
            props.append(pin_jsx)
        if more_jsx:
            props.append(more_jsx)
        header_lines.append(f"<PageHeader {' '.join(props)} />")

    # Essentials → header (full-width, above side nav)
    if page.essentials:
        ess_code = _essentials_code(page.essentials)
        expanded = "true" if page.essentials.expanded else "false"
        header_lines.append(
            f"<EssentialsPanel\n"
            f"  leftItems={{[{ess_code}]}}\n"
            f"  defaultExpanded={{{expanded}}}\n"
            f"/>"
        )

    # Command bar → content
    if page.command_bar:
        items_code = _command_bar_code(page.command_bar)
        content_lines.append(f"<CommandBar items={{{items_code}}} />")

    # Template content lines (zero-indented)
    template_lines = _template_body(tpl)

    # ── Compose the full render body ──
    has_side_nav = page.side_nav is not None

    if has_side_nav:
        nav_code = _nav_items_code(page.side_nav)
        jsx_lines = ['<div className={styles.headerSection}>']
        for line in header_lines:
            jsx_lines.extend(f"  {l}" for l in line.splitlines())
        jsx_lines.append('</div>')
        jsx_lines.append('<div className={styles.body}>')
        jsx_lines.append('  <SideNavigation items={navItems} />')
        jsx_lines.append('  <div className={styles.content}>')
        for line in content_lines:
            jsx_lines.extend(f"    {l}" for l in line.splitlines())
        for line in template_lines:
            jsx_lines.append(f"    {line}")
        jsx_lines.append('  </div>')
        jsx_lines.append('</div>')
    else:
        jsx_lines = ['<div className={styles.content}>']
        for line in header_lines:
            jsx_lines.extend(f"  {l}" for l in line.splitlines())
        for line in content_lines:
            jsx_lines.extend(f"  {l}" for l in line.splitlines())
        for line in template_lines:
            jsx_lines.append(f"  {line}")
        jsx_lines.append('</div>')

    # Indent everything to the render() context (6 spaces base = inside <div className={styles.page}>)
    content_jsx = "\n".join(f"      {line}" for line in jsx_lines)

    # Format icon imports
    icon_import_line = ""
    if icon_imports:
        icon_import_line = f"\nimport {{\n  {',{0}  '.format(chr(10)).join(sorted(icon_imports))},\n}} from '@fluentui/react-icons';"

    nav_const = ""
    if has_side_nav:
        nav_const = f"\nconst navItems: NavItem[] = {nav_code};\n"
        component_imports.add("AzureServiceIcon")

    table_defs = ""
    if isinstance(tpl, ListTableTemplate):
        col_code = _table_columns_code(tpl)
        # Type definition for items
        type_fields = ", ".join(f"{c.key}: string" for c in tpl.columns)
        table_defs = (
            f"\ntype Item = {{ id: string; {type_fields} }};\n\n"
            f"const items: Item[] = []; // TODO: populate with real data\n\n"
            f"const columns = {col_code};\n"
        )

    nav_type_import = ""
    if has_side_nav:
        nav_type_import = f"\nimport type {{ NavItem }} from '{COMPONENT_ROOT}';"

    # Styles
    styles_block = """const useStyles = makeStyles({
  page: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: tokens.colorNeutralBackground1,
  },
  headerSection: {
    display: 'flex',
    flexDirection: 'column',
    flexShrink: 0,
  },
  body: {
    display: 'flex',
    flex: 1,
    overflow: 'hidden',
  },
  content: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'auto',
    minWidth: 0,
  },"""

    if isinstance(tpl, ListTableTemplate):
        styles_block += """
  description: {
    padding: '12px 16px',
    fontSize: tokens.fontSizeBase300,
    color: tokens.colorNeutralForeground2,
  },
  filterRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    flexShrink: 0,
  },
  gridWrapper: {
    flex: 1,
    overflow: 'auto',
    minHeight: 0,
  },"""

    if isinstance(tpl, CardsGridTemplate):
        styles_block += f"""
  cardsGrid: {{
    display: 'grid',
    gridTemplateColumns: 'repeat({tpl.columns}, 1fr)',
    gap: '16px',
    padding: '16px',
  }},"""

    if isinstance(tpl, FormTemplate):
        styles_block += """
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    padding: '24px',
    maxWidth: '600px',
  },"""

    if isinstance(tpl, DetailTemplate):
        styles_block += """
  section: {
    padding: '16px 24px',
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },"""

    styles_block += "\n});"

    # Assemble the file
    code = f"""import React from 'react';
import {{
  {',{0}  '.format(chr(10)).join(sorted(fluent_imports))},
}} from '@fluentui/react-components';{icon_import_line}
import {{
  {',{0}  '.format(chr(10)).join(sorted(component_imports))},
}} from '{COMPONENT_ROOT}';{nav_type_import}

// ─── Styles ──────────────────────────────────────────────────────

{styles_block}

// ─── Data ────────────────────────────────────────────────────────
{nav_const}{table_defs}
// ─── Component ───────────────────────────────────────────────────

const {component_name}: React.FC = () => {{
  const styles = useStyles();
  return (
    <div className={{styles.page}}>
      {header_jsx}
{content_jsx}
    </div>
  );
}};

export default {component_name};
"""
    return code
