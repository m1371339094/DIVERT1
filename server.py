"""
server.py — DIVERT1 | Online Safety Companion
==============================================
Flask server that:
  • Serves the stitch HTML frontend at /
  • Serves the About page at /about
  • Exposes POST /api/chat  → talks to IBM watsonx Orchestrate via chat.py

Run with:
    python server.py
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, abort

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "stitch_divert1_online_safety_companion"
CHAT_HTML    = FRONTEND_DIR / "divert1_safety_companion_chat_wcag_2.1_accessible" / "code.html"
ABOUT_HTML   = FRONTEND_DIR / "divert1_about_architecture" / "code.html"

# ── Import backend helpers ────────────────────────────────────────────────────
from chat import load_env, activate_env, build_clients, send_message

app = Flask(__name__, static_folder=None)

# ── Session state (single-process, single-user dev server) ───────────────────
_state = {
    "ready":          False,
    "run_client":     None,
    "threads_client": None,
    "agent_id":       None,
    "thread_id":      None,
    "init_error":     None,
}


def _ensure_ready():
    """Lazily initialise the watsonx Orchestrate SDK clients."""
    if _state["ready"]:
        return
    if _state["init_error"]:
        raise RuntimeError(_state["init_error"])
    try:
        load_env()
        activate_env()
        rc, tc, aid = build_clients()
        _state["run_client"]     = rc
        _state["threads_client"] = tc
        _state["agent_id"]       = aid
        _state["ready"]          = True
    except SystemExit as e:
        _state["init_error"] = str(e)
        raise RuntimeError(str(e))
    except Exception as e:
        _state["init_error"] = str(e)
        raise


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def chat_page():
    """Serve the WCAG-accessible chat UI."""
    if not CHAT_HTML.exists():
        abort(404, description=f"Chat HTML not found at {CHAT_HTML}")
    return CHAT_HTML.read_text(encoding="utf-8")

@app.route("/about")
def about_page():
    """Redirect to main chat page — About is now an in-page modal."""
    from flask import redirect
    return redirect("/")



@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    POST /api/chat
    Request  JSON: { "message": "...", "thread_id": "..." | null }
    Response JSON: { "reply": "...", "thread_id": "..." }
    """
    data       = request.get_json(force=True, silent=True) or {}
    message    = (data.get("message") or "").strip()
    thread_id  = data.get("thread_id") or _state["thread_id"]

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        _ensure_ready()
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 503

    try:
        reply, new_tid = send_message(
            _state["run_client"],
            _state["threads_client"],
            message,
            _state["agent_id"],
            thread_id,
        )
        _state["thread_id"] = new_tid
        return jsonify({"reply": reply, "thread_id": new_tid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Clear the current conversation thread."""
    _state["thread_id"] = None
    return jsonify({"status": "ok"})


@app.route("/api/status", methods=["GET"])
def api_status():
    """Health-check / connection status."""
    return jsonify({
        "ready": _state["ready"],
        "error": _state["init_error"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  DIVERT1 Online Safety Companion")
    print(f"  ─────────────────────────────────")
    print(f"  Chat : http://localhost:{port}/")
    print(f"  About: http://localhost:{port}/about")
    print(f"  API  : http://localhost:{port}/api/chat\n")
    app.run(host="0.0.0.0", port=port, debug=False)
