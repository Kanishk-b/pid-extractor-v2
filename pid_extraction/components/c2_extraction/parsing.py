import json
from typing import Any
from pid_extraction.exceptions import SchemaValidationError

def clean_and_parse_json(raw_output: str) -> dict[str, Any]:
    """Strips markdown fences and parses JSON safely."""
    clean_str = raw_output.strip()
    if clean_str.startswith("```json"): 
        clean_str = clean_str[7:]
    if clean_str.startswith("```"): 
        clean_str = clean_str[3:]
    if clean_str.endswith("```"): 
        clean_str = clean_str[:-3]
    
    clean_str = clean_str.strip()
    
    try:
        return json.loads(clean_str)
    except json.JSONDecodeError as e:
        # Attempt auto-heal for truncated outputs
        last_brace = clean_str.rfind("}")
        if last_brace != -1:
            salvaged = clean_str[:last_brace+1] + "\n  ]\n}"
            try:
                return json.loads(salvaged)
            except Exception:
                pass
        raise SchemaValidationError(f"Failed to parse JSON: {e}\nRaw Output: {raw_output}")