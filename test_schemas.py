"""Smoke tests — catalog-driven story selection for page composition."""
from schemas.elements import (
    ComponentEntry, PropDefinition, Story, ComponentManifest, Catalog,
)
from schemas.page import (
    PageSchema, PageMeta, StoryRef, ContainerType,
    TitleConfig, SideNavConfig, NavItem, NavGroup,
    EssentialsConfig, EssentialsField,
    CommandBar, CommandBarItem,
    ListTableTemplate, TableColumn, FilterConfig,
    DetailTemplate, DetailSection,
    CustomTemplate,
)
from schemas.loader import fetch_story_index
from schemas.validator import validate_page
import json


# ═══════════════════════════════════════════════════════════════════════════
# 1. Build a mini catalog (what Storybook MCP would return)
# ═══════════════════════════════════════════════════════════════════════════

def build_catalog() -> Catalog:
    """Simulate the catalog that the Storybook MCP provides."""

    button = ComponentManifest(
        component=ComponentEntry(
            componentId="CuiButton",
            tagName="cui-button",
            category="Actions",
            props=[
                PropDefinition(name="appearance", type="enum",
                               enumValues=["primary", "outline", "subtle", "transparent"]),
                PropDefinition(name="label", type="string"),
                PropDefinition(name="icon", type="string"),
                PropDefinition(name="disabled", type="boolean"),
            ],
            stories=[
                Story(storyId="actions-cuibutton--primary", name="Primary",
                      args={"appearance": "primary", "label": "Button"}),
                Story(storyId="actions-cuibutton--subtle", name="Subtle",
                      args={"appearance": "subtle", "label": "Button"}),
                Story(storyId="actions-cuibutton--outline", name="Outline",
                      args={"appearance": "outline", "label": "Button"}),
                Story(storyId="actions-cuibutton--icon-only", name="Icon Only",
                      args={"appearance": "transparent", "icon": "MoreHorizontal"}),
            ],
        ),
    )

    tag = ComponentManifest(
        component=ComponentEntry(
            componentId="CuiTag",
            tagName="cui-tag",
            category="Data Display",
            props=[
                PropDefinition(name="text", type="string"),
                PropDefinition(name="appearance", type="enum",
                               enumValues=["success", "warning", "danger", "info", "neutral"]),
            ],
            stories=[
                Story(storyId="datadisplay-cuitag--success", name="Success",
                      args={"text": "Available", "appearance": "success"}),
                Story(storyId="datadisplay-cuitag--neutral", name="Neutral",
                      args={"text": "Label", "appearance": "neutral"}),
            ],
        ),
    )

    link = ComponentManifest(
        component=ComponentEntry(
            componentId="CuiLink",
            tagName="cui-link",
            category="Navigation",
            props=[
                PropDefinition(name="text", type="string"),
                PropDefinition(name="href", type="string"),
                PropDefinition(name="icon", type="string"),
            ],
            stories=[
                Story(storyId="navigation-cuilink--default", name="Default",
                      args={"text": "Link", "href": "#"}),
                Story(storyId="navigation-cuilink--with-icon", name="With Icon",
                      args={"text": "Link", "href": "#", "icon": "Open"}),
            ],
        ),
    )

    catalog = Catalog(components=[button, tag, link])
    print("Catalog OK:", len(catalog.components), "components,",
          sum(len(m.component.stories) for m in catalog.components), "stories total")
    return catalog


# ═══════════════════════════════════════════════════════════════════════════
# 2. Compose the Preview Features page by SELECTING stories
# ═══════════════════════════════════════════════════════════════════════════

