"""Build a compact text summary of the Storybook catalog for LLM prompts.

The summary lists every component and its stories grouped by category,
so the LLM knows which story IDs are valid when filling StoryRefs.
"""

from __future__ import annotations

from schemas.loader import StoryIndex


def build_catalog_summary(index: StoryIndex) -> str:
    """
    Format the StoryIndex into a compact text block for an LLM prompt.

    Groups stories by component title and lists valid story IDs.
    """
    lines: list[str] = ["# Available Storybook Stories", ""]

    # Group by component title, sorted
    for component in sorted(index.all_components):
        story_ids = sorted(index.stories_for(component))
        lines.append(f"## {component}")
        for sid in story_ids:
            entry = index._by_id[sid]
            lines.append(f"  - `{sid}` ({entry.name})")
        lines.append("")

    return "\n".join(lines)
