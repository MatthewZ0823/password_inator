from ..constants.paths import MASTER_PATH
from ..constants.numbers import KEY_SIZE
from ..utils.aes_utils import create_salt
from ..utils.password_utils import hash_password


def save_master_password(password: str):
    """
    Hashes and saves the master password + salt
    The master password is used to decrypt all passwords

    :param str password: password to save
    """
    with open(MASTER_PATH, "w") as f:
        salt = create_salt(KEY_SIZE)
        hash = hash_password(password, salt)

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
    with open(MASTER_PATH, "r") as f:
        lines = f.readlines()

        salt = lines[1].strip()
        hash = lines[3].strip()

        new_hash = hash_password(password, salt)

        return hash == new_hash