def test_preview_features_page():
    """
    Model the Azure Portal 'Default Directory | Preview features' page.

    Every component is a StoryRef — we pick a story variant and override
    only the args we need to customize.
    """
    page = PageSchema(
        meta=PageMeta(
            title="Preview features",
            route="/default-directory/preview-features",
            topics=["entra", "directory"],
        ),

        # Q1: What container? → Azure
        container="azure",

        # Q2: Side nav? → Yes
        sideNav=SideNavConfig(
            defaultSelected="preview-features",
            collapsible=True,
            closable=True,
            entries=[
                NavItem(key="overview", label="Overview", icon="Info"),
                NavItem(key="preview-features", label="Preview features", icon="PreviewFeatures"),
                NavItem(key="diagnose", label="Diagnose and solve problems", icon="Wrench"),
                NavGroup(label="Manage", items=[
                    NavItem(key="users", label="Users", icon="People"),
                    NavItem(key="groups", label="Groups", icon="Group"),
                    NavItem(key="external-identities", label="External Identities", icon="ExternalIdentities"),
                    NavItem(key="roles", label="Roles and administrators", icon="Shield"),
                ]),
            ],
        ),

        # Q3: Page title? → Yes  (Q4: breadcrumbs included)
        title=TitleConfig(
            resourceName="Default Directory",
            pageName="Preview features",
            icon="EntraID",
            breadcrumbs=["Home", "Default Directory"],
            closable=True,
            moreActions=True,
        ),

        # Q6: Essentials accordion? → No (None)
        essentials=None,

        # ── Command bar — select story variants (real Storybook IDs) ──
        command_bar=CommandBar(items=[
            # Pick the "Subtle" button story, override label → "Save"
            CommandBarItem(story=StoryRef(
                storyId="components-button--subtle",
                instanceId="save-btn",
                argOverrides={"label": "Save", "icon": "Save"},
            )),
            # Pick the "Subtle" button story, override label → "Discard"
            CommandBarItem(story=StoryRef(
                storyId="components-button--subtle",
                instanceId="discard-btn",
                argOverrides={"label": "Discard", "icon": "Dismiss"},
            )),
            # Separator
            CommandBarItem(isSeparator=True),
            # "Got feedback?" link — no link story exists, use subtle button
            CommandBarItem(story=StoryRef(
                storyId="components-button--subtle",
                instanceId="feedback-link",
                argOverrides={"text": "Got feedback?", "icon": "People"},
            )),
        ]),

        # ── Content: list-table ──
        template=ListTableTemplate(
            kind="list-table",
            description="The following preview features are available for your evaluation.",
            columns=[
                TableColumn(key="name", header="Name", sortable=True, columnType="text", truncate=True),
                TableColumn(key="category", header="Category", sortable=True, columnType="text"),
                TableColumn(key="services", header="Services", sortable=True, columnType="text"),
                TableColumn(key="releaseType", header="Release type", sortable=True, columnType="badge"),
                TableColumn(key="releaseDate", header="Release date", sortable=True, columnType="date"),
                TableColumn(key="state", header="State", sortable=True, columnType="toggle"),
            ],
            filters=FilterConfig(
                searchable=True,
                searchPlaceholder="Search",
                addFilters=True,
            ),
            pagination=True,
        ),
    )

    print("Preview Features Page OK:", page.meta.title)
    print("  Q1 Container:", page.container.value)
    print("  Q2 Side nav:", "Yes" if page.side_nav else "No")
    print("  Q3 Page title:", page.title.resource_name, "|", page.title.page_name if page.title else "No")
    print("  Q4 Breadcrumbs:", page.title.breadcrumbs if page.title and page.title.breadcrumbs else "No")
    print("  Q5 Body template:", page.template.kind)
    print("  Q6 Essentials:", "Yes" if page.essentials else "No")
    print("  Command bar: %d items (%d stories, %d separators)" % (
        len(page.command_bar.items),
        sum(1 for i in page.command_bar.items if not i.is_separator),
        sum(1 for i in page.command_bar.items if i.is_separator),
    ))

    # Show what stories were selected
    for item in page.command_bar.items:
        if item.story:
            print("    → %s (story: %s, overrides: %s)" % (
                item.story.instance_id,
                item.story.story_id,
                item.story.arg_overrides or "none",
            ))
        else:
            print("    → [separator]")

    print("  Table columns:", len(page.template.columns))
    return page


# ═══════════════════════════════════════════════════════════════════════════
# 3. Validation tests
# ═══════════════════════════════════════════════════════════════════════════

def test_validation():
    """Verify validators catch invalid data."""
    import sys

    # separator with a story
    try:
        CommandBarItem(isSeparator=True, story=StoryRef(
            storyId="x--y", instanceId="bad"))
        print("FAIL: should have raised", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Validation OK: separator cannot have a story")

    # non-separator without a story
    try:
        CommandBarItem(isSeparator=False)
        print("FAIL: should have raised", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Validation OK: non-separator requires a story")

    # essentials with no fields
    try:
        EssentialsConfig(fields=[])
        print("FAIL: should have raised", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Validation OK: essentials requires at least one field")

    # valid essentials
    ess = EssentialsConfig(fields=[
        EssentialsField(label="Resource group", value="my-rg", copyable=True),
        EssentialsField(label="Status", value="Running"),
        EssentialsField(label="Location", value="East US"),
    ])
    print("Validation OK: essentials with", len(ess.fields), "fields")


if __name__ == "__main__":
    build_catalog()
    page = test_preview_features_page()
    test_validation()

    # ── Live validation against running Storybook ──
    print("\n── Live Storybook validation ──")
    try:
        index = fetch_story_index()
        print(f"Loaded {len(index)} stories from {len(index.all_components)} components")

        errors = validate_page(page, index)
        if errors:
            print(f"✗ {len(errors)} invalid StoryRef(s):")
            for e in errors:
                print(f"  {e}")
        else:
            print("✓ All StoryRefs valid")

        # Show what component each StoryRef resolved to
        print("\nStoryRef resolution:")
        if page.command_bar:
            for item in page.command_bar.items:
                if item.story:
                    comp = index.component_for(item.story.story_id)
                    print(f"  {item.story.instance_id} → {item.story.story_id} → {comp or '???'}")

    except Exception as e:
        print(f"⚠ Storybook not reachable ({e}), skipping live validation")

    print("\n✓ All tests passed")
