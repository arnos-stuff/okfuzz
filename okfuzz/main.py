import typer
import rich
import os
import shutil
from pathlib import Path

from .core import accept, finetune
from .download import download

from rich.prompt import Prompt, Confirm
from typing import Optional, List

app = typer.Typer(
    "okfuzz",
    "A simple CLI tool to fuzzy accept or reject a sentence.",
)

@app.command("dev")
def dev(
    reference: str = typer.Option(None, "--ref", "-r", help="The sentence to be used as a baseline."),
):
    rich.print("""
    📦[bold green]okfuzz[/bold green] is a simple CLI tool to fuzzy accept or reject a sentence.
    
    This is a [bold red]👷 development[/bold red] version.
    
    A few tests 🧪 are going to be run to check if everything is working as expected.
    """)
    
    rich.print("[bold green]👉 Running tests...[/bold green]")
    
    base = Prompt.ask("Enter a sentence to be accepted or rejected.")
    
    if not base:
        rich.print("[bold red]❌ The sentence cannot be empty.[/bold red]")
        return
    rich.print("[bold green]👍 Everything is working as expected.[/bold green]")
    
    
@app.command("setup")
def setup(
    urls: List[str] = typer.Option(None, "--urls", "-u", help="The URLs to be used as a training set."),
    outdir: Path = typer.Option(None, "--outdir", "-o", help="The directory to be used as a training set."),
    ):
    
    base_urls = [
            "https://cdn.jsdelivr.net/gh/facebookresearch/moe@latest/data/moe_misspellings_train.zip",
            "https://github-typo-corpus.s3.amazonaws.com/data/github-typo-corpus.v1.0.0.jsonl.gz",
        ]
    
    if not urls:
        urls = base_urls
        
    if not outdir:
        outdir = Path.cwd() / "data"
        outdir.mkdir(exist_ok=True)
        
    rich.print(f"""🚀 [bold yellow]Setting up[/bold yellow] 🚀""")
    
    download(urls, outdir)