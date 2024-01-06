from typing import Dict

from ..encryption.master_password import verify_master_password
from ..encryption.encrypt_password import encrypt_password, decrypt_password
from ..utils.aes_utils import create_salt


class Password:
    def __init__(self, encrypted_password: bytes, salt: str, nonce: bytes):
        self.encrypted_password = encrypted_password
        self.salt = salt
        self.nonce = nonce

    def decrypt(self, master_password: str) -> str:
        """
        Decrypts the associated password using the master password

        :param str master_password: master password to use to decrypt Password.
        Should be the same password used to encrypt Password
        :return: the decrypted password
        :rtype: str
        :raises ValueError: if master password is incorrect
        """
        return decrypt_password(
            master_password, self.salt, self.nonce, self.encrypted_password
        )

    def to_json_serializable(self) -> Dict[str, str]:
        """
        Converts Password object into a json serializable form

        :return: serializable dictionary representation of Password
            `encrypted_password` and `nonce` are stored as hex representations
        :rtype: Dict[str, str]
        """
        return {
            "encrypted_password": self.encrypted_password.hex(),
            "salt": self.salt,
            "nonce": self.nonce.hex(),
        }

    def __str__(self):
        s = ""

        s += f"encrypted_password: {self.encrypted_password.hex()}\n"
        s += f"salt: {self.salt}\n"
        s += f"nonce: {self.nonce.hex()}"

        return s

    @staticmethod
    def from_json_serilizable(d: Dict[str, str]):
        """
        Converts from a json serializable form of password into a Password object

        :return: Password object representation of the serializable dictionary
        :rtype: Password | None
        """
        try:
            encrypted_password = bytes.fromhex(d["encrypted_password"])
            salt = d["salt"]
            nonce = bytes.fromhex(d["nonce"])

            return Password(encrypted_password, salt, nonce)
        except KeyError:
            return None

    @staticmethod
    def from_plaintext(plaintext_password: str, master_password: str):
        """
        Creates a Password Object from encrypting plaintext_password with the master password

        :param str plaintext_password: plaintext password to encrypt
        :param str master_password: master password used to encrypt all passwords.
        Should be the same as the password encoded in master.txt
        :return: password object with the encrypted password, salt and nonce
        :rtype: Password
        :raises ValueError: if master_password does not match the master password saved in master.txt
        :raises FileNotFoundError: if `master.txt` is not found
        """
        if not verify_master_password(master_password):
            raise ValueError("Master Password is Incorrect")

        salt = create_salt(32)
        encrypted, nonce = encrypt_password(master_password, salt, plaintext_password)

        return Password(encrypted, salt, nonce)
