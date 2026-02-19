import typing as t
from pgsync import plugin

# Configuration for filter rules
# Format: "index_name": {"field": "field_name_to_check", "value": expected_value}
# If the field's value matches the expected_value, the document is KEPT.
# If the field's value DOES NOT match, the document is DROPPED.
FILTER_RULES = {
    "localities": {"field": "status", "value": "Active"},
}


class GenericFilterPlugin(plugin.Plugin):
    """
    A generic plugin to filter documents based on configured rules.
    """

    name: str = "GenericFilterPlugin"

    def transform(self, doc: dict, **kwargs) -> t.Optional[dict]:
        """
        Transforms the document. Returns None to drop the document if it doesn't match the filter rule.
        """
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
