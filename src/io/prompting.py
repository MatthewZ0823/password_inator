import click
from rich.console import Console


def confirm(value: str, console: Console):
    """
    Asks the user to confirm value.

    :param str value: value to confirm
    :return: True if the user repeats the value
    :rtype: bool
    """
    if value == click.prompt("Repeat to Confirm", type=str):
        return True
    else:
        console.print("[red]Values do not Match[/]")
        return False
