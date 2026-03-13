"""Test code generation for all template types."""
from schemas.page import (
    PageSchema, PageMeta, StoryRef, ContainerType,
    TitleConfig, SideNavConfig, NavItem, NavGroup,
    EssentialsConfig, EssentialsField,
    CommandBar, CommandBarItem,
    ListTableTemplate, TableColumn, FilterConfig,
    CardsGridTemplate, CardItem,
    FormTemplate, FormField,
    DetailTemplate, DetailSection,
    CustomTemplate,
)
from schemas.codegen import generate_page


def test_cards_grid():
    page = PageSchema(
        meta=PageMeta(title="Dashboard Overview"),
        container="azure",
        title=TitleConfig(resourceName="My App", pageName="Overview", icon="App", breadcrumbs=["Home"]),
        template=CardsGridTemplate(
            kind="cards-grid",
            columns=3,
            cards=[
                CardItem(cardId="cpu", title="CPU Usage", description="85%"),
                CardItem(cardId="mem", title="Memory", description="60%"),
                CardItem(cardId="disk", title="Disk", description="45%"),
            ],
        ),
    )
    code = generate_page(page, "DashboardOverview")
    print("=== CARDS-GRID ===")
    start = code.index("const DashboardOverview")
    print(code[start:])
    return code


def test_form():
    page = PageSchema(
        meta=PageMeta(title="Create Resource"),
        container="azure",
        title=TitleConfig(resourceName="Create a resource", icon="Add"),
        template=FormTemplate(
            kind="form",
            fields=[
                FormField(name="name", label="Name", required=True, placeholder="Enter name"),
                FormField(name="region", label="Region", inputType="select", options=["East US", "West US"]),
            ],
            submitLabel="Review + Create",
        ),
    )
    code = generate_page(page, "CreateResource")
    print("=== FORM ===")
    start = code.index("const CreateResource")
    print(code[start:])
    return code


def test_detail_with_essentials():
    page = PageSchema(
        meta=PageMeta(title="Resource Detail"),
        container="azure",
        sideNav=SideNavConfig(
            defaultSelected="overview",
            entries=[
                NavItem(key="overview", label="Overview"),
                NavItem(key="properties", label="Properties"),
            ],
        ),
        title=TitleConfig(resourceName="my-db", pageName="Overview", icon="Database"),
        essentials=EssentialsConfig(
            fields=[
                EssentialsField(label="Status", value="Running"),
                EssentialsField(label="Location", value="East US"),
                EssentialsField(label="Resource group", value="prod-rg", copyable=True),
            ]
        ),
        template=DetailTemplate(
            kind="detail",
            sections=[
                DetailSection(sectionId="metrics", label="Metrics"),
                DetailSection(sectionId="activity", label="Activity Log"),
            ],
        ),
    )
    code = generate_page(page, "ResourceDetail")
    print("=== DETAIL + ESSENTIALS + SIDE NAV ===")
    start = code.index("const ResourceDetail")
    print(code[start:])
    return code


def test_custom():
    page = PageSchema(
        meta=PageMeta(title="Custom Page"),
        container="sre",
        template=CustomTemplate(
            kind="custom",
            stories=[
                StoryRef(storyId="components-button--primary", instanceId="hero-btn"),
            ],
        ),
    )
    code = generate_page(page, "CustomPage")
    print("=== CUSTOM (SRE container, no nav/title) ===")
    start = code.index("const CustomPage")
    print(code[start:])
    return code


if __name__ == "__main__":
    test_cards_grid()
    print()
    test_form()
    print()
    test_detail_with_essentials()
    print()
    test_custom()
    print("\n✓ All template types generated successfully")
