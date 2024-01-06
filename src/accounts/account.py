from enum import Enum
from typing import Optional, List, Dict, Any
from rich.table import Table
import uuid

from .password import Password
from ..constants import strings as STRINGS
from ..utils.uuid_utils import is_valid_uuid

field_strs = ["password", "username", "service", "url", "id"]


class AccountFields(Enum):
    PASSWORD = 1
    USERNAME = 2
    SERVICE = 3
    URL = 4
    ID = 5


def _check_empty(val: Optional[str]):
    if val is None or val == "":
        return STRINGS.EMPTY_TEXT
    return val


class Account:
    def __init__(
        self,
        password: Optional[Password] = None,
        username: Optional[str] = None,
        service: Optional[str] = None,
        url: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.password = password
        self.username = None if username == "" else username
        self.service = None if service == "" else service
        self.url = None if url == "" else url
        self.id = uuid.uuid4().hex if id is None else id

        if not is_valid_uuid(self.id):
            raise ValueError

    def get_table(self):
        """
        Return a rich table with the account's information
        If any field is None or "", it will display EMPTY_TEXT
        """
        table = Table(title="Account")
        table.add_column("Field")
        table.add_column("Value")

        if self.password is not None:
            table.add_row("Password", STRINGS.HIDDEN_TEXT)
        else:
            table.add_row("Password", STRINGS.EMPTY_TEXT)

        table.add_row("Username", _check_empty(self.username))
        table.add_row("Service", _check_empty(self.service))
        table.add_row("URL", _check_empty(self.url))

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

    def set_value(self, field: str, new_value: str | Password):
        """
        Sets the value of a field of the account

        :param str field: name of account field, case insensitive
        :param str new_value: value to set the account field to
        :return: the value at the field
        :raises ValueError: if field is not a account valid
        """
        lower = field.lower()
        if lower == "password":
            if isinstance(new_value, str):
                raise TypeError
            else:
                self.password = new_value
                return self

        if isinstance(new_value, Password):
            raise TypeError

        match lower:
            case "username":
                self.username = new_value
            case "service":
                self.service = new_value
            case "url":
                self.url = new_value
            case "id":
                self.id = new_value
            case "salt":
                self.salt = new_value
            case _:
                raise ValueError

        return self

    def get_password(self, master_password: str) -> str:
        """
        Decrypts the password associated with the account

        :param str master_password: master password used to encrypt the password
        :return: the decrypted password
        :rtype: str
        :raises ValueError: if password is not set
        :raises ValueError: if master_password is incorrect
        """
        if self.password is None:
            raise ValueError("Password is not set")

        return self.password.decrypt(master_password)

    def to_json_serializable(self) -> Dict[str, Any]:
        """
        Converts Account object into a json serializable form

        :return: serializable dictionary representation of Account
        :rtype: Dict
        """
        without_password = field_strs.copy()
        without_password.remove("password")

        d: Dict
        d = {x: self.get_value(x) for x in without_password}

        if self.password is None:
            d["password"] = None
        else:
            d["password"] = self.password.to_json_serializable()

        return d

    def __eq__(self, other):
        isAccount = isinstance(other, self.__class__)

        if not isAccount:
            return False

        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        without_password = field_strs.copy()
        without_password.remove("password")

        s = self.password.__str__() + "\n"

        s += "".join(
            [f"{field}: {self.get_value(field)}\n" for field in without_password]
        ).strip()

        return s

    @staticmethod
    def from_unencrypted(
        plaintext_password: str,
        master_password: str,
        username: Optional[str] = None,
        service: Optional[str] = None,
        url: Optional[str] = None,
        id: Optional[str] = None,
    ):
        """
        Create an account with a plaintext password and the master password

        :param str plaintext_password: password in plaintext, will be encrypted using `master_password`
        :param str master_password: master password to encrypt `plaintext_password` with
        :param Optional[str] username: username associated with account. Defaults to None
        :param Optional[str] service: service associated with account. Defaults to None
        :param Optional[str] url: url associated with account. Defaults to None
        :param Optional[str] id: id associated with account. Defaults to None
        :return: An Account object with all the fields filled in
        :rtype: Account
        :raises ValueError: if `master_password` does not match the password in master.txt
        :raises FileNotFoundError: if `master.txt` is not found
        """
        password = Password.from_plaintext(plaintext_password, master_password)

        return Account(
            password,
            username,
            service,
            url,
            id,
        )

    @staticmethod
    def from_dict(data: dict):
        """
        Create an account from `data`
        """
        without_password = field_strs.copy()
        without_password.remove("password")

        field_values = [
            data[field] if field in data else None for field in without_password
        ]
        password = (
            Password.from_json_serilizable(data["password"])
            if "password" in data
            else None
        )

        return Account(password, *field_values)


def find_account_by_id(accounts: List[Account], id: str) -> Optional[Account]:
    for account in accounts:
        if account.id == id:
            return account

    return None
