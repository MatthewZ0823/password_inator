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
)
from .constants import strings as STRINGS

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
    default="Press Enter for a random Password",
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
    if password == "Press Enter to for a random Password":
        password = generate_password()

    if username == STRINGS.SKIP_STRING:
        username = None
    if service == STRINGS.SKIP_STRING:
        service = None
    if url == STRINGS.SKIP_STRING:
        url = None

    new_account = Account(password, username, service, url)

    console.print(new_account.get_table(display_password=(not clipboard)))

    if clipboard:
        pyperclip.copy(password)
        console.print("[green]:clipboard: Password copied to clipboard![/green]")

    if click.confirm("Save account?"):
        save_account_to_file("accounts.json", new_account)
        console.print("[green]Account saved![/green]")


@cli.command()
@click.option(
    "--search-by",
    help="Account Field to Search By",
    default="Username",
    type=click.Choice(["Username", "Service", "URL"], case_sensitive=False),
)
def find_account(search_by: str):
    """
    Find an account
    """
    highlighted_row = 0
    accounts = load_accounts_from_file("accounts.json")
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

    panel_table = create_search_table(filtered_accounts, highlighted_row)
    group = Group(
        ":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to exit): _",
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

            panel_table = create_search_table(filtered_accounts, highlighted_row)

            group = Group(
                f":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to exit): {live_input.input}_",
                panel_table,
            )
            live.update(group)

            input_type = live_input.process_next_input()


if __name__ == "__main__":
    cli()
