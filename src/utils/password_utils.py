import random
import secrets
from Cryptodome.Protocol.KDF import scrypt

special_characters = "~`!@#$%^&*()_-+={[}]|:;<,>.?/"
digits = "0123456789"
lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
uppercase_letters = lowercase_letters.upper()

legal_password_characters = (
    special_characters + digits + lowercase_letters + uppercase_letters
)


def generate_password(length: int = 16) -> str:
    """
    Generate a password with the given length (default 16)
    """
    password = ""
    remainingLength = length

    # Make sure there's at least one of each character type
    if length >= 4:
        password += secrets.choice(special_characters)
        password += secrets.choice(digits)
        password += secrets.choice(lowercase_letters)
        password += secrets.choice(uppercase_letters)
        remainingLength -= 4

    # Fill the rest of the password with random characters
    password += "".join(
        [secrets.choice(legal_password_characters) for _ in range(remainingLength)]
    )

    # Shuffle the characters
    password = "".join(random.sample(password, length))

    return password


def hash_password(password: str, salt: str) -> str:
    """
    Hashes a password with a salt using scrypt

    :param str password: password to encrypt
    :param str salt: salt to apply to password
    :return: hex representation of the hash
    :rtype: str
    """
    return scrypt(password, salt, 32, N=2**14, r=8, p=1).hex()  # type: ignore
