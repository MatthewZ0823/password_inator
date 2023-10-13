from typing_extensions import Annotated
import pyperclip
import typer
from rich.console import Console
from account import save_account_to_file, create_account

from prompter import ask_yes_no
from password_utils import generate_password

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


if __name__ == "__main__":
    app()
