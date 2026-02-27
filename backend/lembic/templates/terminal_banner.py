"""ASCII banner displayed when an in-app terminal opens."""

# ANSI escape helpers
_BOLD = "\033[1m"
_DIM = "\033[2m"
_CYAN = "\033[36m"
_RESET = "\033[0m"

TERMINAL_BANNER = (
    f"\r\n"
    f"  {_BOLD}{_CYAN}╦  ╔═╗╔╦╗╔╗ ╦╔═╗{_RESET}\r\n"
    f"  {_BOLD}{_CYAN}║  ║╣ ║║║╠╩╗║║  {_RESET}\r\n"
    f"  {_BOLD}{_CYAN}╩═╝╚═╝╩ ╩╚═╝╩╚═╝{_RESET}\r\n"
    f"  {_DIM}interactive notebooks{_RESET}\r\n"
    f"\r\n"
).encode("utf-8")
