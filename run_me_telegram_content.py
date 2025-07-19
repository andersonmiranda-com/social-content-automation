#!/usr/bin/env python3
"""
Script to run RAG content generation and Telegram publishing pipeline.

Usage:
    python run_rag_content.py [--test-connection] [--dry-run]
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from pipelines.me_telegram_content_pipeline import me_telegram_content_pipeline
from tools.telegram_tool import test_telegram_connection_chain
from utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()
app = typer.Typer(help="Generate and publish RAG content to Telegram")


@app.command()
def generate_and_publish(
    test_connection: bool = typer.Option(
        False,
        "--test-connection",
        "-t",
        help="Test Telegram connection before running pipeline",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Run pipeline without publishing to Telegram"
    ),
):
    """Generate content using RAG and publish to Telegram."""

    console.print(f"[blue]🚀 Starting RAG Content Generation Pipeline[/blue]")

    # Test Telegram connection if requested
    if test_connection:
        console.print("[yellow]🔗 Testing Telegram connection...[/yellow]")
        connection_result = test_telegram_connection_chain.invoke({})

        if connection_result.get("status") != "success":
            console.print(
                f"[red]❌ Telegram connection failed: {connection_result.get('message')}[/red]"
            )
            console.print(
                "Please check your Telegram configuration in configs/telegram.yaml"
            )
            raise typer.Exit(1)
        else:
            console.print("[green]✅ Telegram connection successful![/green]")

    try:
        # Run the pipeline
        with console.status("[green]Generating content and publishing to Telegram..."):
            result = me_telegram_content_pipeline.invoke({})

        # Display results
        display_results(result)

        # Check final status
        validation = result.get("validation", {})
        if validation.get("status") == "success":
            console.print("[green]✅ Pipeline completed successfully![/green]")
            raise typer.Exit(0)
        else:
            console.print("[red]❌ Pipeline failed![/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]❌ Error running pipeline: {e}[/red]")
        raise typer.Exit(1)


def display_results(result: dict):
    """Display pipeline results in a nice table."""
    console.print("\n")

    # Main results table
    table = Table(title="📊 RAG Content Pipeline Results")
    table.add_column("Step", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="white")

    # Topic Selection
    topic_selection = result.get("topic_selection", {})
    table.add_row(
        "Topic Selection",
        topic_selection.get("status", "unknown"),
        topic_selection.get("selected_topic", "N/A"),
    )

    # Content Generation
    content_generation = result.get("content_generation", {})
    content_preview = (
        content_generation.get("generated_content", "")[:50] + "..."
        if content_generation.get("generated_content")
        else "N/A"
    )
    table.add_row(
        "Content Generation",
        content_generation.get("status", "unknown"),
        content_preview,
    )

    # Image Generation
    image_generation = result.get("image_generation", {})
    table.add_row(
        "Image Generation",
        image_generation.get("status", "unknown"),
        f"Model: {image_generation.get('model_used', 'N/A')}",
    )

    # Overlay Application
    overlay_application = result.get("overlay_application", {})
    table.add_row(
        "Image Overlay",
        overlay_application.get("status", "unknown"),
        f"Overlay: {overlay_application.get('overlay_url', 'N/A').split('/')[-1]}",
    )

    # Content Formatting
    content_formatting = result.get("content_formatting", {})
    table.add_row(
        "Content Formatting",
        content_formatting.get("status", "unknown"),
        f"Quote: {content_formatting.get('quote', 'N/A')[:30]}...",
    )

    # Telegram Publication
    telegram_publication = result.get("telegram_publication", {})
    table.add_row(
        "Telegram Publication",
        telegram_publication.get("status", "unknown"),
        telegram_publication.get("message", "N/A"),
    )

    # Validation
    validation = result.get("validation", {})
    table.add_row(
        "Pipeline Validation",
        validation.get("status", "unknown"),
        validation.get("message", "N/A"),
    )

    console.print(table)

    # Show full content if available
    if content_generation.get("generated_content"):
        console.print("\n[bold cyan]📝 Generated Content:[/bold cyan]")
        console.print(content_generation["generated_content"])

        if content_generation.get("quote"):
            console.print(
                f"\n[bold yellow]💬 Quote:[/bold yellow] {content_generation['quote']}"
            )


if __name__ == "__main__":
    app()
