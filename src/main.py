import click
import pyperclip
from rich.console import Console, Group
from rich.live import Live

from typing import Optional

from .password_utils import generate_password
from .search import find_account_by_field, create_search_table
from .live_input import Key_Type, Live_Input
from .account import (
    Account,
    AccountFields,
    load_accounts_from_file,
    save_account_to_file,
    write_accounts_to_file,
)
from .constants import strings as STRINGS
from .constants import paths as PATHS

console = Console()
err_console = Console(stderr=True)


@click.group()
def cli():
    pass


@cli.command()
@click.option("-c", "--clipboard", help="Copy password to clipboard", is_flag=True)
def create_password(clipboard: bool):
    """
    Generate a new password
    """
    password = generate_password()

    if clipboard:
        pyperclip.copy(password)
        console.print("[green]:clipboard: Password copied to clipboard![/green]")
    else:
        console.print(f"Password: {password}")


@cli.command()
@click.option(
    "--password",
    prompt=True,
    default=STRINGS.RANDOM_PASSWORD_PROMPT,
    show_default=False,
    help="Password for the account",
    type=str,
)
@click.option(
    "--username",
    prompt=True,
    default=STRINGS.SKIP_STRING,
    show_default=False,
    help="Username for the account",
    type=str,
)
@click.option(
    "--service",
    prompt=True,
    default=STRINGS.SKIP_STRING,
    show_default=False,
    help="Service for the account",
    type=str,
)
@click.option(
    "--url",
    prompt=True,
    default=STRINGS.SKIP_STRING,
    show_default=False,
    help="URL for the account",
    type=str,
)
@click.option("-c", "--clipboard", help="Copy password to clipboard", is_flag=True)
def create_account(
    clipboard: bool,
    password: Optional[str] = None,
    username: Optional[str] = None,
    service: Optional[str] = None,
    url: Optional[str] = None,
):
    """
    Create an account with the given parameters
    """
    if password == STRINGS.RANDOM_PASSWORD_PROMPT:
        password = generate_password()

    if username == STRINGS.SKIP_STRING:
        username = None
    if service == STRINGS.SKIP_STRING:
        service = None
    if url == STRINGS.SKIP_STRING:
        url = None

    new_account = Account(password, username, service, url)

    console.print(new_account.get_table(display_password=False))

    if clipboard:
        pyperclip.copy(password)
        console.print("[green]:clipboard: Password copied to clipboard![/green]")

    if click.confirm("Save account?"):
        save_account_to_file(PATHS.ACCOUNT_PATH, new_account)
        console.print("[green]Account saved![/green]")


@cli.command()
@click.option(
    "--search-by",
    help="Account Field to Search By",
    default="Username",
    type=click.Choice(["Username", "Service", "URL"], case_sensitive=False),
)
@click.option(
    "--show-ids",
    help="Display Account IDs in search table",
    is_flag=True,
    default=False,
)
def find_account(search_by: str, show_ids: bool):
    """
    Find an account
    """
    highlighted_row = 0
    selected_account_id = None
    accounts = load_accounts_from_file(PATHS.ACCOUNT_PATH)
    live_input = Live_Input()

    field_mapping = {
        "Username": AccountFields.USERNAME,
        "Service": AccountFields.SERVICE,
        "URL": AccountFields.URL,
    }
    field = field_mapping.get(search_by)

    if field is None:
        err_console.print(f"{STRINGS.ERROR} INVALID FIELD")
        return
    else:
        filtered_accounts = find_account_by_field(field, accounts, "")

    panel_table = create_search_table(filtered_accounts, highlighted_row, show_ids)
    group = Group(
        ":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to Confirm): _",
        panel_table,
    )

    with Live(group, refresh_per_second=60) as live:
        input_type = live_input.process_next_input()

        while input_type != Key_Type.EXIT:
            filtered_accounts = find_account_by_field(field, accounts, live_input.input)

            if input_type == Key_Type.UP:
                highlighted_row = min(highlighted_row - 1, len(filtered_accounts) - 1)
            elif input_type == Key_Type.DOWN:
                highlighted_row = max(highlighted_row + 1, 0)
            elif input_type == Key_Type.ENTER:
                selected_account_id = filtered_accounts[highlighted_row].id
                break

            panel_table = create_search_table(
                filtered_accounts, highlighted_row, show_ids
            )

            group = Group(
                f":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to Confirm): {live_input.input}_",
                panel_table,
            )
            live.update(group)

            input_type = live_input.process_next_input()

    if selected_account_id is not None:
        select_account(selected_account_id)


def select_account(id: str):
    console.print("\nOptions:")
    console.print("1. Edit")
    console.print("2. Delete")
    console.print("3. Quit")

    choice = click.prompt(
        "Enter your choice", type=click.IntRange(min=0, max=3, clamp=True)
    )

    match choice:
        case 1:
            editing = True
            while editing:
                field = click.prompt(
                    "field",
                    type=click.Choice(["password", "username", "service", "url"]),
                )
                new_value = click.prompt("new-value", type=str)
                edit_account(id, field, new_value)
                editing = click.confirm("Continue Editing?")
        case 2:
            delete_account(id)
        case 3:
            console.print("Quitting")
            return


def delete_account(id: str):
    """
    Delete an account with a specific id
    """
    accounts = load_accounts_from_file(PATHS.ACCOUNT_PATH)

    new_accounts = [account for account in accounts if account.id != id]

    # Check if no account was deleted
    if len(accounts) == len(new_accounts):
        console.print(f"[red]No Account Found with id: [/]{id}")
        return

    write_accounts_to_file(PATHS.ACCOUNT_PATH, new_accounts)
    console.print("[green]🗑️ Account Succesfully Deleted[/green]")


@cli.command(name="delete-account")
@click.argument("id")
def delete_account_command(id: str):
    """
    Delete an account with a specific id
    """
    delete_account(id)


def edit_account(id: str, field: str, new_value: str):
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


@cli.command(name="edit-account")
@click.argument("id")
@click.option(
    "--field",
    type=click.Choice(["password", "username", "service", "url"]),
    prompt=True,
)
@click.option("--new-value", type=str, prompt=True)
def edit_account_command(id: str, field: str, new_value: str):
    """
    Edit an account with a specific id
    """
    edit_account(id, field, new_value)


if __name__ == "__main__":
    cli()
