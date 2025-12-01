from langchain_core.tools import StructuredTool
from pydantic import create_model
from typing import List, Optional


def _patch_tools_for_gemini(tools: List[StructuredTool]) -> List[StructuredTool]:
    """
    Patches MCP tools to meet Gemini's strict schema requirements.
    Handles both Pydantic models and Dictionary schemas.
    """
    patched_tools = []

    for tool in tools:
        if not tool.args_schema:
            patched_tools.append(tool)
            continue

        # --- CASE 1: Arguments are a Pydantic V2 Model ---
        if hasattr(tool.args_schema, "model_fields"):
            schema_fields = tool.args_schema.model_fields  # type: ignore
            new_fields = {}
            needs_patch = False

            for name, field_info in schema_fields.items():
                if name in ["order_desc", "order_asc"]:
                    # Force type to Optional[List[str]]
                    new_fields[name] = (Optional[List[str]], field_info)
                    needs_patch = True
                else:
                    new_fields[name] = (field_info.annotation, field_info)

            if needs_patch:
                # Recreate the Pydantic model with strict types
                try:
                    tool.args_schema = create_model(
                        tool.args_schema.__name__, **new_fields  # type: ignore
                    )
                except Exception as e:
                    print(f"⚠️ Could not patch Pydantic model for {tool.name}: {e}")

        # --- CASE 2: Arguments are a Dictionary (JSON Schema) ---
        elif isinstance(tool.args_schema, dict):
            # Modify the dictionary in-place
            props = tool.args_schema.get("properties", {})
            for name in ["order_desc", "order_asc"]:
                if name in props:
                    field_def = props[name]
                    # If it is an array and missing 'items', fix it
                    if isinstance(field_def, dict) and field_def.get("type") == "array":
                        if "items" not in field_def:
                            field_def["items"] = {"type": "string"}

        patched_tools.append(tool)

    return patched_tools
