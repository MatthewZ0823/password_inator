import json
import click
from typing import List
import pyperclip

from rich.console import Console

from .account import Account, find_account_by_id, Password, field_strs
from ..constants import paths as PATHS
from ..constants.strings import (
    COPIED_TO_CLIPBOARD,
    MASTER_PASSWORD_ERROR,
    MASTER_PASSWORD_NOT_FOUND_ERROR,
)
from ..io.prompting import confirm


def load_accounts_from_file(path: str) -> list[Account]:
    """
    Return a list of accounts from the json file given by path. If a file is not found, create a new one
    Can raise a `JSONDecodeError`
    """
    try:
        with open(path, "r") as file:
            data = json.load(file)

        return [Account.from_dict(account) for account in data]
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
        serialized_accounts = [account.to_json_serializable() for account in accounts]
        json.dump(serialized_accounts, file, indent=4)


def write_accounts_to_file(path: str, accounts: List[Account]) -> None:
    """
    Write a list of accounts to a json file. Will overwrite the contents of path

    :param str path: Path of json file to write to
    :param List[Account] accounts: List of accounts to write to path
    """
    with open(path, "w") as file:
        serialized_accounts = [account.to_json_serializable() for account in accounts]
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


def edit_account(id: str, field: str, new_value: str | Password):
    """
    Edit an account with a specific id
    """
    # Check types and values
    if field not in field_strs:
        raise ValueError
    if field == "password" and isinstance(new_value, str):
        raise TypeError
    elif field != "password" and isinstance(new_value, Password):
        raise TypeError

    accounts = load_accounts_from_file(PATHS.ACCOUNT_PATH)

    new_accounts = [
        (account if account.id != id else account.set_value(field, new_value))
        for account in accounts
    ]

    write_accounts_to_file(PATHS.ACCOUNT_PATH, new_accounts)


def edit_account_with_feedback(
    id: str, field: str, new_value: str, console: Console, err_console: Console
):
    """
    Edit an account with a specific id, and print feedback to the user indicating success/failure
    If editing password, function accepts the password in plaintext and will prompt user for the master password
    """
    if field not in field_strs:
        raise ValueError

    # Additional Requirements for editing passwords
    if field == "password":
        # Prompt to re-enter password
        if field == "password" and not confirm(new_value, console):
            return

        # Prompt to ask for Master Password
        master_password = input("Master Password: ")
        try:
            value = Password.from_plaintext(new_value, master_password)
        except ValueError:
            err_console.print(MASTER_PASSWORD_ERROR)
            return
        except FileNotFoundError:
            err_console.print(MASTER_PASSWORD_NOT_FOUND_ERROR)
            return
    else:
        value = new_value

    edit_account(id, field, value)
    console.print("[green]📝 Account Succesfully Edited[/]")


def get_password_from_account(path: str, id: str, master_password: str):
    """
    Gets a password from an account with id `id`

    :param str id: id of account to edit
    :param str master_password: master password used to encrypt the password
    :return: decrypted password
    :rtype: str
    :raises ValueError: if account with id `id` not found
    :raises ValueError: if account has no associated password
    :raises ValueError: if master_password is incorrect
    """
    accounts = load_accounts_from_file(path)

    for account in accounts:
        if account.id == id:
            return account.get_password(master_password)

    raise ValueError(f"No account found with id: {id}")


def get_password_from_account_with_feedback(
    id: str,
    master_password: str,
    console: Console,
    err_console: Console,
    clip: bool = False,
):
    """
    See `get_password_from_account`. Does the same thing, excepts prints error/success or saves to clipboard
    """
    try:
        password = get_password_from_account(PATHS.ACCOUNT_PATH, id, master_password)

        if clip:
            pyperclip.copy(password)
            console.print(COPIED_TO_CLIPBOARD)
        else:
            console.print(f"password: {password}")
    except ValueError as e:
        err_console.print(f"[red]{e}[/]")
