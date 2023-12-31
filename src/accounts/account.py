from enum import Enum
from typing import Optional, List
from rich.table import Table
import uuid

from ..constants import strings as STRINGS
from ..utils.uuid_utils import is_valid_uuid


class AccountFields(Enum):
    PASSWORD = 1
    USERNAME = 2
    SERVICE = 3
    URL = 4
    ID = 5


class Account:
    def __init__(
        self,
        password: Optional[str] = None,
        username: Optional[str] = None,
        service: Optional[str] = None,
        url: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.password = None if password == "" else password
        self.username = None if username == "" else username
        self.service = None if service == "" else service
        self.url = None if url == "" else url
        self.id = uuid.uuid4().hex if id is None else id

        if not is_valid_uuid(self.id):
            raise ValueError

    def _check_empty(self, val: Optional[str]):
        if val is None or val == "":
            return STRINGS.EMPTY_TEXT
        return val

    def get_table(self, display_password: bool = False):
        """
        Return a rich table with the account's information
        If any field is None or "", it will display EMPTY_TEXT (Takes priority over display_password)
        If display_password is True, the password will be displayed, otherwise it will disply HIDDEN_TEXT
        """
        table = Table(title="Account")
        table.add_column("Field")
        table.add_column("Value")

        if display_password:
            table.add_row("Password", self._check_empty(self.password))
        elif self.password is not None and self.password != "":
            table.add_row("Password", STRINGS.HIDDEN_TEXT)
        else:
            table.add_row("Password", STRINGS.EMPTY_TEXT)

        table.add_row("Username", self._check_empty(self.username))
        table.add_row("Service", self._check_empty(self.service))
        table.add_row("URL", self._check_empty(self.url))

        return table

    def get_value(self, field: str):
        """
        Gets the value of a field of the account

        :param str field: name of account field, case insensitive
        :return: the value at the field
        :raises ValueError: if field is not a account valid
        """
        lower = field.lower()
        match lower:
            case "password":
                return self.password
            case "username":
                return self.username
            case "service":
                return self.service
            case "url":
                return self.url
            case "id":
                return self.id
            case _:
                raise ValueError

    def set_value(self, field: str, new_value: str):
        """
        Sets the value of a field of the account

        :param str field: name of account field, case insensitive
        :param str new_value: value to set the account field to
        :return: the value at the field
        :raises ValueError: if field is not a account valid
        """
        lower = field.lower()
        match lower:
            case "password":
                self.password = new_value
            case "username":
                self.username = new_value
            case "service":
                self.service = new_value
            case "url":
                self.url = new_value
            case "id":
                self.id = new_value
            case _:
                raise ValueError

        return self

    def __eq__(self, other):
        isAccount = isinstance(other, self.__class__)

        if not isAccount:
            return False

        # TODO: Change to comparing IDs instead
        return self.__dict__ == other.__dict__

    def __lt__(self, other):
        return self.username < other.username


def account_from_dict(data: dict) -> Account:
    """
    Create an account from `data`
    """
    fields = ["password", "username", "service", "url", "id"]
    field_values = [data[field] if field in data else None for field in fields]

    return Account(*field_values)


def find_account_by_id(accounts: List[Account], id: str):
    for account in accounts:
        if account.id == id:
            return account

    return None
