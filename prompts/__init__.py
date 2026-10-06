from pathlib import Path

_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Load a system prompt by name from prompts/<name>.txt.

    Args:
        name: Filename without extension, e.g. "expense_logging".

    Returns:
        The prompt text, stripped of leading/trailing whitespace.

    Raises:
        FileNotFoundError: if no matching .txt file exists.
    """
    path = _DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"No prompt file found at {path}")
    return path.read_text(encoding="utf-8").strip()
