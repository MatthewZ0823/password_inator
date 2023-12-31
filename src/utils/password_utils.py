import secrets


legal_password_characters = "~`!@#$%^&*()_-+={[}]|:;<,>.?/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_password(length: int = 16) -> str:
    """
    Generate a password with the given length (default 16)
    """
    password = "".join(
        [secrets.choice(legal_password_characters) for _ in range(length)]
    )

    while password.isalnum():
        password = secrets.token_urlsafe(length)[:length]

    return password
