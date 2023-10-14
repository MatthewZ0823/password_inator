import json
from typing import Optional

import typer
from password_utils import generate_password
from prompter import ask_yes_no
from rich.table import Table

EMPTY_TEXT = "[bright_black]Empty[/bright_black]"


class Account:
    def __init__(self, password, username, service, url):
        self.password = password
        self.username = username
        self.service = service
        self.url = url

    def _check_empty(self, val):
        if val == None:
            return EMPTY_TEXT
        return val

    def get_table(self, display_password: bool = False):
        table = Table(title="Account")
        table.add_column("Field")
        table.add_column("Value")

        if display_password:
            table.add_row("Password", self._check_empty(self.password))
        elif self.password != None:
            table.add_row(
                "Password", "[bright_magenta]******[/bright_magenta]")
        else:
            table.add_row("Password", EMPTY_TEXT)

        table.add_row("Username", self._check_empty(self.username))
        table.add_row("Service", self._check_empty(self.service))
        table.add_row("URL", self._check_empty(self.url))

        return table


def account_from_json(data):
    return Account(data["password"], data["username"], data["service"], data["url"])


def load_accounts_from_file(path: str) -> list[Account]:
    """
    Return a list of accounts from the json file given by path. If a file is not found, create a new one
    Can raise a `JSONDecodeError`
    """
    try:
        with open(path, "r") as file:
            data = json.load(file)

        return list(map(lambda account: account_from_json(account), data))
    except FileNotFoundError:
        with open("accounts.json", "w") as file:
            file.write("[]")
        return []


def create_account(
    username: Optional[str] = None,
    service: Optional[str] = None,
    url: Optional[str] = None,
    password: Optional[str] = None,
) -> Account:
    """
    Create a new account, prompts the user for input if any of the fields are missing
    """
    if username == None:
        if ask_yes_no("Enter username?"):
            username = typer.prompt(
                "Enter username", default=None)

    if service == None:
        if ask_yes_no("Enter name of service?"):
            service = typer.prompt(
                "Enter name of service", default=None)

    if url == None:
        if ask_yes_no("Enter url?"):
            url = typer.prompt(
                "Enter name of url", default=None)

    if password == None:
        if ask_yes_no("Generate password?"):
            password = generate_password()
        else:
            password = typer.prompt(
                "Enter password manually", hide_input=True, confirmation_prompt=True)

    return Account(password, username, service, url)


def save_account_to_file(path: str, account: Account) -> None:
    """
    Append the given account to the json file given by path
    Can raise a `JSONDecodeError`
    """
    accounts = load_accounts_from_file(path)
    accounts.append(account)

    with open(path, "w") as file:
        # Convert the accounts to a list of dicts so it's json serializable
        serialized_accounts = list(
            map(lambda account: account.__dict__, accounts))
        json.dump(serialized_accounts, file, indent=4)
