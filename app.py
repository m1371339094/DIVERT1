"""
app.py — DIVERT1 | Online Safety Companion
===========================================
Streamlit frontend — "Warm Reassuring Sanctuary" design system
  • Chat  — talk to the companion
  • About — project story, team, design principles

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
from pathlib import Path

from chat import load_env, activate_env, build_clients, send_message

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DIVERT1 — Online Safety Companion",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Image helpers
# ─────────────────────────────────────────────────────────────────────────────
IMG_DIR = Path(__file__).parent / "images"


def img(filename: str) -> str | None:
    p = IMG_DIR / filename
    return str(p) if p.exists() else None


def placeholder(label: str, h: int = 220) -> str:
    return (
        f'<div style="background:#fff1e7;border:2px dashed #dcc1b6;'
        f'border-radius:16px;height:{h}px;display:flex;flex-direction:column;'
        f'align-items:center;justify-content:center;color:#55433a;'
        f'font-size:0.85rem;gap:8px;">'
        f'<span style="font-size:2.2rem;">🖼️</span>'
        f'<span style="font-weight:600;">{label}</span>'
        f'<span style="color:#897269;font-size:0.75rem;">Place in images/{label}</span>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Design system — "Warm Reassuring Sanctuary"
# Token source: stitch_divert1_online_safety_companion/warm_reassuring_sanctuary/DESIGN.md
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ───────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600;700&display=swap');

/* ── Design tokens ───────────────────────────────────────────────────────── */
:root {
    --surface:               #fff8f4;
    --surface-dim:           #f1d5bc;
    --surface-bright:        #fff8f4;
    --surface-lowest:        #ffffff;
    --surface-low:           #fff1e7;
    --surface-container:     #ffead9;
    --surface-high:          #ffe3cb;
    --surface-highest:       #fadec4;
    --on-surface:            #271909;
    --on-surface-variant:    #55433a;
    --inverse-surface:       #3e2d1c;
    --inverse-on-surface:    #ffeee0;
    --outline:               #897269;
    --outline-variant:       #dcc1b6;
    --primary:               #974311;
    --on-primary:            #ffffff;
    --primary-container:     #b65b28;
    --primary-fixed:         #ffdbcc;
    --primary-fixed-dim:     #ffb693;
    --secondary:             #266b40;
    --on-secondary:          #ffffff;
    --secondary-container:   #abf3bc;
    --on-secondary-container:#2d7145;
    --tertiary:              #8d4b00;
    --on-tertiary:           #ffffff;
    --tertiary-container:    #b15f00;
    --error:                 #ba1a1a;
    --error-container:       #ffdad6;
    --on-error-container:    #93000a;
    --surface-tint:          #9a4514;
}

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, "Segoe UI", sans-serif;
    color: #271909;
}
html, body { background-color: var(--surface) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    background-color: var(--surface) !important;
}
section[data-testid="stMain"] > div { background-color: var(--surface) !important; }

/* ── Hide Streamlit chrome ───────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar — deep coffee #3e2d1c (inverse-surface token) ─────────────── */
[data-testid="stSidebar"] {
    background: var(--inverse-surface) !important;
    border-right: 1px solid #4a3524;
}
[data-testid="stSidebar"] > div { background: var(--inverse-surface) !important; }
[data-testid="stSidebar"] * { color: var(--inverse-on-surface) !important; }
[data-testid="stSidebar"] hr { border-color: #4a3524 !important; }

/* Primary nav button */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #fff !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: var(--inverse-on-surface) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(151,67,17,0.4) !important;
}

/* ── Send & general buttons ──────────────────────────────────────────────── */
.stFormSubmitButton button {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #fff !important;
    border-radius: 50% !important;
    width: 44px !important; height: 44px !important;
    font-size: 1.1rem !important;
    padding: 0 !important;
    min-height: 44px !important;
}
.stFormSubmitButton button:hover { background: var(--primary-container) !important; }

.stButton > button {
    background: var(--surface-lowest) !important;
    border: 1.5px solid var(--outline-variant) !important;
    color: var(--on-surface) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: var(--surface-low) !important;
    border-color: var(--primary) !important;
    color: var(--primary) !important;
}

/* ── Input field ─────────────────────────────────────────────────────────── */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1.5px solid var(--outline-variant) !important;
    background: var(--surface-lowest) !important;
    padding: 11px 18px !important;
    font-size: 0.95rem !important;
    color: var(--on-surface) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input::placeholder { color: var(--outline) !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(151,67,17,0.14) !important;
    outline: none !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ── Error / info boxes ──────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 14px !important; }

/* ── Scrollbar (hide) ────────────────────────────────────────────────────── */
::-webkit-scrollbar { display: none; }

/* ══════════════════════════════════════════════════════════════════════════ */
/*  CHAT PAGE STYLES                                                          */
/* ══════════════════════════════════════════════════════════════════════════ */

/* Chat wrapper */
.chat-wrapper {
    max-width: 760px;
    margin: 0 auto;
}

/* Welcome header */
.welcome-icon {
    width: 72px; height: 72px;
    background: rgba(151,67,17,0.1);
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    ring: 2px solid rgba(151,67,17,0.2);
    margin: 0 auto 20px;
    text-align: center;
}
.welcome-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2rem; font-weight: 500;
    color: var(--on-surface);
    text-align: center; line-height: 1.25;
    margin: 0 0 10px;
    letter-spacing: -0.01em;
}
.welcome-title span { color: var(--primary); }
.welcome-sub {
    font-size: 1rem; color: var(--on-surface-variant);
    text-align: center; line-height: 1.65;
    max-width: 540px; margin: 0 auto 24px;
}

/* Prompt chips grid */
.chips-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    max-width: 600px;
    margin: 0 auto 32px;
}
.prompt-chip {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 14px 16px;
    background: var(--surface-low);
    border: 1px solid rgba(220,193,182,0.4);
    border-radius: 14px;
    cursor: pointer;
    transition: background 0.15s, border-color 0.15s;
    text-align: left;
}
.prompt-chip:hover {
    background: var(--surface-container);
    border-color: rgba(151,67,17,0.3);
}
.chip-icon {
    width: 36px; height: 36px; min-width: 36px;
    background: var(--surface-highest);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.chip-title {
    font-size: 0.875rem; font-weight: 600;
    color: var(--on-surface);
    margin: 0 0 2px;
    line-height: 1.3;
}
.chip-sub {
    font-size: 0.75rem;
    color: var(--outline);
    margin: 0;
    line-height: 1.4;
}

/* Chat stream */
.chat-stream {
    display: flex; flex-direction: column; gap: 20px;
    min-height: 300px;
    padding: 8px 0 16px;
}

/* User bubble */
.bubble-row-user {
    display: flex; justify-content: flex-end;
    gap: 12px; align-items: flex-end;
}
.bubble-user {
    background: var(--primary);
    color: #fff;
    border-radius: 20px 20px 4px 20px;
    padding: 14px 18px;
    max-width: 72%;
    font-size: 0.9375rem; line-height: 1.6;
    white-space: pre-wrap;
    box-shadow: 0 2px 8px rgba(46,31,15,0.15);
}
.user-meta {
    font-size: 0.75rem; color: var(--on-surface);
    text-align: right; margin-bottom: 5px;
    font-weight: 500;
}

/* Companion avatar */
.companion-avatar {
    width: 40px; height: 40px; min-width: 40px;
    background: var(--primary);
    color: #fff;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 2px 8px rgba(46,31,15,0.15);
    ring: 2px solid rgba(151,67,17,0.2);
    align-self: flex-start;
    margin-top: 20px;
}

/* Companion bubble row */
.bubble-row-bot { display: flex; gap: 12px; align-items: flex-start; }

/* Sanctuary card — companion response */
.sanctuary-card {
    background: var(--surface-lowest);
    border: 1px solid #e8d5bc;
    border-radius: 20px 20px 20px 4px;
    padding: 20px 22px;
    max-width: 76%;
    flex: 1;
    box-shadow: 0 2px 10px rgba(46,31,15,0.06);
}
.bot-label {
    font-size: 0.8rem; font-weight: 600;
    color: var(--primary);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 8px;
    display: block;
}
.bot-text {
    font-size: 0.9375rem; line-height: 1.65;
    color: var(--on-surface);
    white-space: pre-wrap;
}

/* Chat input bar */
.chat-input-bar {
    background: var(--surface-low);
    border-radius: 20px;
    padding: 14px 16px;
    box-shadow: 0 2px 10px rgba(46,31,15,0.07);
    margin-top: 12px;
}
.input-privacy {
    display: flex; align-items: center; gap: 7px;
    font-size: 0.75rem; color: var(--on-surface-variant);
    margin-top: 10px; padding: 0 2px;
}

/* ══════════════════════════════════════════════════════════════════════════ */
/*  ABOUT PAGE STYLES                                                          */
/* ══════════════════════════════════════════════════════════════════════════ */

/* Hero */
.hero {
    background: linear-gradient(135deg, #5c2f10 0%, #974311 60%, #c0622f 100%);
    border-radius: 22px;
    padding: 56px 48px;
    color: #fff;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 80% 50%, rgba(255,210,160,0.1) 0%, transparent 65%);
    pointer-events: none;
}
.hero-tag {
    display: inline-block;
    background: rgba(255,235,210,0.18);
    border: 1px solid rgba(255,220,180,0.4);
    color: var(--primary-fixed-dim);
    border-radius: 20px;
    padding: 5px 16px;
    font-size: 0.72rem;
    letter-spacing: .08em;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 18px;
}
.hero h1 {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.75rem; font-weight: 500;
    margin: 0 0 14px; letter-spacing: -0.01em; line-height: 1.18;
}
.hero h1 span { color: var(--primary-fixed-dim); }
.hero p { font-size: 1rem; color: #faebd8; margin: 0; max-width: 560px; line-height: 1.7; }

/* Section header */
.section-label {
    font-size: 0.69rem; letter-spacing: .12em; text-transform: uppercase;
    color: var(--primary); font-weight: 700; margin-bottom: 5px;
}
.section-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.55rem; font-weight: 500;
    color: var(--on-surface);
    margin: 0 0 22px; line-height: 1.3; letter-spacing: -0.01em;
}

/* Cards */
.card {
    background: var(--surface-lowest);
    border: 1px solid #e8d5bc;
    border-radius: 16px;
    padding: 24px 22px;
    height: 100%;
    transition: box-shadow .2s, border-color .2s;
}
.card:hover {
    box-shadow: 0 8px 24px rgba(46,31,15,0.08);
    border-color: #d9c2a3;
}
.card-icon { font-size: 1.75rem; margin-bottom: 12px; }
.card h3   { font-size: 0.9375rem; font-weight: 700; color: var(--on-surface); margin: 0 0 7px; }
.card p    { font-size: 0.85rem; color: var(--on-surface-variant); line-height: 1.65; margin: 0; }

/* Status pill */
.pill {
    display: inline-block;
    background: var(--surface-container);
    color: #7a3000;
    border: 1px solid #f0c898;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.775rem;
    font-weight: 500;
    margin: 3px 3px;
}

/* Agent flow boxes */
.agent-box {
    background: var(--surface-lowest);
    border-left: 5px solid var(--primary);
    border-radius: 0 16px 16px 0;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.agent-box h4 { font-size: 0.9375rem; font-weight: 700; color: var(--on-surface); margin: 0 0 5px; }
.agent-box p  { font-size: 0.84rem; color: var(--on-surface-variant); margin: 0; line-height: 1.6; }
.agent-box.safety  { border-color: var(--tertiary); background: #fffcf5; }
.agent-box.support { border-color: var(--secondary); background: #f4fdf6; }

/* Responsible design principles */
.principle {
    display: flex; gap: 14px; align-items: flex-start;
    margin-bottom: 16px;
}
.principle-icon {
    flex-shrink: 0; width: 38px; height: 38px;
    background: var(--surface-container);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.principle-body h4 { font-size: 0.875rem; font-weight: 700; color: var(--on-surface); margin: 0 0 2px; }
.principle-body p  { font-size: 0.82rem; color: var(--on-surface-variant); margin: 0; line-height: 1.55; }

/* Stat blocks */
.stat-block {
    background: var(--inverse-surface);
    border-radius: 16px;
    padding: 26px 20px;
    text-align: center; color: #fff;
}
.stat-block .num {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.4rem; font-weight: 500;
    color: var(--primary-fixed-dim);
}
.stat-block .lbl { font-size: 0.78rem; color: #d4b89a; margin-top: 5px; line-height: 1.45; }

/* MVP list */
.limit-item {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 12px; font-size: 0.875rem;
    color: var(--on-surface); line-height: 1.6;
}
.limit-dot {
    flex-shrink: 0; margin-top: 7px;
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--tertiary);
}

/* Footer */
.site-footer {
    text-align: center; color: var(--outline);
    font-size: 0.775rem; padding: 32px 0 10px;
    border-top: 1px solid #e8d5bc; margin-top: 56px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
WELCOME = (
    "Hi! I'm your Online Safety Companion.\n\n"
    "I help you check people, messages, and requests online. "
    "You decide what to do — I only give information and options.\n\n"
    "What would you like help with today?"
)

for key, default in [
    ("page",           "chat"),
    ("ready",          False),
    ("thread_id",      None),
    ("messages",       []),
    ("run_client",     None),
    ("threads_client", None),
    ("agent_id",       None),
    ("init_error",     None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — dark coffee rail
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 28px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:36px;height:36px;background:#974311;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:1.3rem;">
                🛡️
            </div>
            <div>
                <div style="font-family:'Newsreader',Georgia,serif;font-size:1.25rem;
                            font-weight:500;color:#ffeee0;line-height:1.1;letter-spacing:-0.01em;">
                    DIVERT<span style="color:#ffb693;">1</span>
                </div>
                <div style="font-size:0.7rem;color:#897269;margin-top:2px;letter-spacing:.02em;">
                    Online Safety Companion
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("💬  Chat", use_container_width=True,
                 type="primary" if st.session_state.page == "chat" else "secondary"):
        st.session_state.page = "chat"
        st.rerun()

    if st.button("ℹ️  About DIVERT1", use_container_width=True,
                 type="primary" if st.session_state.page == "about" else "secondary"):
        st.session_state.page = "about"
        st.rerun()

    st.markdown("<hr style='border-color:#4a3524;margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.75rem;color:#897269;line-height:1.75;padding:0 2px;">
        <span style="color:#dcc1b6;font-weight:600;">Powered by</span><br>
        IBM watsonx Orchestrate<br><br>
        <span style="color:#dcc1b6;font-weight:600;">Built for</span><br>
        Neurodivergent young adults<br>
        navigating life online.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# One-time SDK initialisation
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.ready and st.session_state.init_error is None:
    with st.spinner("Connecting to IBM watsonx Orchestrate…"):
        try:
            load_env()
            activate_env()
            rc, tc, aid = build_clients()
            st.session_state.run_client     = rc
            st.session_state.threads_client = tc
            st.session_state.agent_id       = aid
            st.session_state.ready          = True
        except SystemExit as e:
            st.session_state.init_error = str(e)
        except Exception as e:
            st.session_state.init_error = str(e)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "chat":

    if st.session_state.init_error:
        st.error(f"Could not connect to the agent:\n\n{st.session_state.init_error}")
        st.stop()

    # Page header
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;
                border-bottom:1px solid rgba(220,193,182,0.35);
                padding-bottom:14px;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-family:'Newsreader',Georgia,serif;font-size:1.1rem;
                         font-weight:600;color:#271909;letter-spacing:-0.01em;">
                Online Safety Companion
            </span>
            <span style="padding:3px 10px;border-radius:20px;
                         background:rgba(151,67,17,0.1);color:#974311;
                         font-size:0.7rem;font-weight:600;">Active Session</span>
        </div>
        <div style="font-size:0.75rem;color:#897269;">
            DIVERT1 · IBM watsonx Orchestrate
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Welcome screen (shown when no messages yet) ───────────────────────────
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-wrapper" style="text-align:center;padding:32px 0 16px;">
            <div style="width:72px;height:72px;background:rgba(151,67,17,0.1);
                        border-radius:20px;display:flex;align-items:center;
                        justify-content:center;font-size:2.2rem;margin:0 auto 20px;
                        outline:2px solid rgba(151,67,17,0.18);">🛡️</div>
            <h1 class="welcome-title">
                Hi! I'm your Online Safety Companion.<br>
                <span>How can I help you today?</span>
            </h1>
            <p class="welcome-sub">
                I help you check people, messages, and requests online.
                You decide what to do — I only give information and options.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Prompt chips
        CHIPS = [
            ("📧", "Check a suspicious message or DM",   "Screenshots, links, or awkward chats"),
            ("👤", "Check a person I met online",         "New friends, gaming contacts, dates"),
            ("💸", "Someone asked me for money",          "Gift cards, crypto, urgent requests"),
            ("😟", "I think I was already scammed",       "What to do next and who to tell"),
        ]

        col_left, col_right = st.columns(2, gap="small")
        chip_cols = [col_left, col_left, col_right, col_right]

        clicked_chip = None
        for (icon, title, sub), col in zip(CHIPS, chip_cols):
            with col:
                if st.button(
                    f"{icon}  **{title}**\n\n{sub}",
                    use_container_width=True,
                    key=f"chip_{title}",
                ):
                    clicked_chip = title

        if clicked_chip:
            st.session_state.messages.append({"role": "user", "text": clicked_chip})
            with st.spinner("Thinking…"):
                try:
                    reply, new_tid = send_message(
                        st.session_state.run_client,
                        st.session_state.threads_client,
                        clicked_chip,
                        st.session_state.agent_id,
                        st.session_state.thread_id,
                    )
                    st.session_state.thread_id = new_tid
                    st.session_state.messages.append({"role": "assistant", "text": reply})
                except Exception as e:
                    st.session_state.messages.append(
                        {"role": "assistant", "text": f"Something went wrong: {e}"}
                    )
            st.rerun()

    # ── Chat stream (shown once messages exist) ───────────────────────────────
    else:
        st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="chat-stream">', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="bubble-row-user">'
                    f'<div>'
                    f'<div class="user-meta">You</div>'
                    f'<div class="bubble-user">{msg["text"]}</div>'
                    f'</div>'
                    f'<div style="width:40px;height:40px;min-width:40px;'
                    f'background:var(--surface-highest);border-radius:50%;'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-size:1.1rem;margin-top:20px;ring:2px solid rgba(151,67,17,0.2);">👤</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="bubble-row-bot">'
                    f'<div class="companion-avatar">🛡️</div>'
                    f'<div>'
                    f'<div class="bot-label">DIVERT1 Companion</div>'
                    f'<div class="sanctuary-card">'
                    f'<div class="bot-text">{msg["text"]}</div>'
                    f'</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)  # close chat-stream
        st.markdown('</div>', unsafe_allow_html=True)  # close chat-wrapper

    # ── Input bar ─────────────────────────────────────────────────────────────
    st.markdown('<div style="max-width:760px;margin:0 auto;">', unsafe_allow_html=True)
    st.markdown('<div class="chat-input-bar">', unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([9, 1])
        user_input = cols[0].text_input(
            label="msg",
            placeholder="Paste a message or describe a situation…",
            label_visibility="collapsed",
        )
        submitted = cols[1].form_submit_button("➤")

    st.markdown("""
    <div class="input-privacy">
        🔒 &nbsp;DIVERT1 evaluates context respectfully.
        We never ask for passwords or private data.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close chat-input-bar

    # New conversation button
    _, right_col = st.columns([3, 1])
    with right_col:
        if st.button("🔄 New conversation", use_container_width=True):
            st.session_state.thread_id = None
            st.session_state.messages  = []
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # close max-width wrapper

    if submitted and user_input.strip():
        text = user_input.strip()
        st.session_state.messages.append({"role": "user", "text": text})
        with st.spinner("Thinking…"):
            try:
                reply, new_tid = send_message(
                    st.session_state.run_client,
                    st.session_state.threads_client,
                    text,
                    st.session_state.agent_id,
                    st.session_state.thread_id,
                )
                st.session_state.thread_id = new_tid
                st.session_state.messages.append({"role": "assistant", "text": reply})
            except Exception as e:
                st.session_state.messages.append(
                    {"role": "assistant", "text": f"Something went wrong: {e}"}
                )
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
        <div class="hero-tag">Project DIVERT1</div>
        <h1>Online Safety<br><span>Companion</span></h1>
        <p>
            A multi-agent AI that explains online risks in plain, calm language —
            designed from the ground up for neurodivergent young adults
            navigating scams, fraud, and social pressure online.
        </p>
    </div>
    """, unsafe_allow_html=True)

    hero_img = img("hero_banner.png")
    if hero_img:
        st.image(hero_img, use_container_width=True)
    else:
        st.markdown(placeholder("hero_banner.png", 280), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STATS ─────────────────────────────────────────────────────────────────
    for col, num, lbl in zip(
        st.columns(4),
        ["3×", "3", "100%", "0"],
        ["more likely to be targeted\nby online scams",
         "AI agents working\ntogether in real time",
         "rule-based risk scoring\n— fully auditable",
         "passwords, card numbers\nor IDs ever asked"],
    ):
        col.markdown(
            f'<div class="stat-block"><div class="num">{num}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── THE PROBLEM ───────────────────────────────────────────────────────────
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown("""
        <div class="section-label">The Problem</div>
        <div class="section-title">Why existing tools<br>aren't enough</div>
        """, unsafe_allow_html=True)
        p_img = img("problem_illustration.png")
        if p_img:
            st.image(p_img, use_container_width=True)
        else:
            st.markdown(placeholder("problem_illustration.png", 240), unsafe_allow_html=True)

    with right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        for icon, title, body in [
            ("🎯", "Higher targeting risk",
             "Neurodivergent people are statistically more likely to be targeted by scams, "
             "fraud, and manipulation online."),
            ("🚫", "Tools only block — they don't explain",
             "Spam filters, browser warnings, and block buttons rarely say why something "
             "is risky or help the user decide what to do."),
            ("📖", "Safety lessons are hard to follow",
             "Most online safety content is not written for how neurodivergent people "
             "process information — full of metaphors, sarcasm, and assumed social cues."),
        ]:
            st.markdown(
                f'<div class="card" style="margin-bottom:12px;">'
                f'<div class="card-icon">{icon}</div>'
                f'<h3>{title}</h3><p>{body}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── WHO IT IS FOR ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Who it's for</div>
    <div class="section-title">Our Users</div>
    """, unsafe_allow_html=True)

    u1, u2, u3 = st.columns(3, gap="medium")
    for col, fname, icon, title, body in [
        (u1, "user_persona.png", "🧠", "Neurodivergent Young Adults",
         "Autistic people and people with ADHD who are starting to live more "
         "independently. Thoughtful, honest, and most comfortable communicating online."),
        (u2, "risk_scenario.png", "⚠️", "New to Adult Risks",
         "They may be new to risks like money requests, romance scams, and "
         '"prove you trust me" pressure from people they met online.'),
        (u3, "support_network.png", "👥", "Support Network Often Absent",
         "Parents, campus advisors, and support workers are rarely present in the "
         "moment when these situations unfold online."),
    ]:
        u_img = img(fname)
        with col:
            if u_img:
                st.image(u_img, use_container_width=True)
            else:
                st.markdown(placeholder(fname, 190), unsafe_allow_html=True)
            st.markdown(
                f'<div class="card" style="margin-top:10px;">'
                f'<div class="card-icon">{icon}</div>'
                f'<h3>{title}</h3><p>{body}</p></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── OUR SOLUTION ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Our Solution</div>
    <div class="section-title">How the multi-agent system works</div>
    """, unsafe_allow_html=True)

    sol_l, sol_r = st.columns([1, 1], gap="large")
    with sol_l:
        a_img = img("agent_architecture.png")
        if a_img:
            st.image(a_img, use_container_width=True)
        else:
            st.markdown(placeholder("agent_architecture.png", 320), unsafe_allow_html=True)
    with sol_r:
        st.markdown("""
        <div class="agent-box">
            <h4>🤖 Main Chatbot Agent</h4>
            <p>Welcomes the user, asks one short question at a time, and gathers
            the messages and background needed for analysis.</p>
        </div>
        <div class="agent-box safety">
            <h4>🔍 Safety Agent</h4>
            <p>Checks content with a transparent, rule-based risk-scoring tool.
            Returns a risk level (low / medium / high), exact words of concern,
            how the conversation changed over time, and one follow-up question.</p>
        </div>
        <div class="agent-box support">
            <h4>🤝 Support Agent</h4>
            <p>Turns the risk result into a short, calm reply with 2–3 clear options.
            When risk is high or the user was already scammed, it strongly recommends
            a trusted person and provides practical next steps.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── DIFFERENTIATORS ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Differentiators</div>
    <div class="section-title">What makes DIVERT1 different</div>
    """, unsafe_allow_html=True)

    for col, icon, title, body in zip(
        st.columns(4, gap="medium"),
        ["🔎", "💬", "🫂", "✅"],
        ["Whole-conversation analysis", "Explains the why",
         "Respects friendships", "Avoids over-warning"],
        ["Looks at behaviour patterns across the entire conversation, not just single keywords.",
         "Gives reasons instead of only warnings — so users can learn and decide.",
         "A long-time friend who asks for money gets a careful check, not an accusation.",
         "Recognises normal, safe conversations and does not flag them unnecessarily."],
    ):
        col.markdown(
            f'<div class="card"><div class="card-icon">{icon}</div>'
            f'<h3>{title}</h3><p>{body}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── RESPONSIBLE DESIGN ────────────────────────────────────────────────────
    rd_l, rd_r = st.columns([1, 1], gap="large")
    with rd_l:
        st.markdown("""
        <div class="section-label">Responsible Design</div>
        <div class="section-title">Built with care<br>at every step</div>
        """, unsafe_allow_html=True)
        for icon, title, body in [
            ("🚫", "Never labels anyone a scammer",
             "The companion never claims someone is definitely a scammer — it only shares what raised concern."),
            ("🙋", "User always decides",
             "The system never makes decisions for the user. It gives information and options — nothing more."),
            ("🔒", "No sensitive data, ever",
             "It never asks for passwords, card numbers, or ID."),
            ("📋", "Fully auditable",
             "Risk scoring is rule-based, so every decision can be traced and checked."),
            ("📝", "Clear, literal language",
             "Replies use short sentences with no sarcasm, idioms, or hidden meaning."),
        ]:
            st.markdown(
                f'<div class="principle">'
                f'<div class="principle-icon">{icon}</div>'
                f'<div class="principle-body"><h4>{title}</h4><p>{body}</p></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    with rd_r:
        d_img = img("responsible_design.png")
        if d_img:
            st.image(d_img, use_container_width=True)
        else:
            st.markdown(placeholder("responsible_design.png", 400), unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── MVP SCOPE ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">MVP Scope &amp; Limits</div>
    <div class="section-title">What the current version does</div>
    """, unsafe_allow_html=True)

    mv1, mv2 = st.columns(2, gap="large")
    with mv1:
        st.markdown(
            "<b style='color:#266b40;font-size:0.875rem;'>✔ Included in MVP</b>",
            unsafe_allow_html=True,
        )
        for item in ["Checks pasted messages and explains risk",
                     "Supports users who have already been scammed",
                     "Recommends trusted people to contact",
                     "AI agent reviews every rule-based result"]:
            st.markdown(
                f'<div class="limit-item">'
                f'<div class="limit-dot" style="background:#266b40;"></div>'
                f'{item}</div>',
                unsafe_allow_html=True,
            )
    with mv2:
        st.markdown(
            "<b style='color:#8d4b00;font-size:0.875rem;'>⚠ Not in MVP</b>",
            unsafe_allow_html=True,
        )
        for item in ["Real-time chat monitoring",
                     "Direct connection to social platforms",
                     "Detection of very subtle or novel wording"]:
            st.markdown(
                f'<div class="limit-item"><div class="limit-dot"></div>{item}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── TECH STACK ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">Technology</div>
    <div class="section-title">Built on IBM watsonx Orchestrate</div>
    """, unsafe_allow_html=True)

    t_img = img("tech_stack.png")
    if t_img:
        st.image(t_img, use_container_width=True)
    else:
        st.markdown(placeholder("tech_stack.png", 180), unsafe_allow_html=True)

    pills = ["IBM watsonx Orchestrate", "Multi-agent orchestration",
             "Rule-based risk scoring", "Python", "Streamlit",
             "Transparent AI", "Neurodivergent-inclusive design"]
    st.markdown(
        '<div style="margin-top:16px;">'
        + "".join(f'<span class="pill">{p}</span>' for p in pills)
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── TEAM ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-label">The Team</div>
    <div class="section-title">People behind DIVERT1</div>
    """, unsafe_allow_html=True)

    t1, t2, t3 = st.columns(3, gap="medium")
    for col, fname, name, role in [
        (t1, "team_member_1.png", "Team Member", "Role · Organisation"),
        (t2, "team_member_2.png", "Team Member", "Role · Organisation"),
        (t3, "team_member_3.png", "Team Member", "Role · Organisation"),
    ]:
        tm_img = img(fname)
        with col:
            if tm_img:
                st.image(tm_img, use_container_width=True)
            else:
                st.markdown(placeholder(fname, 160), unsafe_allow_html=True)
            st.markdown(
                f'<div style="text-align:center;margin-top:10px;">'
                f'<b style="color:var(--on-surface);font-size:0.9375rem;">{name}</b><br>'
                f'<span style="font-size:0.8rem;color:var(--on-surface-variant);">{role}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="site-footer">
        DIVERT1 &nbsp;·&nbsp; Online Safety Companion &nbsp;·&nbsp;
        Powered by IBM watsonx Orchestrate<br>
        Built with care for neurodivergent young adults navigating life online.
    </div>
    """, unsafe_allow_html=True)
