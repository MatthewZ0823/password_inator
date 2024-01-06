import json

import unittest
import os

from pprint import pprint  # noqa
from rich.table import Table  # noqa
from rich import print as rprint  # noqa


# from src.account import Account, HIDDEN_TEXT, EMPTY_TEXT, account_from_dict, load_accounts_from_file
from src.accounts import account, file_manager
from src.constants import strings as STRINGS

# from password_utils import generate_password

test_accounts = [
    {
        "encrypted_password": "hash",
        "username": "username",
        "service": "service",
        "url": "url",
        "salt": "2668c9cdd9935ddb7c9426d6f9e65b751c35d8940eb6d9e4f4c11c6220615e80",
        "id": "9a5f74fd89d84d65b281ad6973682319",
    },
    {
        "encrypted_password": None,
        "username": "",
        "service": None,
        "url": None,
        "salt": "59d28f8b61244753a4f02b6452253cb47d4570200cce479b423ff83db5a561f8",
        "id": "40ee92fe284444d881d2509447420a64",
    },
    {
        "encrypted_password": "djsaoijf@#%69",
        "username": "I have a very mature sense of humor",
        "service": None,
        "url": "www.google.com",
        "salt": "31dc84b0f25ebfda29d3f918d120ed76c2c1e650aecc1e059316f1ad69e077e4",
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
            test_fields = ["hash", "username", "service", "url", "salt"]
            test_account = account.Account(*test_fields)

            test_fields[0] = STRINGS.EMPTY_TEXT
            table = test_account.get_table()

            for idx, row in enumerate(table.columns[1].cells):
                if idx == 0:
                    self.assertEqual(row, STRINGS.HIDDEN_TEXT)
                else:
                    self.assertEqual(row, test_fields[idx])

        with self.subTest("Test Account with no Fields"):
            test_account = account.Account()

            table = test_account.get_table()

            for idx, row in enumerate(table.columns[1].cells):
                self.assertEqual(row, STRINGS.EMPTY_TEXT)

        with self.subTest("Test Account with Mixed"):
            test_fields = [None, "eaijf_fdajs@Fj$%♪69", "", None]
            test_account = account.Account(*test_fields)

            table = test_account.get_table()
            rows = list(table.columns[1].cells)

            self.assertEqual(rows[0], STRINGS.EMPTY_TEXT)
            self.assertEqual(rows[1], test_fields[1])
            self.assertEqual(rows[2], STRINGS.EMPTY_TEXT)
            self.assertEqual(rows[3], STRINGS.EMPTY_TEXT)

    def test_account_from_dict(self):
        with self.subTest("Test Account with all Fields"):
            test_account = account.Account(
                "hash",
                "username",
                "service",
                "url",
                "2668c9cdd9935ddb7c9426d6f9e65b751c35d8940eb6d9e4f4c11c6220615e80",
                "9a5f74fd89d84d65b281ad6973682319",
            )
            test_dict = test_accounts[0]
            self.assertEqual(account.account_from_dict(test_dict), test_account)

        with self.subTest("Test Account with no Fields"):
            test_account = account.Account()
            test_dict = {
                "password": None,
                "username": None,
                "service": None,
                "url": None,
            }

            account_from_d = account.account_from_dict(test_dict)

            self.assertEqual(
                account_from_d.encrypted_password, test_account.encrypted_password
            )
            self.assertEqual(account_from_d.username, test_account.username)
            self.assertEqual(account_from_d.service, test_account.service)
            self.assertEqual(account_from_d.url, test_account.url)
            self.assertTrue(account.is_valid_uuid(test_account.id))
            self.assertTrue(len(account_from_d.salt) == 64)

        with self.subTest("Test Account with some Fields"):
            test_account = account.Account(None, "eaijf_fdajs@Fj$%♪69", "", None)
            test_dict = {
                "password": None,
                "username": "eaijf_fdajs@Fj$%♪69",
                "service": "",
                "url": None,
            }

            account_from_d = account.account_from_dict(test_dict)

            self.assertEqual(
                account_from_d.encrypted_password, test_account.encrypted_password
            )
            self.assertEqual(account_from_d.username, test_account.username)
            self.assertEqual(account_from_d.service, test_account.service)
            self.assertEqual(account_from_d.url, test_account.url)
            self.assertTrue(account.is_valid_uuid(test_account.id))
            self.assertTrue(len(account_from_d.salt) == 64)

    def test_load_accounts_from_file(self):
        expected_accounts = [
            account.Account(
                "hash",
                "username",
                "service",
                "url",
                "2668c9cdd9935ddb7c9426d6f9e65b751c35d8940eb6d9e4f4c11c6220615e80",
                "9a5f74fd89d84d65b281ad6973682319",
            ),
            account.Account(
                None,
                None,
                None,
                None,
                "59d28f8b61244753a4f02b6452253cb47d4570200cce479b423ff83db5a561f8",
                "40ee92fe284444d881d2509447420a64",
            ),
            account.Account(
                "djsaoijf@#%69",
                "I have a very mature sense of humor",
                None,
                "www.google.com",
                "31dc84b0f25ebfda29d3f918d120ed76c2c1e650aecc1e059316f1ad69e077e4",
                "8e899c92394f4a80b3c2a91a9095d886",
            ),
        ]

        test_files_path = "tests/test_files"
        test_file_name = "test_load_accounts"

        create_test_accounts(test_files_path, test_file_name)

        loaded_accounts = file_manager.load_accounts_from_file(
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

        file_manager.save_account_to_file(
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

        file_manager.write_accounts_to_file(path, accounts)

        expected = test_accounts.copy()
        # The empty string should've been replaced with None
        expected[1]["username"] = None

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

        file_manager.write_accounts_to_file(path, [new_account])
        loaded = file_manager.load_accounts_from_file(path)

        self.assertEqual(new_account, loaded[0])

        file_manager.save_account_to_file(path, new_account)
        loaded = file_manager.load_accounts_from_file(path)

        self.assertEqual(new_account, loaded[-1])


if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
