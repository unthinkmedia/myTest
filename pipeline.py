"""Pipeline: JSON → Validate → Code.

The LLM step (image analysis → PageSchema JSON) happens in the Copilot
conversation. This script takes the resulting JSON and runs the local
steps: validate against live Storybook + generate a React .tsx page.

Usage:
    # From a JSON file produced by Copilot:
    python pipeline.py schema.json
    python pipeline.py schema.json --output src/pages/MyPage.tsx
    python pipeline.py schema.json --validate-only

    # Or pipe JSON from stdin:
    echo '{"meta":...}' | python pipeline.py -

    # Dump the prompt context (catalog + JSON schema) for reference:
    python pipeline.py --dump-prompt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from schemas.page import PageSchema
from schemas.json_schema import get_json_schema_str
from schemas.loader import fetch_story_index
from schemas.catalog_summary import build_catalog_summary
from schemas.validator import validate_page, validate_icons
from schemas.codegen import generate_page


def _print_summary(page: PageSchema) -> None:
    """Print the six-question summary of a PageSchema."""
    print(f"   Q1 Container: {page.container.value}")
    print(f"   Q2 Side nav:  {'Yes' if page.side_nav else 'No'}")
    if page.title:
        title_str = page.title.resource_name
        if page.title.page_name:
            title_str += f" | {page.title.page_name}"
        print(f"   Q3 Title:     {title_str}")
        print(f"   Q4 Breadcrumbs: {page.title.breadcrumbs or 'None'}")
    else:
        print("   Q3 Title:     No")
        print("   Q4 Breadcrumbs: No")
    print(f"   Q5 Template:  {page.template.kind}")
    print(f"   Q6 Essentials: {'Yes' if page.essentials else 'No'}")


def run_from_json(
    json_input: str,
    storybook_url: str = "http://localhost:6006/index.json",
    output_path: str | None = None,
    validate_only: bool = False,
) -> PageSchema:
    """
    Local pipeline: JSON string → PageSchema → validate → code.

    The JSON is produced by Copilot during the conversation (no API key needed).
    """
    # ── Step 1: Parse JSON → PageSchema ──
    print("📋 Parsing PageSchema...")
    page_data = json.loads(json_input)
    page = PageSchema.model_validate(page_data)
    _print_summary(page)

    # ── Step 2: Load Storybook index + validate ──
    print("\n📖 Loading Storybook index...")
    try:
        index = fetch_story_index(storybook_url)
        print(f"   {len(index)} stories from {len(index.all_components)} components")

        print("\n🔍 Validating StoryRefs...")
        errors = validate_page(page, index)
        if errors:
            print(f"   ⚠ {len(errors)} validation issue(s):")
            for e in errors:
                print(f"     {e}")
        else:
            print("   ✓ All StoryRefs valid")
    except Exception as e:
        print(f"   ⚠ Storybook not reachable ({e}), skipping StoryRef validation")

    # ── Step 2b: Validate icon imports (runs independently of Storybook) ──
    print("\n🎨 Validating icon imports...")
    icon_errors = validate_icons(page)
    if icon_errors:
        print(f"   ⚠ {len(icon_errors)} invalid icon(s):")
        for e in icon_errors:
            print(f"     {e}")
        if not validate_only:
            print("\n❌ Fix invalid icon names before generating code.")
            sys.exit(1)
    else:
        print("   ✓ All icon imports valid")

    if validate_only:
        print("\n✓ Validation complete (--validate-only)")
        return page

    # ── Step 3: Generate code ──
    print("\n🔧 Generating page .tsx...")
    component_name = "".join(w.capitalize() for w in page.meta.title.split())
    code = generate_page(page, component_name)

    if output_path:
        out = Path(output_path)
    else:
        out = Path("src") / "pages" / f"{component_name}.tsx"

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(code)
    print(f"   ✓ Written to {out}")

    # Also write the schema JSON for reference
    schema_out = out.with_suffix(".schema.json")
    schema_out.write_text(json.dumps(page_data, indent=2))
    print(f"   ✓ Schema saved to {schema_out}")

    print("\n✓ Pipeline complete")
    return page


def dump_prompt(storybook_url: str = "http://localhost:6006/index.json") -> str:
    """Print the full prompt context (catalog + JSON schema) for reference."""
    index = fetch_story_index(storybook_url)
    catalog = build_catalog_summary(index)
    schema = get_json_schema_str()
    prompt = (
        "# Available Storybook Stories (use these storyIds)\n\n"
        + catalog
        + "\n\n# JSON Schema (output must conform to this)\n\n```json\n"
        + schema
        + "\n```"
    )
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="PageSchema JSON → Validate → React page pipeline"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to PageSchema JSON file, or '-' for stdin",
    )
    parser.add_argument("--output", "-o", help="Output .tsx page path (default: src/pages/<Name>.tsx)")
    parser.add_argument(
        "--storybook-url",
        default="http://localhost:6006/index.json",
        help="Storybook index.json URL",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate, don't generate code",
    )
    parser.add_argument(
        "--dump-prompt",
        action="store_true",
        help="Print the catalog + JSON schema prompt context and exit",
    )
    args = parser.parse_args()

    if args.dump_prompt:
        print(dump_prompt(args.storybook_url))
        return

    if not args.input:
        parser.error("Provide a JSON file path or '-' for stdin (or use --dump-prompt)")

    if args.input == "-":
        json_input = sys.stdin.read()
    else:
        json_input = Path(args.input).read_text()

    run_from_json(
        json_input=json_input,
        storybook_url=args.storybook_url,
        output_path=args.output,
        validate_only=args.validate_only,
    )


if __name__ == "__main__":
    main()
