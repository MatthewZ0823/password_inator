import json
from typing import Annotated, Optional
import typer
from rich.console import Console
from account import Account, account_from_json

console = Console()
err_console = Console(stderr=True)

app = typer.Typer()


def load_accounts() -> list[Account]:
    try:
        with open("accounts.json", "r") as file:
            data = json.load(file)

        accounts = []
        for account in data:
            account = account_from_json(account)
            accounts.append(account)
        return accounts
    except FileNotFoundError:
        with open("accounts.json", "w") as file:
            file.write("[]")
        return []
    except json.JSONDecodeError as e:
        # TODO handle this error better
        err_console.print(f"[red bold]JSON decoding error:[/red bold] {e}")
        raise typer.Exit(code=1)


def my_callback(value: str):
    if value == "":
        return ":P"
    return value


@app.command()
def new_account(
    username: Optional[str] = typer.Option(
        help="Username to associate with password", default=None),
    service: Optional[str] = typer.Option(
        help="Service to associate with password", default=None),
    url: Optional[str] = typer.Option(
        help="Url to associate with password", default=None),
):
    """
    Create a new account to save credentials for
    """
    accounts = load_accounts()

    if username == None:
        if typer.prompt("Enter username? (Y/n)", default="n") == "Y":
            username = typer.prompt(
                "Enter username", default=None)

    if service == None:
        if typer.prompt("Enter service? (Y/n)", default="n") == "Y":
            service = typer.prompt(
                "Enter name of service", default=None)

    if url == None:
        if typer.prompt("Enter url? (Y/n)", default="n") == "Y":
            url = typer.prompt(
                "Enter name of url", default=None)

    password = typer.prompt(
        "Enter password", hide_input=True, confirmation_prompt=True)

    accounts.append(Account(password, username, service, url))

    with open("accounts.json", "w") as file:
        accounts = list(map(lambda account: account.__dict__, accounts))
        json.dump(accounts, file, indent=4)
        console.print("[green]Account saved![/green]")


if __name__ == "__main__":
    app()
