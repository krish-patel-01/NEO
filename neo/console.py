"""Coloured console output for the agent's reasoning trace."""

BRIGHT_GREEN = "\033[38;2;0;255;1m"
BRIGHT_ORANGE = "\033[38;2;255;128;0m"
RESET = "\033[0m"


def print_text(text: str, color: str = "o") -> None:
    """Print text in green ("g") for observations, orange otherwise."""
    prefix = BRIGHT_GREEN if color == "g" else BRIGHT_ORANGE
    print(prefix + text + RESET)
