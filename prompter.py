import typer


def ask_yes_no(question: str, default: str = "Y") -> bool:
    """
    Ask a yes or no question, returns True iff the answer is yes
    """
    return typer.prompt(f"{question} (Y/n)", default=default) == "Y"
