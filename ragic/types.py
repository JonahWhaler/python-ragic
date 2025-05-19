"""
Types
"""

from enum import Enum
from typing import Optional
import yaml


class OperandType(Enum):
    """
    Enumeration for the types of operands used in query conditions.
    """

    EQUALS = "eq"
    GREATER_OR_EQUALS = "gte"
    LESS_OR_EQUALS = "lte"
    GREATER = "gt"
    LESS = "lt"
    CONTAINS = "like"
    EQUALS_A_NODE_ID = "eqeq"
    REGULAR_EXPRESSION = "regex"


class RagicStructure:
    """
    Class to handle the structure of a Ragic spreadsheet.
    """

    def __init__(self, structure_path: str):
        self.load_structure(structure_path)

    def load_structure(self, structure_path: str):
        """
        Load the structure of the Ragic spreadsheet from a YAML file.
        """
        with open(structure_path, "r", encoding="utf-8") as f:
            self.__structure = yaml.safe_load(f)

    def get_tabs(self) -> list[str]:
        """
        Get the names of all tabs in the Ragic spreadsheet.
        """
        return list(self.__structure["tabs"].keys())

    def get_tab_id(self, tab_name: str) -> str:
        """
        Get the ID of a specific tab.

        Args:
            tab_name (str): The name of the tab.

        Returns:
            str: The ID of the specified tab.
        """
        return self.__structure["tabs"][tab_name]["tab_id"]

    def get_tables(self, tab_name: str) -> list[str]:
        """
        Get the names of all tables in a specific tab.
        """
        return list(self.__structure["tabs"][tab_name]["tables"].keys())

    def get_table_id(self, tab_name: str, table_name: str) -> str:
        """
        Get the ID of a specific table within a tab.

        Args:
            tab_name (str): The name of the tab.
            table_name (str): The name of the table.

        Returns:
            str: The ID of the specified table.
        """
        return self.__structure["tabs"][tab_name]["tables"][table_name]["table_id"]

    def get_fields(self, tab_name: str, table_name: str) -> list[str]:
        """
        Get the names of all fields in a specific table within a tab.
        """
        return list(
            self.__structure["tabs"][tab_name]["tables"][table_name]["fields"].keys()
        )

    def get_field_id(self, tab_name: str, table_name: str, field_name: str) -> str:
        """
        Get the field ID of a specific field within a table.

        Args:
            tab_name (str): The name of the tab.
            table_name (str): The name of the table.
            field_name (str): The name of the field.

        Returns:
            str: The field ID of the specified field.

        Raises:
            KeyError: If the field name is not found in the specified table.
        """
        system_fields = {
            "Create Date": "105",
            "Entry Manager": "106",
            "Create User": "108",
            "Last Update Date": "109",
            "Notify User": "110",
            "If Locked": "111",
            "If Starred": "112",
        }
        if field_name in system_fields:
            return system_fields[field_name]

        return str(
            self.__structure["tabs"][tab_name]["tables"][table_name]["fields"][
                field_name
            ]["field_id"]
        )

    def get_field_type(self, tab_name: str, table_name: str, field_name: str) -> str:
        """
        Get the field type of a specific field within a table.

        Args:
            tab_name (str): The name of the tab.
            table_name (str): The name of the table.
            field_name (str): The name of the field.

        Returns:
            str: The field type of the specified field.
        """
        return self.__structure["tabs"][tab_name]["tables"][table_name]["fields"][
            field_name
        ]["field_type"]


class OtherGETParameters:
    """
    Class to handle other GET parameters for Ragic API requests.

    It is recommended to keep the default settings unless you are sure you need to change them.

    **Notes**:
    - `subtables` and `listing` cannot be set to True at the same time.
    - If `listing` is set to True, only fields make available in the listing view will be returned.
    - Please keep `subtables` as False when more than 1 subtable is available.
    """

    def __init__(
        self,
        subtables: bool = False,
        listing: bool = False,
        reverse: bool = False,
        info: bool = True,
        conversation: bool = False,
        approval: bool = False,
        comment: bool = False,
        bbcode: bool = False,
        history: bool = False,
        ignoreMask: bool = False,
        ignoreFixedFilter: bool = False,
    ):
        if subtables and listing:
            raise ValueError(
                "Cannot set both subtables and listing to True at the same time."
            )

        self.subtables = subtables
        self.listing = listing
        self.reverse = reverse
        self.info = info
        self.conversation = conversation
        self.approval = approval
        self.comment = comment
        self.bbcode = bbcode
        self.history = history
        self.ignoreMask = ignoreMask
        self.ignoreFixedFilter = ignoreFixedFilter


class OrderingType(Enum):
    """
    Enumeration for the types of ordering used in query conditions.
    """

    ASC = "ASC"
    DESC = "DESC"


class Ordering:
    """
    Class to handle ordering of query results.
    """

    def __init__(
        self, order_by: Optional[str] = None, order: Optional[OrderingType] = None
    ):
        if order_by is None and order:
            raise ValueError("If order is set, order_by must also be set.")

        if order_by and order is None:
            order = OrderingType.ASC

        self.order_by = order_by
        self.order = order


class CreateUpdateParameters:
    """
    Class to handle parameters for creating or updating data in Ragic.
    """

    def __init__(
        self,
        doFormula: bool = True,
        doDefaultValue: bool = True,
        doLinkLoad: Optional[str] = None,
        doWorkflow: bool = False,
        notifiation: bool = True,
        checkLock: bool = True,
    ):
        """
        Initialize the parameters for creating or updating data in Ragic.

        Args:
            doFormula (bool): Whether to apply formulas.
            doDefaultValue (bool): Whether to apply default values.
            doLinkLoad (Optional[str]): Whether to load linked data. [true, first]
            doWorkflow (bool): Whether to apply workflow rules.
            notifiation (bool): Whether to send notifications.
            checkLock (bool): Whether to check for locks.
        """
        self.doFormula = doFormula
        self.doDefaultValue = doDefaultValue
        self.doLinkLoad = doLinkLoad
        self.doWorkflow = doWorkflow
        self.notifiation = notifiation
        self.checkLock = checkLock

    def get_params_string(self) -> str:
        """
        Get the parameters as a query string.

        Returns:
            output (str): The parameters as a query string.
        """
        parts = []
        if self.doFormula:
            parts.append("doFormula=true")
        if self.doDefaultValue:
            parts.append("doDefaultValue=true")
        if self.doLinkLoad:
            parts.append(f"doLinkLoad={self.doLinkLoad}")
        if self.doWorkflow:
            parts.append("doWorkflow=true")
        if not self.notifiation:
            parts.append("notifiation=false")
        if self.checkLock:
            parts.append("checkLock=true")

        return "&".join(parts)
