"""
app.py — DIVERT1 | Online Safety Companion
===========================================
Streamlit frontend — design 100% from stitch_divert1_online_safety_companion.
  • Chat  — divert1_safety_companion_chat_wcag_2.1_accessible/code.html
  • About — divert1_about_architecture/code.html

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
    """Warm placeholder matching surface-container-low background."""
    return (
        f'<div style="background:#fff1e7;border:2px dashed #dcc1b6;'
        f'border-radius:12px;height:{h}px;display:flex;flex-direction:column;'
        f'align-items:center;justify-content:center;color:#55433a;'
        f'font-family:Inter,sans-serif;font-size:0.85rem;gap:8px;">'
        f'<span style="font-size:2rem;">🖼️</span>'
        f'<span style="font-weight:600;">{label}</span>'
        f'<span style="color:#897269;font-size:0.75rem;">Place in images/{label}</span>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Design system — copied verbatim from stitch HTML tailwind-config tokens
#
# Colour tokens (tailwind → CSS var):
#   background / surface:          #fff8f4
#   surface-container-lowest:      #ffffff
#   surface-container-low:         #fff1e7
#   surface-container:             #ffead9
#   surface-container-high:        #ffe3cb
#   surface-container-highest:     #fadec4
#   surface-dim:                   #f1d5bc
#   surface-variant:               #fadec4
#   on-surface:                    #271909
#   on-surface-variant:            #55433a
#   inverse-surface:               #3e2d1c
#   inverse-on-surface:            #ffeee0
#   outline:                       #897269
#   outline-variant:               #dcc1b6
#   primary:                       #974311
#   on-primary:                    #ffffff
#   primary-container:             #b65b28
#   primary-fixed:                 #ffdbcc
#   primary-fixed-dim:             #ffb693
#   on-primary-fixed:              #351000
#   on-primary-fixed-variant:      #7a3000
#   secondary:                     #266b40
#   on-secondary:                  #ffffff
#   secondary-container:           #abf3bc
#   secondary-fixed:               #abf3bc
#   secondary-fixed-dim:           #90d6a2
#   on-secondary-fixed:            #00210d
#   on-secondary-container:        #2d7145
#   tertiary:                      #8d4b00
#   on-tertiary:                   #ffffff
#   tertiary-container:            #b15f00
#   tertiary-fixed:                #ffdcc3
#   tertiary-fixed-dim:            #ffb77d
#   on-tertiary-fixed:             #2f1500
#   error:                         #ba1a1a
#   on-error:                      #ffffff
#   error-container:               #ffdad6
#   on-error-container:            #93000a
#
# Typography (stitch):
#   display:   Newsreader 500  40px/48px  -0.01em
#   headline-lg: Newsreader 500  32px/40px
#   headline-sm: Newsreader 600  20px/28px
#   body-lg:   Inter 400  18px/28px
#   body-md:   Inter 400  16px/24px
#   body-sm:   Inter 400  14px/20px
#   label-lg:  Inter 600  15px/20px  0.01em
#   label-md:  Inter 600  13px/18px  0.02em
#   label-sm:  Inter 600  11px/16px  0.04em
#
# Border-radius: DEFAULT 0.25rem, lg 0.5rem, xl 0.75rem, full 9999px
# (stitch uses rounded-xl = 0.75rem, rounded-2xl = 1rem, rounded-[20px] etc.)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── from stitch <link> tags ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600;700&display=swap');

/* ── Colour tokens (from tailwind-config in stitch HTML) ─────────────────── */
:root {
    --surface:                  #fff8f4;
    --surface-lowest:           #ffffff;
    --surface-low:              #fff1e7;
    --surface-container:        #ffead9;
    --surface-high:             #ffe3cb;
    --surface-highest:          #fadec4;
    --surface-dim:              #f1d5bc;
    --surface-variant:          #fadec4;
    --on-surface:               #271909;
    --on-surface-variant:       #55433a;
    --inverse-surface:          #3e2d1c;
    --inverse-on-surface:       #ffeee0;
    --outline:                  #897269;
    --outline-variant:          #dcc1b6;
    --primary:                  #974311;
    --on-primary:               #ffffff;
    --primary-container:        #b65b28;
    --primary-fixed:            #ffdbcc;
    --primary-fixed-dim:        #ffb693;
    --on-primary-fixed:         #351000;
    --secondary:                #266b40;
    --on-secondary:             #ffffff;
    --secondary-container:      #abf3bc;
    --secondary-fixed:          #abf3bc;
    --secondary-fixed-dim:      #90d6a2;
    --on-secondary-fixed:       #00210d;
    --on-secondary-container:   #2d7145;
    --tertiary:                 #8d4b00;
    --on-tertiary:              #ffffff;
    --tertiary-fixed:           #ffdcc3;
    --tertiary-fixed-dim:       #ffb77d;
    --on-tertiary-fixed:        #2f1500;
    --error:                    #ba1a1a;
    --on-error:                 #ffffff;
    --error-container:          #ffdad6;
    --on-error-container:       #93000a;
}

/* ── Base ────────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, "Segoe UI", sans-serif !important;
    color: var(--on-surface);
}
html, body { background-color: var(--surface) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main .block-container {
    background-color: var(--surface) !important;
    padding-top: 0 !important;
}
section[data-testid="stMain"] > div { background-color: var(--surface) !important; }
div.block-container { padding-top: 1rem !important; }

/* ── Hide Streamlit chrome ─────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
::-webkit-scrollbar { display: none; }

/* ══ SIDEBAR — inverse-surface #3e2d1c (from stitch aside bg-inverse-surface) */
[data-testid="stSidebar"] {
    background: var(--inverse-surface) !important;
    border-right: none;
    box-shadow: 4px 0 24px rgba(46,31,15,0.12);
}
[data-testid="stSidebar"] > div { background: var(--inverse-surface) !important; }
[data-testid="stSidebar"] * { color: var(--inverse-on-surface) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

/* Sidebar — primary button (bg-primary text-on-primary, stitch "New Chat" btn) */
[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: var(--primary) !important;
    border: none !important;
    color: var(--on-primary) !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8125rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 1px 4px rgba(46,31,15,0.15) !important;
}
[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
    background: var(--primary-container) !important;
}
/* Sidebar — secondary/ghost nav buttons */
[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: transparent !important;
    border: none !important;
    color: var(--outline-variant) !important;
    border-radius: 8px !important;
    min-height: 44px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8125rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
    background: rgba(250,222,196,0.12) !important;
    color: var(--surface) !important;
}
/* Focus ring (WCAG) on sidebar buttons — ring-[#ffdbcc] */
[data-testid="stSidebar"] .stButton button:focus-visible {
    outline: 2px solid #ffdbcc !important;
    outline-offset: 2px !important;
}

/* ══ MAIN AREA BUTTONS ─────────────────────────────────────────────────── */
/* General secondary buttons */
.stButton > button {
    background: var(--surface-lowest) !important;
    border: 1.5px solid var(--outline-variant) !important;
    color: var(--on-surface) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8125rem !important;
    min-height: 44px !important;
}
.stButton > button:hover {
    background: var(--surface-low) !important;
    border-color: rgba(151,67,17,0.4) !important;
    color: var(--primary) !important;
}
/* Send button — rounded-xl bg-primary (stitch companionSendBtn) */
.stFormSubmitButton button {
    background: var(--primary) !important;
    border: none !important;
    color: var(--on-primary) !important;
    border-radius: 12px !important;
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    font-size: 1.1rem !important;
    padding: 0 !important;
    box-shadow: 0 1px 4px rgba(46,31,15,0.15) !important;
}
.stFormSubmitButton button:hover { background: var(--primary-container) !important; }

/* ══ TEXT INPUT — from stitch input field ──────────────────────────────── */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid var(--outline-variant) !important;
    background: var(--surface-lowest) !important;
    padding: 10px 16px !important;
    font-size: 0.9375rem !important;
    color: var(--on-surface) !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 44px !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--outline) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px rgba(151,67,17,0.2) !important;
    outline: none !important;
}

/* ══ SPINNER ───────────────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--primary) !important; }

/* ══ ALERT ─────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 12px !important; }

/* ══════════════════════════════════════════════════════════════════════════
   CHAT PAGE  —  divert1_safety_companion_chat_wcag_2.1_accessible/code.html
   ════════════════════════════════════════════════════════════════════════ */

/* Outer constraint — max-w-4xl from stitch main workspace */
.chat-workspace {
    max-width: 56rem;   /* 896px ~ max-w-4xl */
    margin: 0 auto;
    padding: 0 1.5rem;
}

/* Conversation context header — border-b border-outline-variant/30 */
.chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(220,193,182,0.3);
    margin-bottom: 24px;
}
.chat-header-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--on-surface);
    margin: 0;
    letter-spacing: -0.01em;
}
.session-badge {
    padding: 2px 10px;
    border-radius: 9999px;
    background: rgba(151,67,17,0.1);
    color: var(--primary);
    font-size: 0.6875rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.04em;
}

/* Welcome splash — from divert1_safety_companion_chat/code.html centre block */
.welcome-block {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 24px;
    padding: 32px 0 8px;
}
.welcome-icon-wrap {
    width: 64px; height: 64px;
    border-radius: 16px;    /* rounded-2xl */
    background: rgba(151,67,17,0.1);
    display: flex; align-items: center; justify-content: center;
    outline: 2px solid rgba(151,67,17,0.2);
    font-size: 2rem;
}
.welcome-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2rem;
    font-weight: 500;
    color: var(--on-surface);
    line-height: 1.25;
    letter-spacing: -0.01em;
    max-width: 32rem;
    margin: 0;
}
.welcome-title .accent { color: var(--primary); }
.welcome-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: var(--on-surface-variant);
    line-height: 1.65;
    max-width: 34rem;
    margin: 0;
}

/* Prompt chip — stitch: rounded-xl bg-surface-container-low border-outline-variant/30 */
/* Streamlit buttons are used; we style .stButton inside col to look like chips */
.chip-col .stButton > button {
    background: var(--surface-low) !important;
    border: 1px solid rgba(220,193,182,0.35) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    min-height: 72px !important;
    color: var(--on-surface) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 400 !important;
    line-height: 1.5 !important;
    box-shadow: 0 1px 4px rgba(46,31,15,0.04) !important;
    white-space: pre-wrap !important;
}
.chip-col .stButton > button:hover {
    background: var(--surface-container) !important;
    border-color: rgba(151,67,17,0.3) !important;
    color: var(--on-surface) !important;
}

/* Dialogue log — role="log" aria-live="polite" */
.dialogue-log {
    display: flex;
    flex-direction: column;
    gap: 24px;
    padding: 8px 0 20px;
}

/* ── User message ── stitch: rounded-[20px] rounded-br-sm bg #c0622f ────── */
.msg-user-row {
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    gap: 14px;
    padding-left: 4rem;
}
.msg-user-inner {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
    max-width: 32rem;
}
.msg-user-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 4px;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--on-surface);
}
.msg-user-bubble {
    padding: 20px;
    border-radius: 20px;
    border-bottom-right-radius: 4px;
    background: #c0622f;   /* exact stitch value: rgb(192,98,47) */
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 0.9375rem;
    line-height: 1.65;
    white-space: pre-wrap;
    box-shadow: 0 2px 8px rgba(46,31,15,0.15);
}
.msg-user-avatar {
    width: 40px; height: 40px; min-width: 40px;
    border-radius: 9999px;
    background: var(--surface-highest);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    margin-top: 24px;
    outline: 2px solid rgba(151,67,17,0.2);
}

/* ── Companion message ── stitch: rounded-[20px] rounded-tl-sm ─────────── */
.msg-bot-row {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding-right: 1rem;
}
/* Companion avatar — rounded-xl bg-primary (stitch: health_and_safety icon) */
.companion-avatar {
    width: 40px; height: 40px; min-width: 40px;
    border-radius: 12px;   /* rounded-xl */
    background: var(--primary);
    color: var(--on-primary);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.25rem;
    margin-top: 24px;
    box-shadow: 0 1px 4px rgba(46,31,15,0.15);
    outline: 2px solid rgba(151,67,17,0.2);
    flex-shrink: 0;
}
.msg-bot-inner {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    max-width: 32rem;
}
.msg-bot-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--primary);
    padding: 0 4px;
}
/* Sanctuary card — exact stitch: #fff9f2 bg, #e8d5bc border, rounded-[20px] rounded-tl-sm */
.sanctuary-card {
    background: #fff9f2;
    border: 1px solid #e8d5bc;
    border-radius: 20px;
    border-top-left-radius: 4px;
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    box-shadow: 0 2px 8px rgba(46,31,15,0.07);
    font-family: 'Inter', sans-serif;
    font-size: 0.9375rem;
    line-height: 1.65;
    color: var(--on-surface);
    white-space: pre-wrap;
}

/* ── Input bar ── stitch: rounded-2xl bg-surface-container-low p-4 ──────── */
.input-bar-wrap {
    background: var(--surface-low);    /* bg-surface-container-low */
    border-radius: 16px;               /* rounded-2xl */
    padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(46,31,15,0.07);
    margin-top: 16px;
}
.input-privacy-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    color: var(--on-surface-variant);
    padding: 8px 2px 0;
    letter-spacing: 0.02em;
}

/* ══════════════════════════════════════════════════════════════════════════
   ABOUT PAGE  —  divert1_about_architecture/code.html
   ════════════════════════════════════════════════════════════════════════ */

/* Breadcrumb bar — bg-surface-container-low border-b border-outline/30 */
.breadcrumb-bar {
    width: 100%;
    background: var(--surface-low);
    border-bottom: 1px solid rgba(137,114,105,0.3);
    padding: 10px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'Inter', sans-serif;
    font-size: 0.8125rem;
    color: var(--on-surface-variant);
    margin-bottom: 0;
}
.breadcrumb-bar .crumb-active {
    font-weight: 600;
    color: var(--on-surface);
}
.breadcrumb-ver {
    padding: 2px 10px;
    border-radius: 9999px;
    background: var(--surface-high);
    color: var(--on-surface-variant);
    font-size: 0.6875rem;
    font-weight: 600;
}

/* Hero — bg-gradient from-inverse-surface via-primary to-primary-container */
.about-hero {
    width: 100%;
    background: linear-gradient(135deg, #3e2d1c 0%, #974311 55%, #b65b28 100%);
    color: var(--inverse-on-surface);
    padding: 56px 64px;
    position: relative;
    overflow: hidden;
}
.about-hero::before {
    content: '';
    position: absolute;
    right: -6rem; top: -6rem;
    width: 24rem; height: 24rem;
    border-radius: 9999px;
    background: rgba(171,243,188,0.1);   /* secondary-container/15 */
    filter: blur(48px);
    pointer-events: none;
}
.about-hero::after {
    content: '';
    position: absolute;
    left: 33%; bottom: -5rem;
    width: 20rem; height: 20rem;
    border-radius: 9999px;
    background: rgba(255,220,195,0.14);   /* tertiary-fixed/20 */
    filter: blur(48px);
    pointer-events: none;
}
.about-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    background: rgba(255,255,255,0.1);
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--primary-fixed);
    margin-bottom: 20px;
}
.about-hero-badge .pulse {
    width: 8px; height: 8px;
    border-radius: 9999px;
    background: var(--secondary-fixed-dim);
}
.about-hero h1 {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.75rem;
    font-weight: 400;
    line-height: 1.18;
    letter-spacing: -0.01em;
    margin: 0 0 16px;
    max-width: 48rem;
}
.about-hero h1 .italic-accent {
    font-style: italic;
    color: var(--tertiary-fixed);
    text-decoration: underline wavy rgba(255,220,195,0.4);
    text-underline-offset: 8px;
}
.about-hero h1 .alpha-badge {
    display: inline-block;
    padding: 2px 8px;
    margin-left: 10px;
    border-radius: 6px;
    background: var(--secondary-container);
    color: var(--on-secondary-fixed);
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    vertical-align: middle;
    font-style: normal;
    text-decoration: none;
}
.about-hero p {
    font-family: 'Inter', sans-serif;
    font-size: 1.125rem;
    font-weight: 300;
    color: var(--surface-high);
    line-height: 1.65;
    max-width: 40rem;
    margin: 0 0 20px;
}
.hero-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 9999px;
    background: rgba(255,255,255,0.08);
    font-family: 'Inter', sans-serif;
    font-size: 0.8125rem;
    color: var(--inverse-on-surface);
    font-weight: 500;
}

/* Stat grid — bg-inverse-surface rounded-xl */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: -24px;
    position: relative;
    z-index: 10;
    padding: 0;
}
.stat-card {
    background: var(--inverse-surface);
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 110px;
    overflow: hidden;
    position: relative;
}
.stat-num {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.75rem;
    font-weight: 400;
    line-height: 1;
    margin-bottom: 10px;
}
.stat-num.tertiary-fixed { color: var(--tertiary-fixed-dim); }
.stat-num.primary-fixed  { color: var(--primary-fixed-dim); }
.stat-num.secondary-fixed{ color: var(--secondary-fixed-dim); }
.stat-num.surface        { color: var(--inverse-on-surface); }
.stat-lbl {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--surface-high);
    line-height: 1.4;
}

/* Section headers — from stitch section labels */
.section-eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.section-eyebrow.primary  { color: var(--primary); }
.section-eyebrow.secondary{ color: var(--secondary); }
.section-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2rem;
    font-weight: 500;
    color: var(--on-surface);
    letter-spacing: -0.01em;
    line-height: 1.25;
    margin: 0 0 10px;
}
.section-body {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: var(--on-surface-variant);
    line-height: 1.65;
    max-width: 40rem;
}

/* Problem infographic card — surface-container-low rounded-xl */
.problem-infographic {
    background: var(--surface-low);
    border-radius: 12px;
    padding: 28px;
}

/* Problem / Differentiator cards — surface-container-lowest rounded-xl */
.about-card {
    background: var(--surface-lowest);
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    box-shadow: 0 1px 4px rgba(46,31,15,0.04);
    transition: box-shadow 0.2s;
    height: 100%;
}
.about-card:hover { box-shadow: 0 4px 12px rgba(46,31,15,0.08); }
.about-card-icon-wrap {
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 1.5rem;
}
.about-card-icon-wrap.primary   { background: rgba(151,67,17,0.1); }
.about-card-icon-wrap.tertiary  { background: rgba(141,75,0,0.12); }
.about-card-icon-wrap.secondary { background: rgba(38,107,64,0.12); }
.about-card h4 {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--on-surface);
    margin: 0;
    line-height: 1.3;
}
.about-card p {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: var(--on-surface-variant);
    line-height: 1.65;
    margin: 0;
}

/* User cohort section — bg-surface-container-low full-width */
.cohort-section {
    background: var(--surface-low);
    padding: 64px 0;
    margin-left: -2rem;
    margin-right: -2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
/* Cohort card bottom tag */
.cohort-tag {
    margin-top: 20px;
    padding: 10px 12px;
    background: rgba(255,227,203,0.4);  /* surface-container-high/40 */
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
}
.cohort-tag.primary  { color: var(--primary); }
.cohort-tag.tertiary { color: var(--tertiary); }
.cohort-tag.secondary{ color: var(--secondary); }

/* Agent architecture cards — bg-surface rounded-xl (inside surface-lowest container) */
.agent-arch-wrap {
    background: var(--surface-lowest);
    border-radius: 16px;
    padding: 32px 40px;
    box-shadow: 0 1px 4px rgba(46,31,15,0.04);
}
.agent-card {
    background: var(--surface);
    border-radius: 12px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    height: 100%;
}
.agent-num-badge {
    width: 32px; height: 32px;
    border-radius: 9999px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--on-primary);
}
.agent-num-badge.primary   { background: var(--primary); }
.agent-num-badge.tertiary  { background: var(--tertiary); color: var(--on-tertiary); }
.agent-num-badge.secondary { background: var(--secondary); color: var(--on-secondary); }
.agent-type-badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
}
.agent-type-badge.primary   { background: var(--primary-fixed); color: var(--on-primary-fixed); }
.agent-type-badge.tertiary  { background: var(--tertiary-fixed); color: var(--on-tertiary-fixed); }
.agent-type-badge.secondary { background: var(--secondary-fixed); color: var(--on-secondary-fixed); }
.agent-card h3 {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--on-surface);
    margin: 0;
}
.agent-card p {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--on-surface-variant);
    line-height: 1.65;
    margin: 0;
}
.agent-card-note {
    margin-top: 4px;
    background: var(--surface-low);
    border-radius: 8px;
    padding: 10px 12px;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--on-surface-variant);
}
.agent-card-note strong { color: var(--on-surface); }
/* Auditable handshake bar */
.arch-audit-bar {
    margin-top: 28px;
    padding: 20px;
    background: var(--surface-low);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.arch-audit-bar p {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--on-surface-variant);
    margin: 0;
    line-height: 1.6;
}

/* Responsible design principles — bg-surface-container-low rounded-xl */
.principle-card {
    background: var(--surface-low);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    height: 100%;
}
.principle-card h4 {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--on-surface);
    margin: 0;
}
.principle-card p {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--on-surface-variant);
    line-height: 1.6;
    margin: 0;
}

/* MVP scope cards */
.scope-card {
    background: var(--surface-lowest);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 4px rgba(46,31,15,0.04);
}
.scope-card h3 {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--on-surface);
    margin: 0 0 14px;
}
.scope-row {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--on-surface-variant);
    margin-bottom: 10px;
    line-height: 1.5;
}
.scope-dot {
    width: 6px; height: 6px;
    border-radius: 9999px;
    flex-shrink: 0;
}
.scope-dot.secondary { background: var(--secondary); }
.scope-dot.tertiary  { background: var(--tertiary); }

/* Tech chip — surface-container-high */
.tech-chip {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 9999px;
    background: var(--surface-high);
    color: var(--on-surface);
    font-family: 'Inter', sans-serif;
    font-size: 0.8125rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    margin: 3px 3px;
}

/* About footer */
.about-footer {
    background: var(--surface-lowest);
    padding: 48px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 40px;
}
.about-footer-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.25rem;
    font-weight: 400;
    color: var(--on-surface);
}
.about-footer-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    color: var(--on-surface-variant);
    margin-top: 4px;
}

/* Differentiators section alt bg */
.diff-section-bg {
    background: rgba(255,227,203,0.3);
    margin-left: -2rem;
    margin-right: -2rem;
    padding: 64px 2rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
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
# Sidebar — exact stitch structure: aside bg-inverse-surface
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + wordmark
    st.markdown("""
    <div style="padding:28px 20px 20px;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:32px;height:32px;flex-shrink:0;">
                <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:32px;height:32px;">
                    <path d="M16 2L4 7v9c0 7.18 5.16 13.9 12 15.93C22.84 29.9 28 23.18 28 16V7L16 2z"
                          fill="#974311" opacity="0.9"/>
                    <path d="M16 2L4 7v9c0 7.18 5.16 13.9 12 15.93C22.84 29.9 28 23.18 28 16V7L16 2z"
                          fill="none" stroke="#ffb693" stroke-width="1.5"/>
                    <path d="M11 16l3.5 3.5L21 12" stroke="#ffffff" stroke-width="2"
                          stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div style="display:flex;flex-direction:column;">
                <span style="font-family:'Newsreader',Georgia,serif;font-size:1.1rem;
                             font-weight:500;color:#ffeee0;line-height:1.1;letter-spacing:-0.01em;">
                    DIVERT1
                </span>
                <span style="font-family:'Inter',sans-serif;font-size:0.6875rem;
                             font-weight:500;color:#897269;letter-spacing:0.02em;">
                    Online Safety Companion
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # + New Chat button
    if st.button("New Chat", use_container_width=True, type="primary",
                 key="new_chat"):
        st.session_state.thread_id = None
        st.session_state.messages  = []
        st.session_state.page      = "chat"
        st.rerun()

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Nav links
    if st.button("ℹ️  About & Architecture", use_container_width=True,
                 type="primary" if st.session_state.page == "about" else "secondary",
                 key="nav_about"):
        st.session_state.page = "about"
        st.rerun()

    if st.button("💬  Safety Companion Chat", use_container_width=True,
                 type="primary" if st.session_state.page == "chat" else "secondary",
                 key="nav_chat"):
        st.session_state.page = "chat"
        st.rerun()

    # Footer info
    st.markdown("""
    <div style="position:absolute;bottom:32px;left:0;right:0;padding:0 20px;">
        <div style="border-top:1px solid rgba(255,255,255,0.08);padding-top:16px;">
            <div style="font-family:'Inter',sans-serif;font-size:0.6875rem;
                        color:#897269;line-height:1.75;letter-spacing:0.02em;">
                <span style="color:#dcc1b6;font-weight:600;">Powered by</span><br>
                IBM watsonx Orchestrate<br><br>
                <span style="color:#dcc1b6;font-weight:600;">Built for</span><br>
                Neurodivergent young adults<br>
                navigating life online.
            </div>
        </div>
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
# PAGE: CHAT  —  divert1_safety_companion_chat_wcag_2.1_accessible/code.html
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "chat":

    if st.session_state.init_error:
        st.error(f"Could not connect to the agent:\n\n{st.session_state.init_error}")
        st.stop()

    st.markdown('<div class="chat-workspace">', unsafe_allow_html=True)

    # Active conversation context header
    st.markdown("""
    <div class="chat-header">
        <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-size:1.1rem;">💬</span>
            <span class="chat-header-title">Safety Companion</span>
            <span class="session-badge">Active Session</span>
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#897269;">
            DIVERT1 · IBM watsonx Orchestrate
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Welcome screen — shown when no messages yet ──────────────────────────
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-block">
            <div class="welcome-icon-wrap">🛡️</div>
            <h1 class="welcome-title">
                Hi! I'm your Online Safety Companion.<br>
                <span class="accent">How can I help you today?</span>
            </h1>
            <p class="welcome-sub">
                I help you check people, messages, and requests online.
                You decide what to do — I only give information and options.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Prompt chips — grid grid-cols-2 gap-3.5 max-w-2xl (stitch)
        CHIPS = [
            ("mark_email_unread", "Check a suspicious message or DM",
             "Screenshots, links, or awkward chats"),
            ("person_search",     "Check a person I met online",
             "New friends, gaming contacts, dates"),
            ("credit_card_off",   "Someone asked me for money",
             "Gift cards, crypto, urgent requests"),
            ("sentiment_worried", "I think I was already scammed",
             "What to do next and who to tell"),
        ]

        col_a, col_b = st.columns(2, gap="small")
        chip_col_map = [col_a, col_b, col_a, col_b]

        clicked_chip = None
        for (icon, title, sub), col in zip(CHIPS, chip_col_map):
            with col:
                st.markdown('<div class="chip-col">', unsafe_allow_html=True)
                label = f"**{title}**\n\n{sub}"
                if st.button(label, use_container_width=True, key=f"chip_{title}"):
                    clicked_chip = title
                st.markdown('</div>', unsafe_allow_html=True)

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

    # ── Dialogue log — role="log" aria-live="polite" ─────────────────────────
    else:
        st.markdown('<div class="dialogue-log" role="log" aria-live="polite">', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="msg-user-row">'
                    f'  <div class="msg-user-inner">'
                    f'    <div class="msg-user-meta"><span>You</span></div>'
                    f'    <div class="msg-user-bubble">{msg["text"]}</div>'
                    f'  </div>'
                    f'  <div class="msg-user-avatar">👤</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="msg-bot-row">'
                    f'  <div class="companion-avatar">🛡️</div>'
                    f'  <div class="msg-bot-inner">'
                    f'    <div class="msg-bot-label">DIVERT1 Companion</div>'
                    f'    <div class="sanctuary-card">{msg["text"]}</div>'
                    f'  </div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div>', unsafe_allow_html=True)  # close dialogue-log

    # ── Input bar — rounded-2xl bg-surface-container-low ────────────────────
    st.markdown('<div class="input-bar-wrap">', unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([9, 1])
        user_input = cols[0].text_input(
            label="companion_input",
            placeholder="How can I help you?",
            label_visibility="collapsed",
        )
        submitted = cols[1].form_submit_button("➤")

    st.markdown("""
    <div class="input-privacy-row">
        🔒&nbsp; DIVERT1 evaluates context respectfully.
        We never ask for passwords or private data.
        &nbsp;·&nbsp; <kbd style="padding:2px 6px;border-radius:4px;
        background:#ffe3cb;border:1px solid #dcc1b6;font-family:monospace;
        font-size:10px;">Esc</kbd> clears context
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close input-bar-wrap
    st.markdown('</div>', unsafe_allow_html=True)  # close chat-workspace

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
# PAGE: ABOUT  —  divert1_about_architecture/code.html
# ═════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":

    # ── Breadcrumb bar ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="breadcrumb-bar">
        <div style="display:flex;align-items:center;gap:6px;">
            <span>Safety Companion</span>
            <span style="font-size:0.9rem;">›</span>
            <span class="crumb-active">About &amp; Architecture</span>
        </div>
        <span class="breadcrumb-ver">v1.0 Architecture</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Immersive hero ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="about-hero">
        <div class="about-hero-badge">
            <span class="pulse"></span>
            Project DIVERT1
        </div>
        <h1>
            Online Safety
            <span class="italic-accent">Companion</span>
            <span class="alpha-badge">ALPHA</span>
        </h1>
        <p>
            A multi-agent AI that explains online risks in plain, calm language —
            designed from the ground up for neurodivergent young adults navigating
            scams, fraud, and social pressure online.
        </p>
        <div class="hero-pill-row">
            <span class="hero-pill">🔒 Zero Credential Capture</span>
            <span class="hero-pill">🧠 Calm Executive Support</span>
            <span class="hero-pill">⚙️ watsonx Orchestration</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Impact stat grid ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="small")
    for col, num, cls, lbl in [
        (c1, "3×",    "tertiary-fixed", "more likely to be targeted by online scams and coercive tactics"),
        (c2, "3",     "primary-fixed",  "specialized AI agents coordinating seamlessly in real time"),
        (c3, "100%",  "secondary-fixed","rule-based risk scoring — deterministic and fully auditable"),
        (c4, "0",     "surface",        "passwords, payment numbers, or state IDs ever requested"),
    ]:
        col.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-num {cls}">{num}</div>'
            f'<div class="stat-lbl">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── The Problem ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-eyebrow primary">The Context &amp; Gap</div>
    <div class="section-title">Why existing protective tools aren't enough</div>
    <p class="section-body">
        Conventional cyber security focuses on technical perimeters rather than subtle human
        persuasion, leaving critical blind spots for vulnerable users.
    </p>
    """, unsafe_allow_html=True)

    prob_l, prob_r = st.columns([5, 7], gap="large")
    with prob_l:
        st.markdown("""
        <div class="problem-infographic">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                <span style="font-family:'Inter',sans-serif;font-size:0.8125rem;font-weight:600;
                             color:#974311;">Social Engineering Trap</span>
                <span style="padding:4px 10px;border-radius:9999px;background:#ffdad6;
                             color:#93000a;font-family:'Inter',sans-serif;font-size:0.6875rem;
                             font-weight:600;">High Friction</span>
            </div>
            <h3 style="font-family:'Newsreader',Georgia,serif;font-size:1.25rem;font-weight:600;
                       color:#271909;margin:0 0 10px;">The Silence in the Grey Areas</h3>
            <p style="font-family:'Inter',sans-serif;font-size:0.875rem;color:#55433a;
                      line-height:1.65;margin:0 0 20px;">
                Technical filters successfully block known malicious links, but they cannot
                interpret social manipulation, artificial urgency, or friendship mimicry.
            </p>
            <div style="background:#fff8f4;border-radius:8px;padding:20px;">
                <div style="display:flex;justify-content:space-between;font-family:'Inter',sans-serif;
                            font-size:0.75rem;color:#55433a;margin-bottom:6px;">
                    <span>Automated Antivirus</span>
                    <span style="color:#266b40;font-weight:600;">Clean (Pass)</span>
                </div>
                <div style="background:#ffe3cb;border-radius:9999px;height:8px;overflow:hidden;margin-bottom:16px;">
                    <div style="background:#266b40;height:100%;width:100%;"></div>
                </div>
                <div style="display:flex;justify-content:space-between;font-family:'Inter',sans-serif;
                            font-size:0.75rem;color:#55433a;margin-bottom:6px;">
                    <span>Coercive Emotional Pressure</span>
                    <span style="color:#8d4b00;font-weight:600;">Undetected (Danger)</span>
                </div>
                <div style="background:#ffe3cb;border-radius:9999px;height:8px;overflow:hidden;margin-bottom:14px;">
                    <div style="background:#8d4b00;height:100%;width:85%;"></div>
                </div>
                <p style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#55433a;
                          text-align:center;font-style:italic;margin:0;">
                    "Technical protection says it is safe. Context proves otherwise."
                </p>
            </div>
            <div style="margin-top:16px;background:#ffead9;border-radius:8px;padding:14px 16px;
                        display:flex;align-items:center;gap:10px;">
                <span style="font-size:1.3rem;">💡</span>
                <span style="font-family:'Inter',sans-serif;font-size:0.875rem;color:#271909;">
                    DIVERT1 bridges the gap between binary firewall rules and human nuance.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with prob_r:
        for icon, title, body, variant in [
            ("🎯", "Higher targeting risk",
             "Neurodivergent individuals are statistically more likely to be deliberately targeted "
             "by fraudsters using rapid emotional pacing, specialized interest hijacking, and social isolation.",
             "primary"),
            ("🚫", "Tools only block — they don't explain",
             "Spam flags, browser red-screens, and generic block lists rarely state <strong>why</strong> "
             "an interaction is alarming or guide the user through constructive, calm next actions.",
             "tertiary"),
            ("📖", "Safety lessons are hard to follow",
             "Traditional safety materials often rely on ambiguous idioms, sarcastic examples, or "
             "presumed neurotypical social instincts, creating secondary confusion in high-anxiety moments.",
             "secondary"),
        ]:
            st.markdown(
                f'<div class="about-card" style="margin-bottom:16px;">'
                f'<div style="display:flex;align-items:flex-start;gap:16px;">'
                f'<div class="about-card-icon-wrap {variant}">{icon}</div>'
                f'<div>'
                f'<h4 style="font-family:\'Newsreader\',Georgia,serif;font-size:1.0625rem;'
                f'font-weight:600;color:#271909;margin:0 0 6px;">{title}</h4>'
                f'<p style="font-family:\'Inter\',sans-serif;font-size:0.9375rem;'
                f'color:#55433a;line-height:1.65;margin:0;">{body}</p>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Who It Is For ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;">
        <div class="section-eyebrow secondary">User Experience Focus</div>
        <div class="section-title" style="text-align:center;">Who it is built for</div>
        <p class="section-body" style="margin:0 auto 32px;">
            Crafted to preserve independence and self-advocacy without patronizing language.
        </p>
    </div>
    """, unsafe_allow_html=True)

    u1, u2, u3 = st.columns(3, gap="medium")
    for col, icon_bg, icon, title, body, tag_cls, tag_text in [
        (u1, "primary-fixed", "🧠", "Neurodivergent Young Adults",
         "Autistic people and people with ADHD who are navigating independent living, "
         "digital employment, or university life. Highly articulate, authentic, and naturally "
         "comfortable communicating via online spaces.",
         "primary", "Core Asset: Clear, literal processing"),
        (u2, "tertiary-fixed", "⚖️", "New to Adult Risks",
         "Encountering ambiguous demands for the first time: urgent peer payments, gift-card "
         "requests, romance escalation, or manipulative \"if you really trust me\" ultimatums "
         "from virtual acquaintances.",
         "tertiary", "Need: Step-by-step decision validation"),
        (u3, "secondary-fixed", "👥", "Support Network Often Absent",
         "Family members, student mentors, and support specialists cannot be present at 2:00 AM "
         "on a chat platform. Young adults need an immediate, non-judgmental soundboard right "
         "when situations unfold.",
         "secondary", "Outcome: Real-time autonomous triage"),
    ]:
        with col:
            st.markdown(
                f'<div class="about-card">'
                f'<div style="width:40px;height:40px;border-radius:9999px;'
                f'background:var(--{icon_bg});display:flex;align-items:center;'
                f'justify-content:center;font-size:1.2rem;margin-bottom:6px;">{icon}</div>'
                f'<h4 style="font-family:\'Newsreader\',Georgia,serif;font-size:1.0625rem;'
                f'font-weight:600;color:#271909;margin:0 0 8px;">{title}</h4>'
                f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
                f'color:#55433a;line-height:1.65;margin:0;">{body}</p>'
                f'<div class="cohort-tag {tag_cls}" style="margin-top:16px;">{tag_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Multi-Agent Architecture ───────────────────────────────────────────────
    st.markdown("""
    <div class="section-eyebrow primary">Technical Blueprint</div>
    <div class="section-title">Our Solution — Multi-Agent Architecture</div>
    <p class="section-body">
        Three specialized actors coordinated under IBM watsonx Orchestrate to separate
        conversation handling, objective risk analysis, and trauma-informed supportive guidance.
    </p>
    <br>
    """, unsafe_allow_html=True)

    st.markdown('<div class="agent-arch-wrap">', unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3, gap="medium")
    for col, num, variant, label, icon, title, body, note_key, note_val in [
        (a1, "1", "primary",   "Interface",     "🤖",
         "Main Chatbot Agent",
         "Welcomes the user into a low-sensory environment. Asks exactly one short question "
         "at a time to prevent cognitive overload, gently collecting conversation context.",
         "Pacing control:", "Max 1 inquiry per conversational turn"),
        (a2, "2", "tertiary",  "Scoring Engine","🔍",
         "Safety Agent",
         "Deterministic rule-based risk scoring. Evaluates patterns across 4 dimensions: "
         "urgency, financial redirection, isolation cues, and tone shifts over time.",
         "Yields:", "Risk level + Exact phrases of concern"),
        (a3, "3", "secondary", "Advocacy",      "🤝",
         "Support Agent",
         "Synthesizes raw risk findings into a calm, grounding summary with 2–3 actionable, "
         "non-pressured pathways. Offers pre-drafted neutral replies.",
         "Empowerment:", "Scripted neutral deferrals & verification"),
    ]:
        with col:
            st.markdown(
                f'<div class="agent-card">'
                f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                f'<span class="agent-num-badge {variant}">{num}</span>'
                f'<span class="agent-type-badge {variant}">{label}</span>'
                f'</div>'
                f'<div style="display:flex;align-items:center;gap:12px;">'
                f'<span style="font-size:1.5rem;">{icon}</span>'
                f'<h3 style="font-family:\'Newsreader\',Georgia,serif;font-size:1.0625rem;'
                f'font-weight:600;color:#271909;margin:0;">{title}</h3>'
                f'</div>'
                f'<p style="font-family:\'Inter\',sans-serif;font-size:0.875rem;'
                f'color:#55433a;line-height:1.65;margin:0;">{body}</p>'
                f'<div class="agent-card-note">'
                f'<strong>{note_key}</strong> {note_val}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("""
    <div class="arch-audit-bar">
        <span style="font-size:1.3rem;flex-shrink:0;">✅</span>
        <div>
            <div style="font-family:'Inter',sans-serif;font-size:0.875rem;font-weight:600;
                        color:#271909;margin-bottom:4px;">Auditable Data Handshake</div>
            <p class="arch-audit-bar" style="box-shadow:none;padding:0;background:none;margin:0;">
                No external model weights decide risk scores. The Safety Agent outputs transparent
                criteria before the Support Agent renders human text.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close agent-arch-wrap
    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Core Differentiators ──────────────────────────────────────────────────
    st.markdown("""
    <div class="section-eyebrow primary">Distinct Value</div>
    <div class="section-title">Key Differentiators</div>
    <br>
    """, unsafe_allow_html=True)

    d1, d2 = st.columns(2, gap="medium")
    d3, d4 = st.columns(2, gap="medium")
    for col, icon, title, body in [
        (d1, "🔎", "Whole-conversation analysis",
         "Rather than isolated keyword matching that flags benign sentences, DIVERT1 monitors "
         "behavioral arcs, shifting dynamics, and relationship pacing across entire chat logs."),
        (d2, "💬", "Explains the why",
         "Replaces vague red alert banners with clear, pedagogical logic. It details why a message "
         "creates artificial pressure, strengthening individual cyber discernment."),
        (d3, "🫂", "Respects friendships",
         "Recognizes that genuine friends sometimes need emergency help. It flags account compromise "
         "possibilities and recommends out-of-band checks without accusing the friend."),
        (d4, "😌", "Avoids over-warning",
         "Sensory fatigue occurs when safety tools cry wolf. DIVERT1 validates safe, genuine "
         "conversations with positive reassurance rather than nervous warnings."),
    ]:
        with col:
            st.markdown(
                f'<div class="about-card" style="display:flex;flex-direction:row;'
                f'align-items:flex-start;gap:16px;margin-bottom:16px;">'
                f'<div style="padding:10px;border-radius:8px;background:#ffead9;'
                f'flex-shrink:0;font-size:1.3rem;">{icon}</div>'
                f'<div>'
                f'<h3 style="font-family:\'Newsreader\',Georgia,serif;font-size:1.0625rem;'
                f'font-weight:600;color:#271909;margin:0 0 6px;">{title}</h3>'
                f'<p style="font-family:\'Inter\',sans-serif;font-size:0.9375rem;'
                f'color:#55433a;line-height:1.65;margin:0;">{body}</p>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Responsible Design & MVP Scope ────────────────────────────────────────
    st.markdown("""
    <div class="section-eyebrow secondary">Governance &amp; Boundaries</div>
    <div class="section-title">Responsible Design &amp; MVP Scope</div>
    <br>
    """, unsafe_allow_html=True)

    # 5 principle cards
    p1, p2, p3, p4, p5 = st.columns(5, gap="small")
    for col, icon, title, body in [
        (p1, "🚫", "Never labels",
         "Never calls someone a \u2018scammer\u2019. Focuses entirely on observable message behaviors."),
        (p2, "✋", "User decides",
         "Never locks the screen or imposes mandatory blocks. Agency remains with the user."),
        (p3, "🔑", "No secrets",
         "Will never accept or store credentials, passkeys, financial PINs, or ID uploads."),
        (p4, "📋", "Fully auditable",
         "Rule heuristics are plain text rules, not inaccessible black-box probabilities."),
        (p5, "🌐", "Clear language",
         "Zero metaphors, idioms, or ambiguous sarcasm in safety assessments."),
    ]:
        with col:
            st.markdown(
                f'<div class="principle-card">'
                f'<span style="font-size:1.3rem;">{icon}</span>'
                f'<h4>{title}</h4>'
                f'<p>{body}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # MVP scope
    s1, s2 = st.columns(2, gap="large")
    with s1:
        st.markdown("""
        <div class="scope-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <span style="font-size:1.2rem;">✅</span>
                <h3 style="margin:0;">Included in Current Scope (MVP)</h3>
            </div>
        """, unsafe_allow_html=True)
        for item in [
            "Real-time chat log copy-paste analysis",
            "Deterministic rule-based risk classification",
            "Low-sensory, high-contrast, calm interface mode",
            "Template response generation for respectful boundaries",
            "Plain-English safety concept library & glossaries",
        ]:
            st.markdown(
                f'<div class="scope-row">'
                f'<div class="scope-dot secondary"></div>{item}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class="scope-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <span style="font-size:1.2rem;">⏳</span>
                <h3 style="margin:0;">Planned for Future Cycles (Out of Scope)</h3>
            </div>
        """, unsafe_allow_html=True)
        for item in [
            "Direct OS screen recording or silent background monitoring",
            "Automated contact blocking or account suspension actions",
            "Financial account or banking API integrations",
            "Automated parent or supervisor notification alerts",
            "Automated law enforcement incident dispatching",
        ]:
            st.markdown(
                f'<div class="scope-row">'
                f'<div class="scope-dot tertiary"></div>{item}'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tech chips
    st.markdown("""
    <div style="font-family:'Inter',sans-serif;font-size:0.6875rem;font-weight:600;
                letter-spacing:0.08em;text-transform:uppercase;color:#897269;margin-bottom:10px;">
        Engineered With
    </div>
    <div>
    """, unsafe_allow_html=True)
    for chip in ["IBM watsonx Orchestrate", "Multi-Agent Orchestration",
                 "Rule-Based Risk Scoring", "Python 3.11",
                 "Transparent Heuristics", "Neuro-Inclusive UX"]:
        st.markdown(f'<span class="tech-chip">{chip}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="about-footer">
        <div>
            <div class="about-footer-title">DIVERT1
                <span style="font-family:'Inter',sans-serif;font-size:0.875rem;
                             font-weight:500;color:#974311;margin-left:8px;">
                    Safe Space Companion
                </span>
            </div>
            <div class="about-footer-sub">
                Dedicated to unconditional psychological safety and autonomous online confidence.
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:20px;">
            <div style="text-align:right;">
                <div style="font-family:'Inter',sans-serif;font-size:0.6875rem;
                            color:#897269;">Powered by</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.875rem;
                            font-weight:600;color:#271909;">IBM watsonx</div>
            </div>
            <div style="width:40px;height:40px;border-radius:9999px;background:#fff1e7;
                        display:flex;align-items:center;justify-content:center;font-size:1.2rem;">
                🌿
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
