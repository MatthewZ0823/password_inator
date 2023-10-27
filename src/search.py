from fuzzyfinder import fuzzyfinder  # type: ignore
from typing import List, Optional
from .account import Account, AccountFields
from rich.table import Table

from .constants import strings as STRINGS


def find_account_by_field(field: AccountFields, accounts: List[Account], search: str):
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


def default_if_empty(s: Optional[str]) -> str:
    """
    Returns a default empty text string if s is None. Otherwise just returns s
    """
    return s if s is not None else STRINGS.EMPTY_TEXT


def create_search_table(accounts: List[Account]) -> Table:
    """
    Creates a rick table to format the search results (accounts)
    """
    panel_table = Table()
    panel_table.add_column("Username", style="bold")
    panel_table.add_column("Service")
    panel_table.add_column("URL")

    for account in accounts:
        username = default_if_empty(account.username)
        service = default_if_empty(account.service)
        url = default_if_empty(account.url)
        panel_table.add_row(username, service, url)

    return panel_table
