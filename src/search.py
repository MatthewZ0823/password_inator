from fuzzyfinder import fuzzyfinder  # type: ignore
from typing import List, Optional
from .accounts.account import Account, AccountFields
from rich.table import Table

from .constants import strings as STRINGS


def fuzzyfind_account_by_field(
    field: AccountFields, accounts: List[Account], search: str
) -> List[Account]:
    """
    Fuzzyfind an account, searching through the list of accounts by field
    search is the string which the fuzzy matching is done
    """
    accessor_mapping = {
        AccountFields.USERNAME: lambda account: account.username,
        AccountFields.SERVICE: lambda account: account.service,
        AccountFields.URL: lambda account: account.url,
    }

    accessor = accessor_mapping.get(field)
    if accessor is None:
        return []  # Handle invalid field

    filtered_accounts = [
        account for account in accounts if accessor(account) is not None
    ]
    return list(fuzzyfinder(search, filtered_accounts, accessor=accessor))


def _default_if_empty(s: Optional[str]) -> str:
    """
    Returns a default empty text string if s is None. Otherwise just returns s
    """
    return s if s is not None else STRINGS.EMPTY_TEXT


def _highlight_text(s: str) -> str:
    return f"[green]{s}[/green]"


def create_search_table(
    accounts: List[Account],
    highlighted_row: Optional[int] = None,
    show_ids: bool = False,
) -> Table:
    """
    Creates a rich table to format the search results

    :param List[Account] accounts: List of accounts to format
    :param Optional[int] highlighted_row: Row of table to be highlighted
    :param bool show_ids: Indicates whether to display the IDs. Defaults to False
    :return: The formatted table
    :rtype: Table
    """
    panel_table = Table()
    panel_table.add_column("Username")
    panel_table.add_column("Service")
    panel_table.add_column("URL")

    if show_ids:
        panel_table.add_column("ID", style="bright_black")

    for idx, account in enumerate(accounts):
        username = _default_if_empty(account.username)
        service = _default_if_empty(account.service)
        url = _default_if_empty(account.url)
        id = _default_if_empty(account.id)

        if idx == highlighted_row:
            username = _highlight_text(username)
            service = _highlight_text(service)
            url = _highlight_text(url)
            id = _highlight_text(account.id)

        if show_ids:
            panel_table.add_row(username, service, url, id)
        else:
            panel_table.add_row(username, service, url)

    return panel_table
