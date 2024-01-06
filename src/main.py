import click
import os
import pyperclip
from rich.console import Console, Group
from rich.live import Live

from typing import Optional

from .encryption.master_password import save_master_password
from .utils.password_utils import generate_password
from .search import fuzzyfind_account_by_field, create_search_table
from .io.live_input import Key_Type, Live_Input
from .io.prompting import confirm
from .accounts.account import (
    Account,
    AccountFields,
)
from .accounts.file_manager import (
    get_password_from_account_with_feedback,
    load_accounts_from_file,
    save_account_to_file,
    edit_account_with_feedback,
    delete_account,
)
from .constants import strings as STRINGS
from .constants import paths as PATHS

console = Console()
err_console = Console(stderr=True)


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    # prompting is handled later
    "--password",
    help="Password for the account",
    type=str,
)
@click.option(
    # prompting is handled later
    "--master-password",
    help="Master password used to encrypt passwords",
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
@click.option("-s", "--save", help="Save account", is_flag=True)
@click.option(
    "-r",
    "--random-password",
    help="Generate a random password for the account",
    is_flag=True,
)
def create_account(
    clipboard: bool,
    save: bool,
    random_password: bool,
    password: Optional[str] = None,
    master_password: Optional[str] = None,
    username: Optional[str] = None,
    service: Optional[str] = None,
    url: Optional[str] = None,
):
    """
    Create an account with the given parameters
    """
    if random_password:
        password = generate_password()
    elif password is None:
        password = input("Password [Press Enter for a Random Password]: ")

        if password == "":
            password = generate_password()
        elif not confirm(password, console):
            return

    if master_password is None:
        master_password = input("Master Password: ")

    if username == STRINGS.SKIP_STRING:
        username = None
    if service == STRINGS.SKIP_STRING:
        service = None
    if url == STRINGS.SKIP_STRING:
        url = None

    try:
        new_account = Account.from_unencrypted(
            password, master_password, username, service, url
        )
    except ValueError:
        err_console.print(STRINGS.MASTER_PASSWORD_ERROR)
        return
    except FileNotFoundError:
        err_console.print(STRINGS.MASTER_PASSWORD_NOT_FOUND_ERROR)
        return

    console.print(new_account.get_table())

    if clipboard:
        pyperclip.copy(password)
        console.print(STRINGS.COPIED_TO_CLIPBOARD)

    if save or click.confirm("Save account?"):
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
        filtered_accounts = fuzzyfind_account_by_field(field, accounts, "")

    panel_table = create_search_table(filtered_accounts, highlighted_row, show_ids)
    group = Group(
        ":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to Confirm): _",
        panel_table,
    )

    with Live(group, refresh_per_second=60) as live:
        input_type = live_input.process_next_input()

        while input_type != Key_Type.EXIT:
            filtered_accounts = fuzzyfind_account_by_field(
                field, accounts, live_input.input
            )

            if input_type == Key_Type.UP:
                highlighted_row = min(highlighted_row - 1, len(filtered_accounts) - 1)
            elif input_type == Key_Type.DOWN:
                highlighted_row = max(highlighted_row + 1, 0)
            elif input_type == Key_Type.ENTER:
                if highlighted_row >= 0 and highlighted_row < len(filtered_accounts):
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
    console.print("3. Get Password")
    console.print("4. Quit")

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
                new_value = input("new-value: ")

                edit_account_with_feedback(id, field, new_value, console, err_console)
                editing = click.confirm("Continue Editing?")
        case 2:
            delete_account(id, console)
        case 3:
            master_password = input("Master Password: ")
            clip = click.confirm("Copy to clipboard?")

            get_password_from_account_with_feedback(
                id, master_password, console, err_console, clip
            )
        case 4:
            console.print("Quitting")
            return


@cli.command(name="delete-account")
@click.argument("id")
def delete_account_command(id: str):
    """
    Delete an account with a specific id
    """
    delete_account(id, console)


@cli.command(name="edit-account")
@click.argument("id")
@click.option(
    "--field",
    type=click.Choice(["password", "username", "service", "url"]),
    prompt=True,
)
@click.option("--new-value", type=Optional[str], default=None, show_default=False)
def edit_account_command(id: str, field: str, new_value: Optional[str]):
    """
    Edit an account with a specific id
    """
    if new_value is None:
        new_value = input("new-value: ")

    edit_account_with_feedback(id, field, new_value, console, err_console)


@cli.command(name="get-account-password")
@click.argument("id")
@click.option(
    "-p",
    "--master-password",
    type=str,
    prompt=True,
    help="Master password used to encrypt all passwords",
)
@click.option("-c", "--clipboard", help="Copy password to clipboard", is_flag=True)
def get_account_password_command(id: str, master_password: str, clipboard: bool):
    """
    Get the password of an account with the specified id
    """
    get_password_from_account_with_feedback(
        id, master_password, console, err_console, clipboard
    )


@cli.command(name="create-master-password")
@click.argument("master_password")
@click.option(
    "--force", help="Force override the current master password", is_flag=True
)
def create_master_password_command(master_password: str, force: bool):
    """
    Create and save the master password to encrypt all passwords
    """
    # Check if overriding existing master password
    if os.path.isfile(PATHS.MASTER_PATH) and not force:
        err_console.print("[red]Master Password already exists![/]")
        err_console.print(
            "[red]Running this command will override the existing master password. Previous passwords encrypted with the already existing master password will be unrecoverable[/]"
        )
        err_console.print(
            "[red]If you would like to override the master password use the --force flag[/]"
        )
        return

    confirmation = confirm(master_password, console)

    if not confirmation:
        return

    save_master_password(master_password)
    console.print("[green]🔐 Master Password Saved![/]")


if __name__ == "__main__":
    cli()
