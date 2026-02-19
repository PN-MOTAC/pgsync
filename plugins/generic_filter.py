import json
import os
import sys
import typing as t
from pgsync import plugin

# Global cache for filter rules to avoid reading the file on every transform
FILTER_RULES = None


def load_filter_rules():
    """
    Loads filter rules from schema.json.
    Searches for schema.json in common locations.
    """
    global FILTER_RULES
    if FILTER_RULES is not None:
        return

    FILTER_RULES = {}
    
    # Potential paths for schema.json
    # 1. Environment variable if set
    # 2. Default Docker path
    # 3. Local path (relative to cwd)
    potential_paths = [
        os.environ.get("SCHEMA_FILE"),
        "/data/schema.json",
        "./data/schema.json",
        "schema.json",
    ]

    schema_path = None
    for path in potential_paths:
        if path and os.path.exists(path):
            schema_path = path
            break
    
    if not schema_path:
        # Fallback: maintain empty rules if file not found (logging would be good here)
        print("GenericFilterPlugin: schema.json not found.", file=sys.stderr)
        return

    try:
        with open(schema_path, "r") as f:
            schema = json.load(f)
            
            # Schema is a list of index definitions
            for index_def in schema:
                index_name = index_def.get("index")
                filter_config = index_def.get("filter")
                
                if index_name and filter_config:
                    # Validate filter config structure
                    if "field" in filter_config and "value" in filter_config:
                        FILTER_RULES[index_name] = filter_config
                        print(f"GenericFilterPlugin: Loaded rule for index '{index_name}': {filter_config}", file=sys.stdout)

    except Exception as e:
        print(f"GenericFilterPlugin: Error parsing schema.json: {e}", file=sys.stderr)


class GenericFilterPlugin(plugin.Plugin):
    """
    A generic plugin to filter documents based on configured rules in schema.json.
    """

    name: str = "GenericFilterPlugin"

    def __init__(self):
        super().__init__()
        # Load rules when plugin is initialized
        load_filter_rules()

    def transform(self, doc: dict, **kwargs) -> t.Optional[dict]:
        """
        Transforms the document. Returns None to drop the document if it doesn't match the filter rule.
        """
        # Ensure rules are loaded (double check for safety)
        if FILTER_RULES is None:
            load_filter_rules()

        index: str = kwargs.get("_index")
        
        # Check if there is a rule for this index
        if index in FILTER_RULES:
            rule = FILTER_RULES[index]
            field = rule.get("field")
            expected_value = rule.get("value")

            # If the document has the field, check its value
            if field in doc:
                value = doc[field]
                # If value doesn't match, drop the document
                if value != expected_value:
                    return None
        
        return doc
