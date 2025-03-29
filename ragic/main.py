import os
from typing import Optional
from enum import Enum
import logging
import requests
import yaml  # type: ignore
import pandas as pd  # type: ignore


class QueryFilterType(Enum):
    EQUAL = "eq"
    GTE = "gte"
    LTE = "lte"
    GT = "gt"
    LT = "lt"
    CONTAINS = "like"


class DataClient:
    """
    Client for interacting with the Ragic Database backend via HTTP GET requests.

    This client relies on a YAML structure file that defines the schema (tabs, tables, columns) for your Ragic Database.
    Only the fields visible in the Ragic Table View will be returned by queries.

    Note:
        - Ensure that the structure file is always up-to-date.
        - This implementation currently uses synchronous HTTP requests. An asynchronous version is planned.
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
        self.structure_path = structure_path

        self.load_structure()
        self.__query_string: Optional[str] = None
        self.__active_tab: Optional[str] = None
        self.__active_table: Optional[str] = None

    def load_structure(self):
        """
        Load and parse the structure file that defines the database schema.

        Reads the YAML file specified by `structure_path` and stores its contents in the instance variable `structure`.

        Raises:
            FileNotFoundError: If the structure file does not exist at the specified path.

        TODO: Validate the structure file
        """
        if not os.path.exists(self.structure_path):
            raise FileNotFoundError(
                f"Structure file {self.structure_path} does not exist"
            )

        with open(self.structure_path, "r") as f:
            self.structure = yaml.safe_load(f)

    def tables(self, tab_name: str) -> dict:
        return self.structure["tabs"][tab_name]["tables"]

    def columns(self, tab_name: str, table_name: str) -> dict:
        return self.structure["tabs"][tab_name]["tables"][table_name]["columns"]

    def headers(self) -> dict:
        """
        Build the HTTP headers required for API requests.

        Returns:
            dict: A dictionary containing the Authorization header with the API key.
        """
        return {"Authorization": f"Basic {self.api_key}"}

    @staticmethod
    def _translate(operator: QueryFilterType) -> str:
        """
        Translate an internal query filter operator to the corresponding parameter used in Ragic API requests.

        Args:
            operator (QueryFilterType): The operator to translate (e.g., EQUAL, GTE, LTE).

        Returns:
            str: The operator as a string matching the Ragic API requirements.

        Raises:
            ValueError: If the provided operator is invalid.
        """
        if operator == QueryFilterType.EQUAL:
            return "eq"
        if operator == QueryFilterType.GTE:
            return "gte"
        if operator == QueryFilterType.LTE:
            return "lte"
        if operator == QueryFilterType.GT:
            return "gt"
        if operator == QueryFilterType.LT:
            return "lt"
        if operator == QueryFilterType.CONTAINS:
            return "like"
        raise ValueError(f"Invalid operator {operator}")

    @staticmethod
    def _compile(
        table_structure: dict, filters: list[tuple[str, QueryFilterType, str | int]]
    ) -> str:
        """
        Compile filter conditions into a query string segment for the API request.

        Each filter condition is provided as a tuple of (field_name, operator, field_value).
        The method translates each condition using the field ID from the table structure and the corresponding operator.

        Args:
            table_structure (dict): The table's structure, including column definitions.
            filters (list of tuple): A list of filter conditions formatted as (field_name, operator, field_value).

        Returns:
            str: A URL-encoded string of filter conditions, prefixed with '&'.
        """
        output_strings = []
        for _filter in filters:
            field_name, operator, field_value = _filter
            field_id = table_structure["columns"][field_name]["fieldId"]
            output_strings.append(
                f"where={field_id},{DataClient._translate(operator)},{field_value}"
            )
        output_string = "&".join(output_strings)
        return "&" + output_string

    def define_query(
        self,
        tab_name: str,
        table_name: str,
        conditions: list | None = None,
        include_subtable: bool = False,
    ):
        """
        Define the query string for retrieving data from a specific table.

        Constructs the query string using the provided tab and table names, along with pagination settings
        and optional filter conditions. The constructed query is stored internally for later use.

        Args:
            tab_name (str): The name of the tab containing the target table.
            table_name (str): The name of the table to query.
            conditions (list, optional): A list of filter conditions (each as a tuple: field_name, operator, field_value).
                Defaults to None.
            include_subtable (bool, optional): Flag indicating whether to include subtable data. Defaults to False.
        """
        # Default query setup
        query_string = f"v={self.version}&info=true&listing=true&subtables={1 if include_subtable else 0}"

        if conditions is not None:
            query_string = query_string + DataClient._compile(
                self.tables(tab_name)[table_name], conditions
            )

        self.__query_string = query_string
        self.__active_tab = tab_name
        self.__active_table = table_name

    @property
    def active_tab(self) -> Optional[str]:
        return self.__active_tab

    @property
    def active_table(self) -> Optional[str]:
        return self.__active_table

    @property
    def query_string(self) -> Optional[str]:
        """
        Get the constructed query string.

        Returns:
            Optional[str]: The constructed query string, or None if no query has been defined.
        """
        return self.__query_string

    def get_dataframe(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> Optional[pd.DataFrame]:
        """
        Execute the defined query and return the results as a pandas DataFrame.

        This method sends an HTTP GET request to the Ragic API using the constructed query string,
        processes the returned JSON data, and converts it into a DataFrame.
        Numerical columns with empty values are converted to pd.NA and cast to float32,
        while text columns replace empty strings with "Missing Value".

        Args:
            offset (int, optional): The record offset for pagination. Defaults to 0.
            limit (int, optional): The maximum number of records to retrieve. Defaults to 100.

        Returns:
            Optional[pd.DataFrame]: A DataFrame containing the retrieved data, or None if the response is empty
            or an error occurs during the request or processing.

        Raises:
            ValueError: If the query string, active tab, or active table has not been set.
        """

        logger = logging.getLogger(__name__)

        if (
            self.query_string is None
            or self.active_tab is None
            or self.active_table is None
        ):
            raise ValueError("Query not ready!!!")

        tab_identifier = self.structure["tabs"][self.active_tab]["identifier"]
        table_identifier = self.tables(self.active_tab)[self.active_table]["identifier"]
        RESOURCE = f"{tab_identifier}/{table_identifier}"
        PAGINATION = f"limit={limit}&offset={offset}"

        URL = f"{self.base_url}/{self.namespace}/{RESOURCE}?{self.query_string}&{PAGINATION}"
        HEADERS = self.headers()
        logger.info("URL: %s", URL)
        logger.info("HEADERS: %s", HEADERS)

        try:
            response = requests.get(URL, headers=HEADERS)
            response.raise_for_status()

            data = response.json()

            columns = ["index"]
            values = []
            for index, value_dict in data.items():
                _values = [index]
                for field, value in value_dict.items():
                    if (
                        field.startswith("_")
                        and field != "_create_date"
                        and field != "_update_date"
                    ):
                        continue
                    if field not in columns:
                        columns.append(field)
                    _values.append(value)
                values.append(_values)

            df = pd.DataFrame(values, columns=columns)
            if df.empty:
                return None

            logger.info("DataFrame Columns: %s", df.columns)
            columns_structure = self.columns(self.active_tab, self.active_table)
            for column_name, column_dict in columns_structure.items():
                column_type = column_dict["type"]

                if column_type == "number":
                    df[column_name] = df[column_name].transform(
                        lambda x: pd.NA if x == "" else x
                    )
                    df[column_name] = df[column_name].astype("float32")
                else:  # text
                    df[column_name] = df[column_name].transform(
                        lambda x: "Missing Value" if x == "" else x
                    )
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
        except Exception as e:
            logger.error(f"Error: {e}")
        return None
