"""Azure DevOps API client with retry logic."""
import logging
import time
from typing import Any, Optional

import requests

from .config import Settings

logger = logging.getLogger(__name__)


class AdoClient:
    """Client for interacting with Azure DevOps REST API."""

    MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 1  # seconds

    def __init__(self, settings: Settings):
        """Initialize the ADO client with settings."""
        self.settings = settings
        self.base_url = f"{settings.ado_org}/{settings.ado_project}"
        self.api_version = settings.ado_api_version
        self.session = requests.Session()
        self.session.auth = ("", settings.ado_pat)  # PAT auth
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": f"application/json;api-version={self.api_version}",
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> dict:
        """Make an HTTP request with retry logic."""
        url = f"{self.base_url}/{endpoint}"
        retries = 0

        while retries <= self.MAX_RETRIES:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", self.RETRY_BACKOFF_BASE * (2 ** retries)))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after)
                    retries += 1
                    continue

                # Handle server errors (5xx)
                if response.status_code >= 500:
                    backoff = self.RETRY_BACKOFF_BASE * (2 ** retries)
                    logger.warning(f"Server error {response.status_code}. Retrying in {backoff} seconds.")
                    time.sleep(backoff)
                    retries += 1
                    continue

                # Success
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                if retries >= self.MAX_RETRIES:
                    raise Exception(f"Request failed after {self.MAX_RETRIES} retries: {e}") from e
                backoff = self.RETRY_BACKOFF_BASE * (2 ** retries)
                logger.warning(f"Request error: {e}. Retrying in {backoff} seconds.")
                time.sleep(backoff)
                retries += 1

        raise Exception("Max retries exceeded")

    def wiql(self, query: str, top: int = 100) -> dict:
        """Run a WIQL query and return work items."""
        endpoint = "_apis/wit/wiql"
        data = {
            "query": query,
        }
        params = {"$top": top} if top else None

        result = self._make_request("POST", endpoint, params=params, json_data=data)

        # Extract work items from result
        work_items = []
        if "workItems" in result:
            for item in result["workItems"]:
                work_items.append({
                    "id": item.get("id"),
                    "url": item.get("url"),
                })

        return {
            "workItems": work_items,
            "count": len(work_items),
        }

    def get_work_item(self, work_item_id: int, fields: Optional[list] = None) -> dict:
        """Get a work item by ID."""
        endpoint = f"_apis/wit/workitems/{work_item_id}"

        params = {}
        if fields:
            params["fields"] = ",".join(fields)

        return self._make_request("GET", endpoint, params=params)

    def get_work_items_batch(self, ids: list, fields: Optional[list] = None) -> dict:
        """Get multiple work items by IDs."""
        endpoint = "_apis/wit/workitemsbatch"

        data = {
            "ids": ids,
        }
        if fields:
            data["fields"] = fields

        return self._make_request("POST", endpoint, json_data=data)
