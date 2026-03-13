"""Pydantic schemas for the Storybook component catalog.

This file describes what EXISTS in the Storybook library — the available
components, their props, and their pre-configured stories (variants).
It's the "menu" you pick from.  It can be auto-populated from the
Storybook MCP's getComponentList / getStoryDetails endpoints.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Prop schema — describes one prop a component accepts
# ---------------------------------------------------------------------------

class PropType(str, Enum):
    """Allowed property value types for a component arg."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ENUM = "enum"
    OBJECT = "object"
    ARRAY = "array"
    FUNCTION = "function"
    NODE = "node"


class PropDefinition(BaseModel):
    """Schema for a single component prop / arg."""
    name: str = Field(..., min_length=1, description="Prop name, e.g. 'appearance'")
    type: PropType = Field(..., description="Data type of the prop")
    required: bool = Field(False, description="Whether this prop is required")
    default_value: Any = Field(None, alias="defaultValue", description="Default value if any")
    description: str = Field("", description="Human-readable description of the prop")
    enum_values: list[str] | None = Field(
        None,
        alias="enumValues",
        description="Allowed values when type is 'enum'",
    )

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Story — one pre-configured variant of a component
# ---------------------------------------------------------------------------

class Story(BaseModel):
    """
    A single Storybook story — one pre-configured variant of a component.

    The story_id is the Storybook identifier used to look it up,
    e.g. 'components-cuibutton--primary'.
    """
    story_id: str = Field(
        ...,
        alias="storyId",
        min_length=1,
        description="Storybook story ID, e.g. 'components-cuibutton--primary'",
    )
    name: str = Field(..., min_length=1, description="Display name, e.g. 'Primary'")
    args: dict[str, Any] = Field(
        default_factory=dict,
        description="Default arg values for this story variant",
    )
    description: str = Field("", description="What this variant demonstrates")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Component catalog entry
# ---------------------------------------------------------------------------

class ComponentEntry(BaseModel):
    """
    A component in the Storybook catalog.

    Lists the component's props schema and available stories (variants).
    This is what the Storybook MCP returns — you don't author these
    by hand, they're discovered from the running Storybook.
    """
    component_id: str = Field(
        ...,
        alias="componentId",
        min_length=1,
        description="Unique component identifier, e.g. 'CuiButton'",
    )
    tag_name: str | None = Field(
        None,
        alias="tagName",
        description="Custom-element tag if web component, e.g. 'cui-button'",
    )
    category: str = Field("", description="Grouping category, e.g. 'Actions', 'Data Display'")
    props: list[PropDefinition] = Field(
        default_factory=list,
        description="Prop/arg definitions this component accepts",
    )
    stories: list[Story] = Field(
        ...,
        min_length=1,
        description="Available stories (variants) — at least one required",
    )

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Slot
# ---------------------------------------------------------------------------

class SlotKind(str, Enum):
    DEFAULT = "default"
    NAMED = "named"


class SlotDefinition(BaseModel):
    """Describes a slot exposed by a web-component element."""
    name: str = Field("", description="Slot name (empty string = default slot)")
    kind: SlotKind = Field(SlotKind.DEFAULT)
    description: str = Field("")
    allowed_elements: list[str] = Field(
        default_factory=list,
        alias="allowedElements",
        description="Component IDs allowed in this slot",
    )

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# CSS custom property
# ---------------------------------------------------------------------------

class CSSCustomProperty(BaseModel):
    """A CSS custom property (design token) exposed by a component."""
    name: str = Field(..., pattern=r"^--[\w-]+$", description="e.g. '--button-bg-color'")
    default_value: str = Field("", alias="defaultValue")
    description: str = Field("")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Full component manifest (entry + slots + CSS props)
# ---------------------------------------------------------------------------

class ComponentManifest(BaseModel):
    """
    Complete manifest for a component — its catalog entry plus
    structural metadata (slots, CSS custom properties).
    """
    component: ComponentEntry
    slots: list[SlotDefinition] = Field(default_factory=list)
    css_properties: list[CSSCustomProperty] = Field(
        default_factory=list,
        alias="cssProperties",
    )

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Catalog — the full set of available components
# ---------------------------------------------------------------------------

class Catalog(BaseModel):
    """
    The complete Storybook catalog — all components and their stories.

    This is the source of truth for what's available to select from
    when composing a page.
    """
    components: list[ComponentManifest] = Field(
        ...,
        min_length=1,
        description="All available components with their stories",
    )
