from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import get_random_bytes

from ..constants.numbers import KEY_SIZE


def create_salt(size: int) -> str:
    """
    Creates a random salt of a specified size

    :param int size: size of salt in bytes
    :return: hex representation of salt
    :rtype: str
    """
    return get_random_bytes(size).hex()


def create_key(password: str, salt: str) -> bytes:
    """
    Creates a 32-bit AES key using a password and a salt. This is done using the scrypt KDF

    :param str password: password to generate key from
    :param str salt: salt to generate key from
    :return: The 32-bit AES key
    :rtype: bytes
    """
    return scrypt(password, salt, KEY_SIZE, N=2**14, r=8, p=1)  # type: ignore
