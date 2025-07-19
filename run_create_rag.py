#!/usr/bin/env python3
"""
Script to create RAG database from PDF files.

Usage:
    python run_create_rag.py [--pdf-dir PDF_DIR] [--clear-existing]
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from pipelines.create_rag_pipeline import create_rag_pipeline
from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()
app = typer.Typer(help="Create RAG database from PDF files")


@app.command()
def create_rag(
    pdf_dir: Optional[str] = typer.Option(
        None, "--pdf-dir", "-d", help="Directory containing PDF files"
    ),
    clear_existing: bool = typer.Option(
        False,
        "--clear-existing",
        "-c",
        help="Clear existing documents from vector store before processing",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """Create RAG database from PDF files."""

    # Load configuration
    config = load_config("rag")

    # Use config default if not provided
    if pdf_dir is None:
        pdf_dir = config.get("pdf_directory", "data/pdfs")

    # Validate PDF directory
    pdf_path = Path(pdf_dir) if pdf_dir else Path("data/pdfs")
    if not pdf_path.exists():
        console.print(f"[red]❌ PDF directory does not exist: {pdf_path}[/red]")
        raise typer.Exit(1)

    pdf_files = list(pdf_path.glob("*.pdf"))
    if not pdf_files:
        console.print(f"[yellow]⚠️ No PDF files found in {pdf_path}[/yellow]")
        console.print("Please add PDF files to the directory and run again.")
        raise typer.Exit(1)

    # Display configuration
    console.print(f"[blue]🚀 Starting RAG Database Creation Pipeline[/blue]")
    console.print(f"📁 PDF Directory: {pdf_path}")
    console.print(f"🗑️ Clear Existing: {clear_existing}")
    console.print(f"📄 PDF Files Found: {len(pdf_files)}")

    if verbose:
        for pdf_file in pdf_files:
            console.print(f"   • {pdf_file.name}")

    try:
        # Run the pipeline
        with console.status("[green]Processing PDFs and creating vector database..."):
            result = create_rag_pipeline.invoke(
                {"pdf_directory": str(pdf_path), "clear_existing": clear_existing}
            )

        # Display results
        display_results(result)

        if result.get("status") == "success":
            console.print(
                "[green]✅ RAG Database creation completed successfully![/green]"
            )
            return
        else:
            console.print("[red]❌ RAG Database creation failed![/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]❌ Error running RAG pipeline: {e}[/red]")
        raise typer.Exit(1)


def display_results(result: dict):
    """Display pipeline results in a nice table."""
    console.print("\n")

    # Main results table
    table = Table(title="📊 RAG Database Creation Results")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    status = result.get("status", "unknown")
    message = result.get("message", "No message")
    documents_processed = result.get("documents_processed", 0)

    table.add_row("Status", status)
    table.add_row("Message", message)
    table.add_row("Documents Processed", str(documents_processed))

    if "collection_info" in result:
        collection_info = result["collection_info"]
        table.add_row("Collection Name", collection_info.get("collection_name", "N/A"))
        table.add_row("Total Documents", str(collection_info.get("document_count", 0)))
        table.add_row("Vector DB Path", collection_info.get("vector_db_path", "N/A"))

    if "validation" in result:
        validation = result["validation"]
        table.add_row("Validation Status", validation.get("status", "N/A"))
        table.add_row("Validation Message", validation.get("message", "N/A"))

    console.print(table)


if __name__ == "__main__":
    app()
