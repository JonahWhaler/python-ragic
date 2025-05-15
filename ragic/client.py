"""
RagicAPIClient.py
"""

import os
from typing import Any, Optional
import logging
import httpx

from .types import (
    OperandType,
    RagicStructure,
    OtherGETParameters,
    Ordering,
)


logger = logging.getLogger(__name__)


class RagicAPIClient:
    """
    Client for interacting with the Ragic Database backend via HTTP GET requests.

    This client relies on a YAML structure file that defines the schema (tabs, tables, columns) for your Ragic Database.
    Only the fields visible in the Ragic Table View will be returned by queries.

    **Methods**:
        - load(table_name: str, offset: int, size: int, include_subtable: bool) -> Optional[DataFrame]

    **Notes**:
        - Add these environment variables to your `.env` file:
            - `RAGIC_URL`
            - `RAGIC_NAMESPACE`
            - `RAGIC_API_KEY`
        - The structure file should be in YAML format and should define the schema of your Ragic Database.
    """

    def __init__(
        self,
        base_url: Optional[str],
        namespace: Optional[str],
        api_key: Optional[str],
        version: int,
        structure_path: str,
    ):
        """
        Initialize a DataClient instance.

        Sets up API configuration and loads the structure file that describes the database schema.
        If any of the key parameters (base_url, namespace, api_key) are not provided, they will be retrieved from
        the corresponding environment variables: "RAGIC_URL", "RAGIC_NAMESPACE", and "RAGIC_API_KEY".

        Args:
            base_url (str, optional): Base URL for the Ragic API. Defaults to the environment variable if not provided.
            namespace (str, optional): The namespace for your Ragic Database. Defaults to the environment variable if not provided.
            api_key (str, optional): API key for Ragic authentication. Defaults to the environment variable if not provided.
            version (int): API version to use in the requests.
            structure_path (str): Path to the YAML file containing the database structure.

        Raises:
            ValueError: If base_url, namespace, or api_key are not provided and cannot be found in the environment.
        """

        if base_url is None:
            base_url = os.getenv("RAGIC_URL")
        if namespace is None:
            namespace = os.getenv("RAGIC_NAMESPACE")
        if api_key is None:
            api_key = os.getenv("RAGIC_API_KEY")

        if base_url is None or namespace is None or api_key is None:
            raise ValueError("RAGIC_URL, RAGIC_NAMESPACE and RAGIC_API_KEY must be set")

        self.base_url = base_url
        self.namespace = namespace
        self.api_key = api_key
        self.version = version
        self.structure: RagicStructure = RagicStructure(structure_path)

    @property
    def headers(self) -> dict[str, str]:
        """
        Build the HTTP headers required for API requests.

        Returns:
            output (dict[str, str]): A dictionary containing the Authorization header with the API key.
        """
        return {"Authorization": f"Basic {self.api_key}"}

    def handle_other_get_params(self, params: OtherGETParameters) -> list[str]:
        """
        Handle additional GET parameters for the API request.

        Args:
            params (OtherGETParameters): Additional GET parameters to include in the request.

        Returns:
            parts (list[str]): A list of key-value-pair GET parameters.

        **Notes**:
            - [Other-GET-parameters](https://www.ragic.com/intl/en/doc-api/25/Other-GET-parameters)
            - Converts the attributes of the `OtherGETParameters` object into corresponding GET parameter strings.
        """
        parts = []
        if not params.subtables:
            parts.append("subtables=0")
        if params.listing:
            parts.append("listing=true")
        if params.reverse:
            parts.append("reverse=true")
        if params.info:
            parts.append("info=true")
        if params.conversation:
            parts.append("conversation=true")
        if params.approval:
            parts.append("approval=true")
        if params.comment:
            parts.append("comment=true")
        if params.bbcode:
            parts.append("bbcode=true")
        if params.history:
            parts.append("history=true")
        if params.ignoreMask:
            parts.append("ignoreMask=true")
        if params.ignoreFixedFilter:
            parts.append("ignoreFixedFilter=true")

        return parts

    def load(
        self,
        tab_name: str,
        table_name: str,
        conditions: Optional[list[tuple[str, OperandType, Any]]] = None,
        offset: int = 0,
        size: int = 100,
        other_get_params: Optional[OtherGETParameters] = None,
        ordering: Optional[Ordering] = None,
    ) -> Optional[dict]:
        """
        Loads data from a specified table within a tab, applying optional conditions, pagination, and ordering.

        Args:
            tab_name (str): The name of the tab containing the table.
            table_name (str): The name of the table to load data from.
            conditions (Optional[list[tuple[str, OperandType, Any]]], optional):
                A list of conditions to filter the data. Each condition is a tuple of (field_name, operator, value).
            offset (int, optional): The starting index for pagination. Defaults to 0.
            size (int, optional): The number of records to retrieve. Defaults to 100.
            other_get_params (Optional[OtherGETParameters], optional):
                Additional GET parameters for the request.
            ordering (Optional[Ordering], optional):
                Ordering specification for the results.

        Returns:
            Optional[dict]: The loaded data after post-processing, or None if no data is found.

        Raises:
            ValueError: If the specified tab or table does not exist, or if both reverse and ordering are set.
            RuntimeError: If the maximum number of request attempts is reached.
            httpx.RequestError: If there is an error with the HTTP request.
            Exception: For any other unexpected errors.

        **Notes**:
        - Retry mechanism is implemented for handling timeouts errors.
        """
        # Validate input parameters
        if tab_name not in self.structure.get_tabs():
            raise ValueError(f"Tab {tab_name} not found in structure")

        if table_name not in self.structure.get_tables(tab_name):
            raise ValueError(f"Table {table_name} not found in tab {tab_name}")

        if other_get_params and other_get_params.reverse and ordering:
            raise ValueError("Cannot set both reverse and ordering at the same time.")

        # Construct the API URL
        tab_id = self.structure.get_tab_id(tab_name)
        table_id = self.structure.get_table_id(tab_name, table_name)

        base_url = f"{self.base_url}/{self.namespace}/{tab_id}/{table_id}"
        parts = ["api", f"v={self.version}", f"limit={size}", f"offset={offset}"]

        if other_get_params:
            other_parts = self.handle_other_get_params(other_get_params)
            if other_parts:
                parts.extend(other_parts)

        if ordering:
            if ordering.order_by not in self.structure.get_fields(tab_name, table_name):
                raise ValueError(
                    f"Field {ordering.order_by} not found in table {table_name} in tab {tab_name}"
                )

            field_id = self.structure.get_field_id(
                tab_name, table_name, ordering.order_by
            )
            parts.append(f"order={field_id},{ordering.order.value}")

        if conditions:
            for condition in conditions:
                logger.info("Condition: %s", condition)
                field_name, operator, field_value = condition
                if field_name == "fts":
                    part_value = f"fts={field_value}"
                elif field_name == "filterId":
                    part_value = f"filterId={field_value}"
                else:
                    field_id = self.structure.get_field_id(
                        tab_name, table_name, field_name
                    )
                    part_value = f"where={field_id},{operator.value},{field_value}"
                parts.append(part_value)

        target_url = f"{base_url}?{'&'.join(parts)}"
        logger.info("URL: %s", target_url)
        _timeout = 300
        attempt: int = 1
        max_attempts: int = 3
        while attempt <= max_attempts:
            try:
                with httpx.Client(
                    http2=True, headers=self.headers, timeout=_timeout
                ) as client:
                    response = client.get(target_url)
                    response.raise_for_status()

                    data = response.json()

                    if data:
                        # return data
                        return self.post_processing(data)
                    return None
            except httpx.TimeoutException as timeout_err:
                logging.warning("[%d] Request timed out: %s", attempt, timeout_err)
                _timeout *= 2.0
                attempt += 1
                logger.warning("Extend timeout to %.2f seconds", _timeout)
            except httpx.RequestError as req_err:
                logging.error(
                    "Request failed: %s", req_err, exc_info=True, stack_info=True
                )
                raise
            except Exception as err:
                logging.error(
                    "An unexpected error occurred: %s",
                    err,
                    exc_info=True,
                    stack_info=True,
                )
                raise

        raise RuntimeError("Max re-attempts reached.")

    @staticmethod
    def post_processing(returned_data: dict) -> dict:
        """
        Post-process the data returned from the API.

        Remove fields with "_" prefix, except for specific fields like "_create_date", "_update_date", and "_ragicId".
        This is to ensure that only relevant data is returned.

        Args:
            returned_data (dict): The data returned from the API.

        Returns:
            processed_data (dict): The processed data.
        """
        processed_data = {}
        for index, value_dict in returned_data.items():
            _value_dict = {}
            for field_name, value in value_dict.items():
                if field_name.startswith("_") and field_name not in [
                    "_create_date",
                    "_update_date",
                    "_ragicId",
                ]:
                    continue
                _value_dict[field_name] = value
            processed_data[index] = _value_dict

        return processed_data
