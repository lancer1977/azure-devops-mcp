"""Constants and enums for Azure DevOps work items."""

# Work Item System Fields
class WorkItemFields:
    """Azure DevOps System fields for work items."""
    SYSTEM_ID = "System.Id"
    SYSTEM_TITLE = "System.Title"
    SYSTEM_STATE = "System.State"
    SYSTEM_WORK_ITEM_TYPE = "System.WorkItemType"
    SYSTEM_ASSIGNED_TO = "System.AssignedTo"
    SYSTEM_CHANGED_DATE = "System.ChangedDate"
    SYSTEM_CREATED_DATE = "System.CreatedDate"
    SYSTEM_DESCRIPTION = "System.Description"
    SYSTEM_TEAM_PROJECT = "System.TeamProject"
    SYSTEM_ITERATION_PATH = "System.IterationPath"
    SYSTEM_PRIORITY = "System.Priority"
    SYSTEM_TAGS = "System.Tags"


# Work Item States
class WorkItemStates:
    """Common work item states."""
    NEW = "New"
    ACTIVE = "Active"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    DONE = "Done"
    REMOVED = "Removed"


# Work Item Types
class WorkItemTypes:
    """Common work item types."""
    EPIC = "Epic"
    FEATURE = "Feature"
    USER_STORY = "User Story"
    TASK = "Task"
    BUG = "Bug"
    IMPEDIMENT = "Impediment"


# API Endpoints
class ApiEndpoints:
    """Azure DevOps API endpoints."""
    WIQL = "_apis/wit/wiql"
    WORK_ITEMS = "_apis/wit/workitems"
    WORK_ITEMS_BATCH = "_apis/wit/workitemsbatch"
