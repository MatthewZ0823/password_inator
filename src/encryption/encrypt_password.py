from Cryptodome.Cipher import AES
from typing import Tuple
from ..constants.strings import MASTER_PASSWORD_ERROR
from ..encryption.master_password import verify_master_password
from ..utils.aes_utils import create_key


def encrypt_password(
    master_password: str, salt: str, plaintext_password: str
) -> Tuple[bytes, bytes]:
    """
    Encrypts `plaintext_password` with `master_password`

    :param str master_password: password to use to encrypt `plaintext_password`
    :param str salt: salt to use to encrypt password
    :param str plaintext_password: password to encrypt
    :return: Tuple with two entries
        First entry is the encrypted password
        Second entry is the nonce used
    :rtype: Tuple[bytes, bytes]
    """
    key = create_key(master_password, salt)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext = cipher.encrypt(plaintext_password.encode("utf-8"))

    return (ciphertext, cipher.nonce)


def decrypt_password(
    master_password: str, salt: str, nonce: bytes, encrypted_password: bytes
) -> str:
    """
    Decrypts `encrypted_password` encrypted with `master_password`

    :param str master_password: master password used to encrypt the password
    :param str salt: salt used to encrypt the password
    :param bytes nonce: nonce generated by the original cipher
    :param bytes encrypted_password: the password to decrypt
    :return: the decrypted password
    :rtype: str
    :raises ValueError: if master password is incorrect
    """
    if not verify_master_password(master_password):
        raise ValueError(MASTER_PASSWORD_ERROR)

    key = create_key(master_password, salt)
    cipher = AES.new(key, AES.MODE_EAX, nonce)
    decoded = cipher.decrypt(encrypted_password)

    return decoded.decode("utf-8")
