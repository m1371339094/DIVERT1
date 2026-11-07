"""
chat.py — Talk to the Online Safety Companion agent
====================================================
Starts an interactive terminal conversation with the deployed
online_safety_companion agent on watsonx Orchestrate.

Usage:
    python chat.py

Requirements:
    - ibm-watsonx-orchestrate installed
    - .env file with WATSONX_URL and WATSONX_APIKEY
"""

import subprocess
import sys
import os
import re
from pathlib import Path

# Force UTF-8 on Windows so any unicode in agent replies prints correctly.
if sys.platform == "win32":
    import io, ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    # Re-open stdin in UTF-8 so input() doesn't raise EOFError from encoding mismatch
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Load .env into the current process environment
# ---------------------------------------------------------------------------
def load_env() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("ERROR: .env file not found. Run .\\run.ps1 first.")
        sys.exit(1)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), value)


# ---------------------------------------------------------------------------
# Re-activate the environment (token refresh)
# ---------------------------------------------------------------------------
def activate_env() -> None:
    api_key = os.environ.get("WATSONX_APIKEY", "")
    if not api_key:
        print("ERROR: WATSONX_APIKEY not found in .env")
        sys.exit(1)
    print("Connecting to watsonx Orchestrate ...", end=" ", flush=True)
    result = subprocess.run(
        ["orchestrate", "env", "activate", "online-safety-companion",
         "--api-key", api_key],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("\nERROR: Could not authenticate.")
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(1)
    print("Connected\n")


# ---------------------------------------------------------------------------
# Send one message; return the server-assigned thread_id for this session.
# On the first call pass thread_id=None so the server creates a new thread.
# On subsequent calls pass the thread_id returned by the first call.
# ---------------------------------------------------------------------------
def ask(message: str, thread_id: str | None, show_reasoning: bool = False) -> str | None:
    """Send message, print reply, return thread_id (from first call or existing)."""
    cmd = [
        "orchestrate", "chat", "ask",
        "--agent-name", "online_safety_companion",
    ]
    # Only attach thread-id after the first message (when we have one)
    if thread_id:
        cmd += ["--thread-id", thread_id]
    if show_reasoning:
        cmd.append("--include-reasoning")
    cmd.append(message)

    print("  (Thinking...)", flush=True)

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")

    # Capture thread ID from output (appears as "[INFO] - Thread ID: <uuid>")
    new_thread_id = thread_id
    for line in (result.stdout + result.stderr).splitlines():
        m = re.search(r"thread.?id[:\s]+([0-9a-f\-]{36})", line, re.IGNORECASE)
        if m:
            new_thread_id = m.group(1)
            break

    # Hard error — nothing came back at all
    if result.returncode != 0 and not result.stdout.strip():
        err = result.stderr.strip() or "No output received."
        first_error = next((l for l in err.splitlines() if l.strip()), err)
        print(f"\n[Could not get a reply: {first_error}]\n")
        return new_thread_id

    # The ADK wraps the reply in a Rich box:
    #   ╭─ robot agent_name ──╮
    #   │  <reply text>       │
    #   ╰─────────────────────╯
    # Extract the text inside the box borders.
    reply = _extract_box_reply(result.stdout)

    if not reply:
        # Fallback: strip log lines and show whatever is left
        lines = result.stdout.splitlines()
        reply_lines = [l for l in lines
                       if not l.startswith("[INFO]")
                       and not l.startswith("[DEBUG]")
                       and not l.startswith("[WARNING]")
                       and not l.startswith("[ERROR]")
                       and not l.startswith("╭") and not l.startswith("╰")]
        reply = "\n".join(reply_lines).strip()

    if not reply:
        reply = "(No reply received — check agent configuration in Orchestrate UI)"

    safe_reply = reply.encode("utf-8", errors="replace").decode("utf-8")
    print(f"\nCompanion: {safe_reply}\n")
    return new_thread_id


def _extract_box_reply(stdout: str) -> str:
    """Extract agent reply text from inside the Rich box borders the ADK uses."""
    inside = False
    reply_lines = []
    for line in stdout.splitlines():
        # Box starts at the agent name header line
        if line.startswith("╭") or line.startswith("\u256d"):
            inside = True
            continue
        # Box ends at the bottom border
        if line.startswith("╰") or line.startswith("\u2570"):
            inside = False
            continue
        if inside:
            # Strip the leading "│ " border character and trailing spaces
            clean = re.sub(r"^[│\u2502]\s?", "", line).rstrip()
            # Skip pure log lines inside the box
            if clean.startswith("[INFO]") or clean.startswith("[DEBUG]"):
                continue
            reply_lines.append(clean)
    return "\n".join(reply_lines).strip()


# ---------------------------------------------------------------------------
# Main interactive loop
# ---------------------------------------------------------------------------
def main() -> None:
    load_env()
    activate_env()

    print("=" * 60)
    print("  Online Safety Companion")
    print("  Powered by IBM watsonx Orchestrate")
    print("=" * 60)
    print("  Type your message and press Enter.")
    print("  Commands:  /quit  exit   /reason  toggle reasoning")
    print("=" * 60 + "\n")

    print("Companion: Hi! I'm your Online Safety Companion.\n")
    print("  I help you check people, messages, and requests online.")
    print("  You decide what to do. I only give information and options.\n")
    print("  What would you like help with today?\n")

    thread_id: str | None = None   # will be set after first message
    show_reasoning = False

    while True:
        # Flush prompt explicitly — needed when stdout is wrapped
        sys.stdout.write("You: ")
        sys.stdout.flush()
        try:
            user_input = sys.stdin.readline()
            if not user_input:          # readline returns "" on true EOF (Ctrl+Z)
                print("\n\nGoodbye. Stay safe online.")
                break
            user_input = user_input.strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye. Stay safe online.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "quit", "exit", "/exit"):
            print("\nGoodbye. Stay safe online.")
            break

        if user_input.lower() == "/reason":
            show_reasoning = not show_reasoning
            print(f"[Reasoning trace: {'ON' if show_reasoning else 'OFF'}]\n")
            continue

        thread_id = ask(user_input, thread_id, show_reasoning)


if __name__ == "__main__":
    main()
