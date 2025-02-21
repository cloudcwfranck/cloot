
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from openai_helper import OpenAIHelper

app = typer.Typer(help="CloudBot - Your AI Cloud Engineering Assistant")
console = Console()
ai_helper = OpenAIHelper()

@app.command()
def ask(
    query: str = typer.Argument(..., help="Your cloud engineering question or request"),
):
    """
    Ask CloudBot to generate cloud commands or provide explanations
    """
    with console.status("[bold green]Generating response..."):
        response = ai_helper.generate_response(query)
        
    console.print(Panel(
        Markdown(response),
        title="CloudBot Response",
        border_style="blue"
    ))

@app.command()
def version():
    """Display the current version of CloudBot"""
    console.print("CloudBot v1.0.0")
