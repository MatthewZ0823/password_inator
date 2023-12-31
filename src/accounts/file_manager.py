import json
import click
from typing import List

from rich.console import Console

from .account import Account, account_from_dict, find_account_by_id
from ..constants import paths as PATHS


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


def delete_account(id: str, console: Console):
    """
    Delete an account with a specific id. Will ask the user for confirmation before deleting the account
    """
    accounts = load_accounts_from_file(PATHS.ACCOUNT_PATH)

    deleted_account = find_account_by_id(accounts, id)

    if deleted_account is None:
        console.print(f"[red]No account found with id: [/]{id}")
        return

    console.print(deleted_account.get_table())

    confirmation = click.confirm("Are you sure you want to delete the account: ")

    if not confirmation:
        return

    new_accounts = [account for account in accounts if account.id != id]

    # Check if no account was deleted
    if len(accounts) == len(new_accounts):
        console.print(f"[red]No Account Found with id: [/]{id}")
        return

    write_accounts_to_file(PATHS.ACCOUNT_PATH, new_accounts)
    console.print("[green]🗑️ Account Succesfully Deleted[/green]")


def edit_account(id: str, field: str, new_value: str, console: Console):
    """
    Edit an account with a specific id
    """
    accounts = load_accounts_from_file(PATHS.ACCOUNT_PATH)

    new_accounts = [
        (account if account.id != id else account.set_value(field, new_value))
        for account in accounts
    ]

    write_accounts_to_file(PATHS.ACCOUNT_PATH, new_accounts)
    console.print("[green]📝 Account Succesfully Edited[/]")
