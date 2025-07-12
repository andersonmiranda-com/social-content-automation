"""
File utility functions.
"""


def load_prompt_template(file_path: str) -> str:
    """Loads a prompt template or any text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
