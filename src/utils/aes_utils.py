from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import get_random_bytes


def create_salt(size: int) -> str:
    """
    Creates a random salt of a specified size

    :param int size: size of salt in bytes
    :return: hex representation of salt
    :rtype: str
    """
    return get_random_bytes(size).hex()


def create_key(password: str):
    salt = create_salt(32)
    scrypt(password, salt, 32, N=2**14, r=8, p=1)
