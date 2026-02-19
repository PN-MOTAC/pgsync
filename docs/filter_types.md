# Supported Filter Types in GenericFilterPlugin

The `GenericFilterPlugin` supports all standard JSON data types for filtering, not just strings. This includes:

*   **Strings**: `"value": "Active"`
*   **Integers**: `"value": 123`
*   **Floats**: `"value": 12.5`
*   **Booleans**: `"value": true`
*   **Nulls**: `"value": null`

## Strict Type Matching
The plugin performs **strict type comparison**. This means the type defined in `schema.json` must exactly match the type of the field in the document (the Python type returned by `pgsync`).

### Examples

**Correct:**
```json
// schema.json (Integer)
"filter": { "field": "count", "value": 10 }
```
Document: `{"count": 10}` (Python `int`)
Result: **Match** (10 == 10)

**Incorrect:**
```json
// schema.json (String)
"filter": { "field": "count", "value": "10" }
```
Document: `{"count": 10}` (Python `int`)
Result: **Mismatch** (10 != "10") -> Document Dropped

**Note on Dates:**
Date/Time objects should generally not be used for direct filtering unless you are sure `pgsync` converts them to strings first, or you use string comparison on both sides.
