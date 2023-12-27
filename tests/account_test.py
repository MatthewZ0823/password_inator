import json
from pprint import pprint
import unittest
import os

from rich.table import Table
from rich import print as rprint

# from src.account import Account, HIDDEN_TEXT, EMPTY_TEXT, account_from_dict, load_accounts_from_file
import src.account as account
import src.constants.strings as strings

# from password_utils import generate_password

test_accounts = [
    {
        "password": "password",
        "username": "username",
        "service": "service",
        "url": "url",
    },
    {"password": None, "username": "", "service": None, "url": None},
    {
        "password": "djsaoijf@#%♪69",
        "username": "I have a very mature sense of humor",
        "service": None,
        "url": "www.google.com",
    },
]


def create_test_accounts(path: str, filename: str):
    if not os.path.exists(path):
        os.makedirs(path)

    with open(f"{path}/{filename}.json", "w") as f:
        json.dump(test_accounts, f, indent=4)


class TestAccount(unittest.TestCase):
    def test_get_table(self):
        with self.subTest("Test Account with all Fields"):
            test_fields = ["password", "username", "service", "url"]
            test_account = account.Account(*test_fields)

            table = test_account.get_table(display_password=True)

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, test_fields[idx])

            test_fields[0] = strings.EMPTY_TEXT
            table = test_account.get_table(display_password=False)

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, test_fields[idx])

        with self.subTest("Test Account with no Fields"):
            test_fields = [None, None, None, None]
            test_account = account.Account(*test_fields)

            table = test_account.get_table(display_password=True)

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, strings.EMPTY_TEXT)

            table = test_account.get_table(display_password=False)

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, strings.EMPTY_TEXT)

        with self.subTest("Test Account with Mixed"):
            test_fields = [None, "eaijf_fdajs@Fj$%♪69", "", None]
            test_account = account.Account(*test_fields)

            table = test_account.get_table(display_password=True)
            rows = list(table.columns[1].cells)

            self.assertEqual(rows[0], strings.EMPTY_TEXT)
            self.assertEqual(rows[1], test_fields[1])
            self.assertEqual(rows[2], strings.EMPTY_TEXT)
            self.assertEqual(rows[3], strings.EMPTY_TEXT)

            table = test_account.get_table(display_password=False)
            rows = list(table.columns[1].cells)

            self.assertEqual(rows[0], strings.EMPTY_TEXT)
            self.assertEqual(rows[1], test_fields[1])
            self.assertEqual(rows[2], strings.EMPTY_TEXT)
            self.assertEqual(rows[3], strings.EMPTY_TEXT)

    def test_account_from_dict(self):
        with self.subTest("Test Account with all Fields"):
            test_fields = ["password", "username", "service", "url"]
            test_account = account.Account(*test_fields)
            test_dict = {
                "password": "password",
                "username": "username",
                "service": "service",
                "url": "url",
            }
            self.assertEqual(account.account_from_dict(test_dict), test_account)

        with self.subTest("Test Account with no Fields"):
            test_fields = [None, None, None, None]
            test_account = account.Account(*test_fields)
            test_dict = {
                "password": None,
                "username": None,
                "service": None,
                "url": None,
            }
            self.assertEqual(account.account_from_dict(test_dict), test_account)

        with self.subTest("Test Account with some Fields"):
            test_fields = [None, "eaijf_fdajs@Fj$%♪69", "", None]
            test_account = account.Account(*test_fields)
            test_dict = {
                "password": None,
                "username": "eaijf_fdajs@Fj$%♪69",
                "service": "",
                "url": None,
            }
            self.assertEqual(account.account_from_dict(test_dict), test_account)

    def test_load_accounts_from_file(self):
        expected_accounts = [
            account.Account("password", "username", "service", "url"),
            account.Account(None, "", None, None),
            account.Account(
                "djsaoijf@#%♪69",
                "I have a very mature sense of humor",
                None,
                "www.google.com",
            ),
        ]

        test_files_path = "tests/test_files"
        test_file_name = "test_load_accounts"

        create_test_accounts(test_files_path, test_file_name)

        loaded_accounts = account.load_accounts_from_file(
            f"{test_files_path}/{test_file_name}.json"
        )

        for loaded, expected in zip(loaded_accounts, expected_accounts):
            self.assertEqual(loaded, expected)

    def test_save_account_to_file(self):
        test_files_path = "tests/test_files"
        test_file_name = "test_save_accounts"

        create_test_accounts(test_files_path, test_file_name)
        new_account = account.Account(
            "password123", "John Smith", "example website", "www.example.com"
        )

        account.save_account_to_file(
            f"{test_files_path}/{test_file_name}.json", new_account
        )

        with open(f"{test_files_path}/{test_file_name}.json", "r") as f:
            file_content = json.load(f)
            self.assertEqual(file_content[-1], new_account.__dict__)


if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
