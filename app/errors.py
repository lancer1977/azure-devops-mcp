"""Application-level error types and helpers."""


class AdoMcpError(Exception):
    """Base error with HTTP + MCP mapping metadata."""

    def __init__(self, message: str, http_status: int = 500, mcp_code: int = -32000):
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.mcp_code = mcp_code


class ValidationError(AdoMcpError):
    """Input validation error."""

    def __init__(self, message: str):
        super().__init__(message, http_status=400, mcp_code=-32602)


class UnauthorizedError(AdoMcpError):
    """AuthN/AuthZ error."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, http_status=401, mcp_code=-32001)


class UpstreamError(AdoMcpError):
    """Upstream Azure DevOps API error."""

    def __init__(self, message: str = "Azure DevOps API error", http_status: int = 502):
        super().__init__(message, http_status=http_status, mcp_code=-32002)
