from .getch import getch
from .constants import bytes as BYTES

EXIT_CHARS = [b"\r", b"\x03", b"\x04"]


class Live_Input:
    def __init__(self):
        self.input = ""

    def process_next_input(self) -> bool:
        """
        Appends the next character the user types into the terminal onto self.input
        Returns True iff the next user input should not be processed
        """
        next_byte = getch()

        if next_byte in EXIT_CHARS:
            return True

        if next_byte == BYTES.BACKSPACE_BYTE:
            self.input = self.input[:-1]
            return False

        if next_byte == BYTES.FUNCTION_ARROW_BYTE:
            # Function bytes take up two bytes, so we need to consume the next byte
            next_byte = getch()
            return False

        try:
            if isinstance(next_byte, bytes):
                self.input += next_byte.decode("UTF-8")
                return False
        except UnicodeDecodeError:
            return False

        return True
