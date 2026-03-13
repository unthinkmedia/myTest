"""Export the PageSchema JSON Schema for LLM structured output."""

from schemas.page import PageSchema


def get_json_schema() -> dict:
    """Return the JSON Schema dict for PageSchema."""
    return PageSchema.model_json_schema()


def get_json_schema_str() -> str:
    """Return the JSON Schema as a formatted JSON string."""
    import json
    return json.dumps(get_json_schema(), indent=2)


if __name__ == "__main__":
    print(get_json_schema_str())
