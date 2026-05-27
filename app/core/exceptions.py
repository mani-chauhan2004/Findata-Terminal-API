class UpstreamAPIError(Exception):
    """Raised when the upstream data provider returns an error response."""

    STATUS_MESSAGES = {
        400: "Invalid request parameters",
        401: "Data provider authentication failed",
        403: "Access to this resource is not permitted",
        404: "Requested data not found",
        429: "Rate limit exceeded, please try again later",
    }

    def __init__(self, status_code: int, endpoint: str = ""):
        self.status_code = status_code
        self.endpoint = endpoint
        self.detail = self.STATUS_MESSAGES.get(
            status_code,
            "Data provider is temporarily unavailable" if status_code >= 500 else "Upstream request failed",
        )
        super().__init__(self.detail)


class UpstreamParseError(Exception):
    """Raised when the upstream response cannot be parsed."""

    detail = "Received an unexpected response format from the data provider"
