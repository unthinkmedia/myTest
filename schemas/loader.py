"""Load the Storybook index.json and build a StoryIndex for validation.

The StoryIndex is a lightweight lookup: it knows every valid story ID
grouped by component title.  It does NOT try to replicate all of
Storybook's metadata — just enough to validate that StoryRefs in a
PageSchema point at real stories.

Usage:
    index = fetch_story_index("http://localhost:6006/index.json")
    index.has("components-button--primary")          # True
    index.stories_for("Components/Button")           # {"components-button--primary", ...}
    index.component_for("components-button--primary") # "Components/Button"
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass, field


@dataclass(frozen=True)
class StoryEntry:
    """Minimal info about one Storybook story."""
    story_id: str
    name: str
    title: str  # component title, e.g. "Components/Button"


@dataclass
class StoryIndex:
    """Registry of every story in the running Storybook instance."""

    _by_id: dict[str, StoryEntry] = field(default_factory=dict)
    _by_component: dict[str, set[str]] = field(default_factory=dict)

    # -- queries --

    def has(self, story_id: str) -> bool:
        return story_id in self._by_id

    def stories_for(self, component_title: str) -> set[str]:
        return self._by_component.get(component_title, set())

    def component_for(self, story_id: str) -> str | None:
        entry = self._by_id.get(story_id)
        return entry.title if entry else None

    @property
    def all_story_ids(self) -> set[str]:
        return set(self._by_id)

    @property
    def all_components(self) -> set[str]:
        return set(self._by_component)

    def __len__(self) -> int:
        return len(self._by_id)

    # -- construction --

    def _add(self, entry: StoryEntry) -> None:
        self._by_id[entry.story_id] = entry
        self._by_component.setdefault(entry.title, set()).add(entry.story_id)


def fetch_story_index(url: str = "http://localhost:6006/index.json") -> StoryIndex:
    """Fetch index.json from a running Storybook and return a StoryIndex."""
    with urllib.request.urlopen(url) as resp:  # noqa: S310 — trusted local dev server
        data = json.loads(resp.read())

    index = StoryIndex()
    for entry in data.get("entries", {}).values():
        if entry.get("type") != "story":
            continue
        index._add(StoryEntry(
            story_id=entry["id"],
            name=entry["name"],
            title=entry["title"],
        ))
    return index
