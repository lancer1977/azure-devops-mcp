"""Tools manifest - describes available tools and their schemas."""


def get_tools_manifest() -> dict:
    """Return the JSON manifest of available tools."""
    return {
        "tools": [
            {
                "name": "ado.search_work_items",
                "description": "Search for Azure DevOps work items using WIQL query",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "wiql": {
                            "type": "string",
                            "description": "WIQL query to execute",
                        },
                        "top": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 100,
                        },
                    },
                    "required": ["wiql"],
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "workItems": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "url": {"type": "string"},
                                },
                            },
                        },
                        "count": {"type": "integer"},
                    },
                },
            },
            {
                "name": "ado.get_work_item",
                "description": "Get a specific Azure DevOps work item by ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "The work item ID",
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of fields to retrieve",
                        },
                    },
                    "required": ["id"],
                },
                "output_schema": {
                    "type": "object",
                    "description": "Full Azure DevOps work item JSON",
                },
            },
        ]
    }
