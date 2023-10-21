import click
import pyperclip
from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from account import EMPTY_TEXT, Account, load_accounts_from_file, save_account_to_file
from fuzzyfinder import fuzzyfinder
from getch import getch

# from prompter import ask_yes_no
from password_utils import generate_password

BACKSPACE_BYTE = b'\x08'
FUNCTION_ARROW_BYTE = b'\xe0'

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
        console.print("[green]Password copied to clipboard:clipboard:![/green]")
    else:
        console.print(f"Password: {password}")


SKIP_STRING = "Press Enter to Skip"


@cli.command()
@click.option("--password", prompt=True, default="Press Enter to for a random Password", show_default=False, help="Password for the account", type=str)
@click.option("--username", prompt=True, default=SKIP_STRING, show_default=False, help="Username for the account", type=str)
@click.option("--service", prompt=True, default=SKIP_STRING, show_default=False, help="Service for the account", type=str)
@click.option("--url", prompt=True, default=SKIP_STRING, show_default=False, help="URL for the account", type=str)
@click.option("-c", "--clipboard", help="Copy password to clipboard", is_flag=True)
def create_account(clipboard: bool, password: str = None, username: str = None, service: str = None, url: str = None):
    """
    Create an account with the given parameters
    """
    if password == "Press Enter to for a random Password":
        password = generate_password()

    if username == SKIP_STRING:
        username = None
    if service == SKIP_STRING:
        service = None
    if url == SKIP_STRING:
        url = None

    new_account = Account(password, username, service, url)

    console.print(new_account.get_table(display_password=(not clipboard)))

    if clipboard:
        pyperclip.copy(password)
        console.print("[green]Password copied to clipboard:clipboard:![/green]")

    if click.confirm("Save account?"):
        save_account_to_file("accounts.json", new_account)
        console.print("[green]Account saved![/green]")


@cli.command()
def find_account():
    """
    Find an account
    """
    accounts = load_accounts_from_file('accounts.json')
    usernames = list[str]([])

    input = ""

    panel_table = Table()
    panel_table.add_column("Username", style="bold")
    panel_table.add_column("Service")
    panel_table.add_column("URL")

    for account in accounts:
        if (account.username != None):
            usernames.append(account.username)

            service = account.service if account.service != None else EMPTY_TEXT
            url = account.url if account.url != None else EMPTY_TEXT
            panel_table.add_row(account.username, service, url)

    group = Group(
        ":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to exit): _",
        panel_table
    )

    with Live(group, refresh_per_second=60) as live:
        next_byte = getch()

        while next_byte != b'\r':
            if next_byte == BACKSPACE_BYTE:
                input = input[:-1]
            elif next_byte == FUNCTION_ARROW_BYTE:
                # Function bytes take up two bytes, so we need to consume the next byte
                next_byte = getch()
            else:
                try:
                    input += next_byte.decode("UTF-8")
                except UnicodeDecodeError:
                    continue

            panel_table = Table()
            panel_table.add_column("Username", style="bold")
            panel_table.add_column("Service")
            panel_table.add_column("URL")

            found_usernames = list(fuzzyfinder(input, usernames))
            for account in accounts:
                if (account.username in found_usernames):
                    usernames.append(account.username)

                    service = account.service if account.service != None else EMPTY_TEXT
                    url = account.url if account.url != None else EMPTY_TEXT
                    panel_table.add_row(account.username, service, url)

            group = Group(
                f":magnifying_glass_tilted_right: [yellow]Search[/yellow] (Enter to exit): {input}_",
                panel_table
            )
            live.update(group)
            next_byte = getch()


if __name__ == "__main__":
    cli()
