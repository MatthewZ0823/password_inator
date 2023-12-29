import json

import unittest
import os

from pprint import pprint  # noqa
from rich.table import Table  # noqa
from rich import print as rprint  # noqa


# from src.account import Account, HIDDEN_TEXT, EMPTY_TEXT, account_from_dict, load_accounts_from_file
import src.account as account
import src.constants.strings as STRINGS

# from password_utils import generate_password

test_accounts = [
    {
        "password": "password",
        "username": "username",
        "service": "service",
        "url": "url",
        "id": "9a5f74fd89d84d65b281ad6973682319",
    },
    {
        "password": None,
        "username": "",
        "service": None,
        "url": None,
        "id": "40ee92fe284444d881d2509447420a64",
    },
    {
        "password": "djsaoijf@#%69",
        "username": "I have a very mature sense of humor",
        "service": None,
        "url": "www.google.com",
        "id": "8e899c92394f4a80b3c2a91a9095d886",
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

            test_fields[0] = STRINGS.EMPTY_TEXT
            table = test_account.get_table(display_password=False)

            for idx, row in enumerate(table.columns[1].cells):
                if idx == 0:
                    self.assertEqual(row, STRINGS.HIDDEN_TEXT)
                else:
                    self.assertEqual(row, test_fields[idx])

        with self.subTest("Test Account with no Fields"):
            test_fields = [None, None, None, None]
            test_account = account.Account(*test_fields)

            table = test_account.get_table(display_password=True)

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, STRINGS.EMPTY_TEXT)

            table = test_account.get_table(display_password=False)

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, STRINGS.EMPTY_TEXT)

        with self.subTest("Test Account with Mixed"):
            test_fields = [None, "eaijf_fdajs@Fj$%♪69", "", None]
            test_account = account.Account(*test_fields)

            table = test_account.get_table(display_password=True)
            rows = list(table.columns[1].cells)

            self.assertEqual(rows[0], STRINGS.EMPTY_TEXT)
            self.assertEqual(rows[1], test_fields[1])
            self.assertEqual(rows[2], STRINGS.EMPTY_TEXT)
            self.assertEqual(rows[3], STRINGS.EMPTY_TEXT)

            table = test_account.get_table(display_password=False)
            rows = list(table.columns[1].cells)

            self.assertEqual(rows[0], STRINGS.EMPTY_TEXT)
            self.assertEqual(rows[1], test_fields[1])
            self.assertEqual(rows[2], STRINGS.EMPTY_TEXT)
            self.assertEqual(rows[3], STRINGS.EMPTY_TEXT)

    def test_account_from_dict(self):
        with self.subTest("Test Account with all Fields"):
            test_fields = [
                "password",
                "username",
                "service",
                "url",
                "035d0b2a3cc644d4914e31915eb87673",
            ]
            test_account = account.Account(*test_fields)
            test_dict = {
                "password": "password",
                "username": "username",
                "service": "service",
                "url": "url",
                "id": "035d0b2a3cc644d4914e31915eb87673",
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

            account_from_d = account.account_from_dict(test_dict)

            self.assertEqual(account_from_d.password, test_account.password)
            self.assertEqual(account_from_d.username, test_account.username)
            self.assertEqual(account_from_d.service, test_account.service)
            self.assertEqual(account_from_d.url, test_account.url)
            self.assertTrue(account.is_valid_uuid(test_account.id))

        with self.subTest("Test Account with some Fields"):
            test_fields = [None, "eaijf_fdajs@Fj$%♪69", "", None]
            test_account = account.Account(*test_fields)
            test_dict = {
                "password": None,
                "username": "eaijf_fdajs@Fj$%♪69",
                "service": "",
                "url": None,
            }

            account_from_d = account.account_from_dict(test_dict)

            self.assertEqual(account_from_d.password, test_account.password)
            self.assertEqual(account_from_d.username, test_account.username)
            self.assertEqual(account_from_d.service, test_account.service)
            self.assertEqual(account_from_d.url, test_account.url)
            self.assertTrue(account.is_valid_uuid(test_account.id))

    def test_load_accounts_from_file(self):
        expected_accounts = [
            account.Account(
                "password",
                "username",
                "service",
                "url",
                "9a5f74fd89d84d65b281ad6973682319",
            ),
            account.Account(None, "", None, None, "40ee92fe284444d881d2509447420a64"),
            account.Account(
                "djsaoijf@#%69",
                "I have a very mature sense of humor",
                None,
                "www.google.com",
                "8e899c92394f4a80b3c2a91a9095d886",
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

    def test_write_accounts_to_file(self):
        test_files_path = "tests/test_files"
        test_file_name = "test_write_accounts"

        path = f"{test_files_path}/{test_file_name}.json"
        accounts = [
            account.account_from_dict(test_account) for test_account in test_accounts
        ]

        account.write_accounts_to_file(path, accounts)

        expected = [
            {
                "password": "password",
                "username": "username",
                "service": "service",
                "url": "url",
                "id": "9a5f74fd89d84d65b281ad6973682319",
            },
            {
                "password": None,
                "username": None,
                "service": None,
                "url": None,
                "id": "40ee92fe284444d881d2509447420a64",
            },
            {
                "password": "djsaoijf@#%69",
                "username": "I have a very mature sense of humor",
                "service": None,
                "url": "www.google.com",
                "id": "8e899c92394f4a80b3c2a91a9095d886",
            },
        ]

        with open(path, "r") as f:
            file_content = json.load(f)

            self.assertEqual(file_content, expected)

    def test_load_and_save_to_file(self):
        test_files_path = "tests/test_files"
        test_file_name = "test_save_and_load_accounts"

        new_account = account.Account(
            "afdia912jd@", "my_user", "this_service", "google.com"
        )

        path = f"{test_files_path}/{test_file_name}.json"

        account.write_accounts_to_file(path, [new_account])
        loaded = account.load_accounts_from_file(path)

        self.assertEqual(new_account, loaded[0])

        account.save_account_to_file(path, new_account)
        loaded = account.load_accounts_from_file(path)

        self.assertEqual(new_account, loaded[-1])


if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
