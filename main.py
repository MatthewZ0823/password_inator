import typer
from rich.console import Console

console = Console()
err_console = Console(stderr=True)

app = typer.Typer()

@app.command("hi")
def sample_func():
    console.print("[red bold]Hi[/red bold] [yellow]World[yello]")

@app.command("hello")
def sample_func():
    console.print("[red bold]Hello[/red bold] [yellow]World[yello]")

if __name__ == "__main__":
    app()    