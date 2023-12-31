import uuid


def is_valid_uuid(uuid_hex: str):
    """
    Checks if uuid_hex is a valid hex representation of a uuid

    :param str uuid: uuid to check, as a 32 character lowercase hexadecimal string
    :return: If uuid is a valid uuid
    :rtype: bool
    """
    try:
        uuid_obj = uuid.UUID(uuid_hex)
        return uuid_obj.hex == uuid_hex
    except ValueError:
        return False
