from enum import Enum
from .getch import getch
from ..constants import bytes as BYTES


class Key_Type(Enum):
    EXIT = 0  # ^C, ^D
    UP = 1  # Up arrow on the keyboard
    DOWN = 2  # Down arrow on the keyboard
    STANDARD = (
        3  # Standard character ie. Alphanumric. Will update the self.input string
    )
    SPECIAL = 4  # Some other not before mentioned special character
    UNKNOWN = 5  # Some UnicodeDecodeError or otherwise some other character that can't be interpreted
    ENTER = 6  # Enter


class Live_Input:
    def __init__(self):
        self.input = ""

    def process_next_input(self) -> Key_Type:
        """
        Appends the next character the user types into the terminal onto self.input
        Returns True iff the next user input should not be processed
        """
        next_byte = getch()

        if next_byte in BYTES.EXIT_BYTES:
            return Key_Type.EXIT

        if next_byte == BYTES.ENTER_BYTE:
            return Key_Type.ENTER

        if next_byte == BYTES.BACKSPACE_BYTE:
            self.input = self.input[:-1]
            return Key_Type.SPECIAL

        if next_byte == BYTES.FUNCTION_ARROW_BYTE:
            # Function bytes take up two bytes, so we need to consume the next byte
            next_byte = getch()

            if next_byte == BYTES.UP_ARROW:
                return Key_Type.UP
            if next_byte == BYTES.DOWN_ARROW:
                return Key_Type.DOWN
            return Key_Type.SPECIAL

        try:
            if isinstance(next_byte, bytes):
                self.input += next_byte.decode("UTF-8")
                return Key_Type.STANDARD
        except UnicodeDecodeError:
            return Key_Type.SPECIAL

        return Key_Type.UNKNOWN
