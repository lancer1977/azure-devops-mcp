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
            {
                "name": "ado.list_repositories",
                "description": "List Git repositories in the Azure DevOps project",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
                "output_schema": {
                    "type": "object",
                    "description": "Repository list response",
                },
            },
            {
                "name": "ado.list_pull_requests",
                "description": "List pull requests for a repository",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "repository_id": {
                            "type": "string",
                            "description": "Repository ID or name",
                        },
                        "status": {
                            "type": "string",
                            "description": "PR status filter",
                            "default": "active",
                        },
                        "top": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50,
                        },
                    },
                    "required": ["repository_id"],
                },
                "output_schema": {
                    "type": "object",
                    "description": "Pull request list response",
                },
            },
            {
                "name": "ado.list_builds",
                "description": "List recent Azure DevOps builds",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "top": {
                            "type": "integer",
                            "description": "Maximum number of builds",
                            "default": 25,
                        },
                        "status_filter": {
                            "type": "string",
                            "description": "Optional build status filter",
                        },
                    },
                },
                "output_schema": {
                    "type": "object",
                    "description": "Build list response",
                },
            },
            {
                "name": "ado.create_work_item",
                "description": "Create a work item (guarded, requires ADO_ALLOW_WRITES=true)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "work_item_type": {"type": "string", "description": "Work item type (e.g. Task, Bug)"},
                        "fields": {
                            "type": "object",
                            "description": "Dictionary of Azure DevOps work item fields",
                        },
                    },
                    "required": ["work_item_type", "fields"],
                },
                "output_schema": {"type": "object", "description": "Created work item"},
            },
            {
                "name": "ado.update_work_item",
                "description": "Update a work item fields (guarded, requires ADO_ALLOW_WRITES=true)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Work item ID"},
                        "fields": {
                            "type": "object",
                            "description": "Dictionary of fields to update",
                        },
                    },
                    "required": ["id", "fields"],
                },
                "output_schema": {"type": "object", "description": "Updated work item"},
            },
            {
                "name": "ado.add_pr_comment",
                "description": "Add a pull request comment (guarded, requires ADO_ALLOW_WRITES=true)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "repository_id": {"type": "string", "description": "Repository ID or name"},
                        "pull_request_id": {"type": "integer", "description": "Pull request ID"},
                        "content": {"type": "string", "description": "Comment text"},
                    },
                    "required": ["repository_id", "pull_request_id", "content"],
                },
                "output_schema": {"type": "object", "description": "Created PR comment thread"},
            },
        ]
    }
