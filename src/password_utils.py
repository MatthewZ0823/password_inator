import secrets


def generate_password(
    length: int = 16
) -> str:
    """
    Generate a password with the given length (default 16)
    """
    password = secrets.token_urlsafe(length)[:length]

    while password.isalnum():
        password = secrets.token_urlsafe(length)[:length]

    return password
