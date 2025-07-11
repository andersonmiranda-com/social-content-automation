import typer
from flows import generate_content
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()


@app.command()
def generate_content_cmd(
    topic: str = typer.Option(..., help="Topic for the reel"),
    output: str = typer.Option("output.json", help="Output JSON file"),
):
    """Generate content for a reel given a topic and save to a JSON file."""
    generate_content.run(topic, output)


# Example command to chain flows (placeholder)
@app.command()
def pipeline(
    topic: str = typer.Option(..., help="Topic for the reel"),
    output: str = typer.Option("output.json", help="Output JSON file"),
):
    """Run the complete pipeline: generate content and publish."""
    generate_content.run(topic, output)
    # Here you could call other flows, e.g.:
    # publish_instagram.run(generated_id)


if __name__ == "__main__":
    app()
