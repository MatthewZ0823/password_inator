import unittest
from src.utils.password_utils import (
    generate_password,
    special_characters,
    digits,
    lowercase_letters,
    uppercase_letters,
)


def is_legal_password(password: str):
    contains_special = False
    contains_digit = False
    contains_lowercase = False
    contains_uppercase = False

    for c in password:
        if c in special_characters:
            contains_special = True
        elif c in digits:
            contains_digit = True
        elif c in lowercase_letters:
            contains_lowercase = True
        elif c in uppercase_letters:
            contains_uppercase = True

    return (
        contains_special
        and contains_digit
        and contains_lowercase
        and contains_uppercase
    )


class TestPassword(unittest.TestCase):
    def test_generate_password(self):
        self.assertEqual(len(generate_password()), 16)
        self.assertEqual(len(generate_password(10)), 10)
        self.assertEqual(len(generate_password(1)), 1)

        self.assertTrue(is_legal_password(generate_password()))
        self.assertTrue(is_legal_password(generate_password(10)))


if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
