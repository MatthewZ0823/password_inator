from Cryptodome.Protocol.KDF import scrypt
from ..constants import paths as PATHS
from ..utils.aes_utils import create_salt


def _hash_password(password: str, salt: str) -> str:
    """
    Hashes a password with a salt using scrypt

    :param str password: password to encrypt
    :param str salt: salt to apply to password
    :return: hex representation of the hash
    :rtype: str
    """
    return scrypt(password, salt, 32, N=2**14, r=8, p=1).hex()  # type: ignore


def save_master_password(password: str):
    """
    Hashes and saves the master password + salt
    The master password is used to decrypt all passwords

    :param str password: password to save
    """
    with open(PATHS.MASTER_PATH, "w") as f:
        salt = create_salt(32)
        hash = _hash_password(password, salt)

        f.write("Salt: \n")
        f.write(salt)
        f.write("\n")
        f.write("Hash: \n")
        f.write(hash)


def verify_master_password(password: str) -> bool:
    """
    Verifies that the hash of the password matches that of the master password

    :param str password: password to verify
    :return: True iff password is the same as the master password
    :rtype: bool
    :raises FileNotFoundError: if master.txt file is not found
    """
    with open(PATHS.MASTER_PATH, "r") as f:
        lines = f.readlines()

        salt = lines[1].strip()
        hash = lines[3].strip()

        new_hash = scrypt(password, salt, 32, N=2**14, r=8, p=1)

        if not isinstance(new_hash, bytes):
            return False

        return hash == new_hash.hex()
