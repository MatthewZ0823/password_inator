from typing_extensions import Annotated
import pyperclip
import typer
from rich.console import Console, Group
from rich.live import Live
from rich.columns import Columns
from rich.table import Table
from rich.panel import Panel
from account import EMPTY_TEXT, load_accounts_from_file, save_account_to_file, create_account
from fuzzyfinder import fuzzyfinder
from getch import getch

from prompter import ask_yes_no
from password_utils import generate_password

BACKSPACE_BYTE = b'\x08'
FUNCTION_ARROW_BYTE = b'\xe0'

console = Console()
err_console = Console(stderr=True)

app = typer.Typer()


@app.command()
def new_password(clipboard: Annotated[bool, typer.Option(
        "--clipboard", "-c", help="Copy password to clipboard", is_flag=True)]):
    """
    Generate a new password
    """
    password = generate_password()

    if clipboard:
        pyperclip.copy(password)
        console.print("[green]Password copied to clipboard![/green]")
    else:
        console.print(f"Password: {password}")

    if ask_yes_no("Save password?"):
        new_account = create_account(password=password)
        save_account_to_file("accounts.json", new_account)
        console.print("[green]Account saved![/green]")
        console.print(new_account.get_table())


@app.command()
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
    app()
