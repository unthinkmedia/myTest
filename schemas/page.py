"""Pydantic schemas for composing pages from Storybook stories.

The PageSchema answers six questions:

    1. What container?        →  "azure" or "sre"
    2. Side nav?              →  SideNavConfig or None
    3. Page title?            →  TitleConfig or None
    4. Breadcrumbs?           →  list inside TitleConfig (if title exists)
    5. What body template?    →  ContentTemplate (list-table, form, cards-grid, …)
    6. Essentials accordion?  →  EssentialsConfig or None (key-value pairs above body)

Every component on the page is a StoryRef — a pointer to an existing
Storybook story (variant) with optional arg overrides.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, model_validator


# ═══════════════════════════════════════════════════════════════════════════
# StoryRef — select a story variant from the Storybook catalog
# ═══════════════════════════════════════════════════════════════════════════

class StoryRef(BaseModel):
    """
    A reference to a specific Storybook story (variant).

    Points at an existing story by its ID and optionally overrides
    args to tweak the variant for this specific usage.  The story
    already carries the component, its default args, and its visual
    state — you just pick it and adjust.

    Example: select the "Subtle" button story, override label text:
        StoryRef(
            storyId="components-cuibutton--subtle",
            argOverrides={"label": "Save"},
        )
    """
    story_id: str = Field(
        ...,
        alias="storyId",
        min_length=1,
        description="Storybook story ID, e.g. 'components-cuibutton--primary'",
    )
    instance_id: str = Field(
        ...,
        alias="instanceId",
        min_length=1,
        description="Unique placement ID within this page, e.g. 'save-btn'",
    )
    arg_overrides: dict[str, Any] = Field(
        default_factory=dict,
        alias="argOverrides",
        description="Override specific args from the story defaults",
    )
    css_overrides: dict[str, str] = Field(
        default_factory=dict,
        alias="cssOverrides",
        description="CSS custom property overrides for this instance",
    )
    slot_children: dict[str, list[str]] = Field(
        default_factory=dict,
        alias="slotChildren",
        description="Slot name → list of child instance IDs",
    )

    model_config = {"populate_by_name": True}


# ═══════════════════════════════════════════════════════════════════════════
# Container Layout — the page shell
# ═══════════════════════════════════════════════════════════════════════════

# --- Side navigation ---

class NavItem(BaseModel):
    """A clickable leaf item in the side navigation."""
    kind: Literal["item"] = "item"
    key: str = Field(..., min_length=1, description="Unique key for this nav item")
    label: str = Field(..., min_length=1)
    icon: str = Field("", description="Icon name, e.g. 'Home', 'Settings'")
    route: str = Field("", description="Route this item navigates to")


class NavGroup(BaseModel):
    """
    A non-clickable section header that groups nav items beneath it.

    Example: "Manage" groups Users, Groups, Roles, etc.
    """
    kind: Literal["group"] = "group"
    label: str = Field(..., min_length=1, description="Section header text, e.g. 'Manage'")
    items: list[NavItem] = Field(..., min_length=1, description="Items within this group")


# Discriminated union — top-level nav entries are either items or groups
NavEntry = Annotated[
    Union[NavItem, NavGroup],
    Field(discriminator="kind"),
]


class SideNavConfig(BaseModel):
    """Configuration for the side navigation panel."""
    entries: list[NavEntry] = Field(
        ...,
        min_length=1,
        description="Ordered nav entries — items or group headers",
    )
    default_selected: str = Field(
        ...,
        alias="defaultSelected",
        min_length=1,
        description="Key of the initially selected nav item",
    )
    width: int = Field(220, ge=120, le=400, description="Side nav width in pixels")
    collapsible: bool = Field(True, description="Whether the side nav can be collapsed")
    closable: bool = Field(False, description="Whether the side nav shows a close (X) button")

    model_config = {"populate_by_name": True}


# --- Title bar ---

class TitleConfig(BaseModel):
    """
    Configuration for the page title / header bar.

    Azure Portal pattern: "Resource Name | Page Name"
    e.g. "Default Directory | Preview features"
    """
    resource_name: str = Field(
        ...,
        alias="resourceName",
        min_length=1,
        description="Primary resource name, e.g. 'Default Directory'",
    )
    page_name: str = Field(
        "",
        alias="pageName",
        description="Sub-page name after the '|', e.g. 'Preview features'. "
                    "Derived from selected nav item if empty.",
    )
    icon: str = Field("", description="Icon displayed next to the title")
    breadcrumbs: list[str] = Field(
        default_factory=list,
        description="Breadcrumb trail, e.g. ['Home', 'Default Directory']",
    )
    closable: bool = Field(False, description="Show a close (X) button on the far right")
    more_actions: bool = Field(
        False,
        alias="moreActions",
        description="Show a '…' overflow menu next to the title",
    )

    model_config = {"populate_by_name": True}


# --- Container type ---

class ContainerType(str, Enum):
    """Which application shell / frame wraps the page."""
    AZURE = "azure"
    SRE = "sre"


# ═══════════════════════════════════════════════════════════════════════════
# Essentials accordion — key-value summary panel above the body
# ═══════════════════════════════════════════════════════════════════════════

class EssentialsField(BaseModel):
    """A single key-value row in the Essentials accordion."""
    label: str = Field(..., min_length=1, description="Field label, e.g. 'Resource group'")
    value: str = Field(..., description="Display value, e.g. 'my-rg'")
    copyable: bool = Field(False, description="Show a copy-to-clipboard button")
    link: str = Field("", description="Makes the value a clickable link")


class EssentialsConfig(BaseModel):
    """
    Collapsible accordion of key-value pairs shown above the body template.

    Azure Portal pattern: appears on resource overview pages with fields
    like Resource group, Status, Location, Subscription, etc.
    """
    fields: list[EssentialsField] = Field(
        ...,
        min_length=1,
        description="Key-value rows displayed in the essentials panel",
    )
    expanded: bool = Field(True, description="Whether the accordion starts open")


# ═══════════════════════════════════════════════════════════════════════════
# Command Bar — toolbar between title and content
# ═══════════════════════════════════════════════════════════════════════════

class CommandBarItem(BaseModel):
    """
    A single item in the command bar.

    Each item is a StoryRef — select the right button/link story variant.
    Separators are modeled as a special story or a sentinel.
    """
    story: StoryRef | None = Field(
        None,
        description="Story reference for this item (None = separator)",
    )
    is_separator: bool = Field(
        False,
        alias="isSeparator",
        description="If true, renders a visual divider instead of a component",
    )

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def _validate_separator_or_story(self) -> CommandBarItem:
        if self.is_separator and self.story is not None:
            raise ValueError("A separator cannot also have a story reference")
        if not self.is_separator and self.story is None:
            raise ValueError("Non-separator items must have a story reference")
        return self


class CommandBar(BaseModel):
    """
    Toolbar rendered between the title bar and the content area.

    Contains story-backed buttons/links and separators.
    Example: [Save] [Discard] | Got feedback?
    """
    items: list[CommandBarItem] = Field(..., min_length=1)


# ═══════════════════════════════════════════════════════════════════════════
# Content Templates — what fills the content area
# ═══════════════════════════════════════════════════════════════════════════

# --- Table ---

class ColumnType(str, Enum):
    """How a table column renders its cell values."""
    TEXT = "text"
    DATE = "date"
    BADGE = "badge"
    LINK = "link"
    TOGGLE = "toggle"


class TableColumn(BaseModel):
    """Column definition for a table template."""
    key: str = Field(..., min_length=1)
    header: str = Field(..., min_length=1, description="Column header text")
    column_type: ColumnType = Field(
        ColumnType.TEXT,
        alias="columnType",
        description="Cell renderer type",
    )
    sortable: bool = Field(False)
    filterable: bool = Field(False, description="Include this column in the 'Add filters' panel")
    width: str = Field("", description="CSS width, e.g. '200px' or '1fr'")
    truncate: bool = Field(False, description="Truncate long text with ellipsis")

    model_config = {"populate_by_name": True}


class FilterConfig(BaseModel):
    """Configuration for the search/filter toolbar above a table."""
    searchable: bool = Field(False, description="Show a search input")
    search_placeholder: str = Field(
        "Search",
        alias="searchPlaceholder",
    )
    add_filters: bool = Field(
        False,
        alias="addFilters",
        description="Show an 'Add filters' button",
    )

    model_config = {"populate_by_name": True}


class ListTableTemplate(BaseModel):
    """Template: data table / list view with optional search and filters."""
    kind: Literal["list-table"] = "list-table"
    description: str = Field(
        "",
        description="Informational text displayed above the table",
    )
    columns: list[TableColumn] = Field(..., min_length=1)
    filters: FilterConfig = Field(
        default_factory=FilterConfig,
        description="Search and filter toolbar above the table",
    )
    pagination: bool = Field(True)
    row_actions: list[StoryRef] = Field(
        default_factory=list,
        alias="rowActions",
        description="Story-backed action components rendered per row",
    )

    model_config = {"populate_by_name": True}


# --- Form ---

class FormField(BaseModel):
    """A single field in a form template."""
    name: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    input_type: str = Field(
        "text",
        alias="inputType",
        description="Input type: text, number, select, checkbox, textarea, etc.",
    )
    required: bool = Field(False)
    placeholder: str = Field("")
    options: list[str] = Field(
        default_factory=list,
        description="Options for select / radio inputs",
    )

    model_config = {"populate_by_name": True}


class FormTemplate(BaseModel):
    """Template: form / create / edit view."""
    kind: Literal["form"] = "form"
    description: str = Field("")
    fields: list[FormField] = Field(..., min_length=1)
    submit_label: str = Field("Submit", alias="submitLabel")
    cancel_label: str = Field("Cancel", alias="cancelLabel")

    model_config = {"populate_by_name": True}


# --- Cards grid ---

class CardItem(BaseModel):
    """A card definition for the cards-grid template."""
    card_id: str = Field(..., alias="cardId", min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field("")
    icon: str = Field("")
    stories: list[StoryRef] = Field(
        default_factory=list,
        description="Story-backed components rendered inside this card",
    )

    model_config = {"populate_by_name": True}


class CardsGridTemplate(BaseModel):
    """Template: grid of cards (dashboard, overview KPIs, etc.)."""
    kind: Literal["cards-grid"] = "cards-grid"
    description: str = Field("")
    columns: int = Field(3, ge=1, le=6, description="Number of grid columns")
    cards: list[CardItem] = Field(..., min_length=1)


# --- Detail ---

class DetailSection(BaseModel):
    """A section inside a detail/overview template."""
    section_id: str = Field(..., alias="sectionId", min_length=1)
    label: str = Field(..., min_length=1)
    stories: list[StoryRef] = Field(
        default_factory=list,
        description="Story-backed components in this section",
    )

    model_config = {"populate_by_name": True}


class DetailTemplate(BaseModel):
    """Template: detail / overview page (properties, metrics, etc.)."""
    kind: Literal["detail"] = "detail"
    description: str = Field("")
    sections: list[DetailSection] = Field(..., min_length=1)


# --- Custom ---

class CustomTemplate(BaseModel):
    """Template: fully custom content — escape hatch for non-standard layouts."""
    kind: Literal["custom"] = "custom"
    description: str = Field("")
    stories: list[StoryRef] = Field(
        ...,
        min_length=1,
        description="Story-backed components arranged in the content area",
    )


# Discriminated union over the `kind` field
ContentTemplate = Annotated[
    Union[ListTableTemplate, FormTemplate, CardsGridTemplate, DetailTemplate, CustomTemplate],
    Field(discriminator="kind"),
]


# ═══════════════════════════════════════════════════════════════════════════
# Page schema — ties it all together
# ═══════════════════════════════════════════════════════════════════════════

class PageMeta(BaseModel):
    """Metadata about a page."""
    title: str = Field(..., min_length=1)
    description: str = Field("")
    route: str = Field("", description="URL route path, e.g. '/overview'")
    topics: list[str] = Field(default_factory=list)


class PageSchema(BaseModel):
    """
    Top-level page schema — answers six questions:

    1. container   — What container? "azure" or "sre"
    2. side_nav    — Side nav? config or None
    3. title       — Page title? config or None
    4. (breadcrumbs are inside title.breadcrumbs)
    5. template    — What body template? list-table, form, cards-grid, …
    6. essentials  — Essentials accordion above the body? config or None
    """
    meta: PageMeta

    # Q1: What container are we using?
    container: ContainerType = Field(
        ...,
        description="Application shell: 'azure' or 'sre'",
    )

    # Q2: Does the container have a side nav?
    side_nav: SideNavConfig | None = Field(
        None,
        alias="sideNav",
        description="Side navigation config, or None for no side nav",
    )

    # Q3 + Q4: Does it have a page title? (breadcrumbs live inside title)
    title: TitleConfig | None = Field(
        None,
        description="Page title bar config, or None for no title",
    )

    # Q6: Is there an Essentials accordion above the body?
    essentials: EssentialsConfig | None = Field(
        None,
        description="Key-value essentials panel above the body template",
    )

    # Toolbar between title / essentials and the body content
    command_bar: CommandBar | None = Field(
        None,
        alias="commandBar",
        description="Toolbar between the title and content (optional)",
    )

    # Q5: What template is inside the body?
    template: ContentTemplate = Field(
        ...,
        description="Content template that fills the body area",
    )

    model_config = {"populate_by_name": True}
