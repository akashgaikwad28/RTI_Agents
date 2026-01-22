# helpers.py - auto-generated
from pathlib import Path

def load_prompt(name: str) -> str:
    path = Path(__file__).parent.parent / "prompts" / f"{name}_prompt.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")
