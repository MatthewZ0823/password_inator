from enum import Enum
import json
from typing import Optional
from rich.table import Table
import uuid

from typing import List

from .constants import strings as STRINGS
from .constants import paths as PATHS


class AccountFields(Enum):
    PASSWORD = 1
    USERNAME = 2
    SERVICE = 3
    URL = 4
    ID = 5


def is_valid_uuid(uuid_hex: str):
    """
    Checks if uuid_hex is a valid hex representation of a uuid

    :param str uuid: uuid to check, as a 32 character lowercase hexadecimal string
    :return: If uuid is a valid uuid
    :rtype: bool
    """
    try:
        uuid_obj = uuid.UUID(uuid_hex)
        return uuid_obj.hex == uuid_hex
    except ValueError:
        return False


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


def load_accounts_from_file(path: str) -> list[Account]:
    """
    Return a list of accounts from the json file given by path. If a file is not found, create a new one
    Can raise a `JSONDecodeError`
    """
    try:
        with open(path, "r") as file:
            data = json.load(file)

        return list(map(lambda account: account_from_dict(account), data))
    except FileNotFoundError:
        with open(PATHS.ACCOUNT_PATH, "w") as file:
            file.write("[]")
        return []


def save_account_to_file(path: str, account: Account) -> None:
    """
    Append the given account to the json file given by path

    :param str path: Path of json file to append to
    :param Account account: Account to append to file
    :raises ValueError: If path contains invalid json
    :raises JSONDecodeError: If path contains semantic errors
    """
    accounts = load_accounts_from_file(path)
    accounts.append(account)

    with open(path, "w") as file:
        # Convert the accounts to a list of dicts so it's json serializable
        serialized_accounts = list(map(lambda account: account.__dict__, accounts))
        json.dump(serialized_accounts, file, indent=4)


def write_accounts_to_file(path: str, accounts: List[Account]) -> None:
    """
    Write a list of accounts to a json file. Will overwrite the contents of path

    :param str path: Path of json file to write to
    :param List[Account] accounts: List of accounts to write to path
    """
    with open(path, "w") as file:
        serialized_accounts = [account.__dict__ for account in accounts]
        json.dump(serialized_accounts, file, indent=4)
