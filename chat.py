"""
chat.py — Talk to the Online Safety Companion
==============================================
Uses the watsonx Orchestrate SDK directly (RunClient + ThreadsClient)
instead of the 'orchestrate chat ask' CLI command, which only works on
local Developer Edition servers and times out on SaaS instances.

Usage:
    python chat.py
"""

import sys
import os
import subprocess
from pathlib import Path

# ── Windows UTF-8 fix ────────────────────────────────────────────────────────
if sys.platform == "win32":
    import io, ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    sys.stdin  = io.TextIOWrapper(sys.stdin.buffer,  encoding="utf-8", errors="replace")

AGENT_NAME = "online_safety_companion"


# ── Load .env ────────────────────────────────────────────────────────────────
def load_env() -> None:
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("ERROR: .env file not found.")
        sys.exit(1)
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


# ── Activate the Orchestrate environment (token refresh) ─────────────────────
def activate_env() -> None:
    api_key = os.environ.get("WATSONX_APIKEY", "")
    if not api_key:
        print("ERROR: WATSONX_APIKEY not found in .env")
        sys.exit(1)
    print("Connecting ...", end=" ", flush=True)
    result = subprocess.run(
        ["orchestrate", "env", "activate", "online-safety-companion",
         "--api-key", api_key],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("\nERROR: Could not authenticate.")
        print(result.stderr.strip() or result.stdout.strip())
        sys.exit(1)
    print("Connected.\n")


# ── Build SDK clients and resolve agent ID ────────────────────────────────────
def build_clients():
    """Return (run_client, threads_client, agent_id)."""
    from ibm_watsonx_orchestrate.client.utils import instantiate_client
    from ibm_watsonx_orchestrate_clients.agents.agent_client import AgentClient
    from ibm_watsonx_orchestrate_clients.chat.run_client import RunClient
    from ibm_watsonx_orchestrate_clients.threads.threads_client import ThreadsClient

    run_client     = instantiate_client(RunClient)
    threads_client = instantiate_client(ThreadsClient)
    agent_client   = instantiate_client(AgentClient)

    # Resolve agent name → ID
    all_agents = agent_client.get()
    agent_list = all_agents if isinstance(all_agents, list) else all_agents.get("data", [])
    agent_id = None
    for a in agent_list:
        if a.get("name") == AGENT_NAME:
            agent_id = a.get("id")
            break

    if not agent_id:
        names = [a.get("name") for a in agent_list]
        print(f"ERROR: Agent '{AGENT_NAME}' not found.")
        print(f"Available agents: {names}")
        sys.exit(1)

    return run_client, threads_client, agent_id


# ── Send a message and return (reply_text, thread_id) ────────────────────────
def send_message(run_client, threads_client, message: str,
                 agent_id: str, thread_id: str | None) -> tuple[str, str | None]:

    # Count current messages so we can detect the new reply
    initial_count = 0
    if thread_id:
        try:
            msgs = threads_client.get_thread_messages(thread_id)
            msg_list = msgs if isinstance(msgs, list) else msgs.get("data", [])
            initial_count = len(msg_list)
        except Exception:
            pass

    # Send the message
    run_resp = run_client.create_run(
        message=message,
        agent_id=agent_id,
        thread_id=thread_id
    )
    thread_id = run_resp.get("thread_id") or thread_id
    run_id    = run_resp.get("run_id")

    # Wait for run to finish
    run_status = run_client.wait_for_run_completion(
        run_id, poll_interval=2, max_retries=90
    )
    if run_status.get("status") in ("failed", "error"):
        return f"[Agent error. Status: {run_status.get('status')}]", thread_id

    # Get the new assistant reply
    try:
        msg = threads_client.poll_for_flow_completion(
            thread_id=thread_id,
            initial_message_count=initial_count,
            poll_interval=1,
            max_retries=30
        )
        if msg:
            return _extract_text(msg), thread_id
    except Exception:
        pass

    # Fallback: grab the last assistant message
    try:
        msgs = threads_client.get_thread_messages(thread_id)
        msg_list = msgs if isinstance(msgs, list) else msgs.get("data", [])
        for m in reversed(msg_list):
            if isinstance(m, dict) and m.get("role") == "assistant":
                text = _extract_text(m)
                if text:
                    return text, thread_id
    except Exception:
        pass

    return "[No reply received.]", thread_id


def _extract_text(msg: dict) -> str:
    """Extract plain text from an assistant message dict."""
    content = msg.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("response_type") == "text":
                    parts.append(item.get("text", ""))
                elif "text" in item:
                    parts.append(item["text"])
        return "\n".join(parts).strip()
    return str(content).strip()


# ── Main interactive loop ─────────────────────────────────────────────────────
def main() -> None:
    load_env()
    activate_env()

    try:
        run_client, threads_client, agent_id = build_clients()
    except SystemExit:
        raise
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    print("=" * 60)
    print("  Online Safety Companion")
    print("  Powered by IBM watsonx Orchestrate")
    print("=" * 60)
    print("  Type your message and press Enter.")
    print("  Type 'quit' to stop.")
    print("=" * 60 + "\n")

    print("Companion: Hi! I'm your Online Safety Companion.\n")
    print("  I help you check people, messages, and requests online.")
    print("  You decide what to do. I only give information and options.\n")
    print("  What would you like help with today?\n")

    thread_id: str | None = None

    while True:
        sys.stdout.write("You: ")
        sys.stdout.flush()
        try:
            user_input = sys.stdin.readline()
            if not user_input:
                print("\nGoodbye. Stay safe online.")
                break
            user_input = user_input.strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye. Stay safe online.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "/quit", "/exit"):
            print("\nGoodbye. Stay safe online.")
            break

        print("  (Thinking...)", flush=True)
        try:
            reply, thread_id = send_message(
                run_client, threads_client, user_input, agent_id, thread_id
            )
            safe = reply.encode("utf-8", errors="replace").decode("utf-8")
            print(f"\nCompanion: {safe}\n")
        except KeyboardInterrupt:
            print("\nGoodbye. Stay safe online.")
            break
        except Exception as e:
            print(f"\n[Error: {e}]\n")


if __name__ == "__main__":
    main()
