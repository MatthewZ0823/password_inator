import random
import secrets


legal_password_characters = "~`!@#$%^&*()_-+={[}]|:;<,>.?/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

special_characters = "~`!@#$%^&*()_-+={[}]|:;<,>.?/"
digits = "0123456789"
lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
uppercase_letters = lowercase_letters.upper()


def generate_password(length: int = 16) -> str:
    """
    Generate a password with the given length (default 16)
    """
    password = ""

    # Make sure there's at least one of each character type
    if length >= 4:
        password += secrets.choice(special_characters)
        password += secrets.choice(digits)
        password += secrets.choice(lowercase_letters)
        password += secrets.choice(uppercase_letters)

    # Fill the rest of the password with random characters
    password += "".join(
        [secrets.choice(legal_password_characters) for _ in range(length - 4)]
    )

    # Shuffle the characters
    password = "".join(random.sample(password, length))

    return password
