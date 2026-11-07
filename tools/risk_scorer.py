"""
risk_scorer.py
==============
IBM watsonx Orchestrate ADK tool for the Online Safety Companion project.

Analyzes a message or profile text and returns a structured risk assessment
containing a risk level (low / medium / high), a list of detected signals,
and recommended next steps.

Detection is rule-based using keyword/phrase matching. It is intentionally
transparent so that safety agents and human reviewers can audit every decision.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from ibm_watsonx_orchestrate.agent_builder.tools import tool


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RiskAssessment:
    """Structured output returned by score_risk."""
    risk_level: str                          # "low" | "medium" | "high"
    signals: list[str]                       # human-readable signal labels
    recommended_next_steps: list[str]        # actionable steps for the agent
    signal_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.signal_count = len(self.signals)


# ---------------------------------------------------------------------------
# Signal definitions
# ---------------------------------------------------------------------------

# Each entry: (signal_label, [regex_patterns], weight)
# weight 1 = minor concern; weight 2 = strong red flag
_SIGNAL_RULES: list[tuple[str, list[str], int]] = [
    (
        "Platform migration pressure",
        [
            r"\b(move|switch|come|join|add me|find me|message me|contact me)\b.{0,40}"
            r"\b(telegram|whatsapp|snapchat|kik|signal|wickr|viber|line app)\b",
            r"\b(telegram|whatsapp|snapchat|kik|signal|wickr)\b.{0,40}"
            r"\b(better|safer|private|secret|easier|cleaner)\b",
        ],
        2,
    ),
    (
        "Secrecy from parents or family",
        [
            r"\b(don'?t (tell|mention|say|show)|keep (this|it|us) secret|"
            r"between (us|you and me)|delete (this|after)|hide (this|it|our))\b",
            r"\b(parents?|family|mum|mom|dad|sister|brother).{0,40}"
            r"\b(won'?t understand|freak out|get angry|not get it|make it awkward|"
            r"wouldn'?t understand|would freak)\b",
            r"\b(they won'?t understand|they wouldn'?t understand)\b",
            r"\b(don'?t (tell|mention|say).{0,20}"
            r"(parents?|family|mum|mom|dad|friends?))\b",
        ],
        2,
    ),
    (
        "Isolation language",
        [
            r"\b(only (you|we|us)|no one else (gets|understands|knows))\b",
            r"\byou('?re| are) (the only one|different|special|not like them)\b",
            r"\b(stay away from|stop talking to|avoid) (your )?"
            r"(friends?|family|parents?)\b",
        ],
        2,
    ),
    (
        "Money or financial request",
        [
            r"\b(send|transfer|wire|give|lend|borrow|need).{0,30}"
            r"\b(money|cash|dollars?|pounds?|euros?|funds?)\b",
            r"\b(gift card|itunes|google play|amazon|steam card|voucher)\b",
            r"\b(bitcoin|crypto|eth|ethereum|usdt|paypal|venmo|cashapp|zelle)\b.{0,20}"
            r"\b(send|transfer|pay|give)\b",
            r"\b(send|transfer|pay|give)\b.{0,20}"
            r"\b(bitcoin|crypto|eth|ethereum|usdt|paypal|venmo|cashapp|zelle)\b",
        ],
        2,
    ),
    (
        "Photo or video request",
        [
            r"\b(send|share|show|take).{0,30}"
            r"\b(pic(s|ture)?|photo|image|selfie|nude|naked|video|clip)\b",
            r"\b(sexy|intimate|private|adult).{0,20}"
            r"\b(pic(s|ture)?|photo|image|selfie|video)\b",
            r"\bshow me (your|you)\b",
        ],
        2,
    ),
    (
        "Fake urgency",
        [
            r"\b(right now|immediately|urgent|asap|hurry|limited time|"
            r"expires? (tonight|today|soon)|must reply|reply fast|"
            r"don'?t wait|act now|time is running out)\b",
        ],
        1,
    ),
    (
        "Too-good-to-be-true offer",
        [
            r"\b(guaranteed|100%|risk.?free|double your|triple your)\b",
            r"\b(model(l?ing)?|casting|influencer|brand deal|sponsorship).{0,30}"
            r"\b(offer|opportunity|contract|audition)\b",
            r"\b(win|winner|prize|lottery|selected|chosen|reward).{0,30}"
            r"\b(claim|collect|verify|confirm)\b",
            r"\b(easy money|make \$|earn \$|passive income|invest .{0,15} return)\b",
        ],
        1,
    ),
    (
        "Love-bombing or excessive flattery",
        [
            r"\b(you'?re? (so )?(mature|beautiful|gorgeous|perfect|amazing|"
            r"special|unique|not like other)).{0,20}\b",
            r"\b(i love you|i('?ve| have) (never )?felt this way|"
            r"you'?re? my (soulmate|everything|world|one))\b.{0,50}"
            r"(after|already|just|only).{0,10}(day|week|hour|message|met)\b",
            r"\b(destiny|meant to be|fate|love at first)\b",
        ],
        1,
    ),
    (
        "Personal information request",
        [
            r"\b(what('?s| is) your (address|home|school|college|uni|workplace|"
            r"work|location|street|postcode|zip|route|schedule))\b",
            r"\b(where do you (live|go to school|work|study|stay))\b",
            r"\b(send (me )?your (location|address|home|school))\b",
            r"\b(full name|last name|surname|id (card|number)|passport)\b",
        ],
        1,
    ),
    (
        "In-person meeting request",
        [
            r"\b(meet (up|in person|irl|face.?to.?face)|come (over|to mine|"
            r"to my place|see me)|visit me|hang out (in person|at mine))\b",
            r"\b(i'?ll |i could |i can )(pick you up|come to you|come get you)\b",
            r"\b(alone|just (us|the two of us)|without (your )?"
            r"(friends?|parents?|family))\b",
            r"\b(pick you up|come get you|quiet spot|private place|"
            r"somewhere (quiet|private|alone|just us))\b",
        ],
        2,
    ),
    (
        "Sextortion / leverage with existing content",
        [
            r"\b(i have (your )?(pictures?|photos?|videos?|screenshots?|nudes?))\b",
            r"\b(will (send|post|share|expose|leak)).{0,30}"
            r"\b(pictures?|photos?|videos?|screenshots?)\b",
            r"\b(everyone (will|is going to) (see|know))\b",
            r"\b(pay (me|up)|send (money|more|another)).{0,30}"
            r"\b(or (i|i'?ll|we|they))\b",
        ],
        2,
    ),
    (
        "Inconsistent identity claims",
        [
            r"\b(i'?m (actually|really|secretly|not really) "
            r"(a|an|the|just|also))\b",
            r"\b(i (lied|wasn'?t honest|forgot to mention|didn'?t tell you))\b",
        ],
        1,
    ),
]


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------

def _compile_patterns(patterns: list[str]) -> list[re.Pattern]:
    return [re.compile(p, re.IGNORECASE | re.DOTALL) for p in patterns]


_COMPILED_RULES: list[tuple[str, list[re.Pattern], int]] = [
    (label, _compile_patterns(patterns), weight)
    for label, patterns, weight in _SIGNAL_RULES
]


# Signals that are high-risk even when appearing alone (weight-2 critical signals)
_ALWAYS_HIGH_SIGNALS: frozenset[str] = frozenset({
    "Photo or video request",
    "Sextortion / leverage with existing content",
    "In-person meeting request",
    "Money or financial request",
    "Platform migration pressure",
})


def _compute_risk_level(total_weight: int, signal_count: int,
                        signals: list[str]) -> str:
    if total_weight == 0:
        return "low"
    # Any single critical signal is immediately high-risk
    if any(s in _ALWAYS_HIGH_SIGNALS for s in signals):
        return "high"
    if total_weight <= 2 and signal_count <= 1:
        return "medium"
    return "high"


def _build_next_steps(risk_level: str, signals: list[str]) -> list[str]:
    steps: list[str] = []
    if risk_level == "low":
        steps.append("Continue talking cautiously and notice if anything changes.")
        steps.append("It is always okay to stop the conversation at any time.")
        return steps

    steps.append("Do not share personal information like your address or school.")
    steps.append("You do not have to reply right away. Take your time.")

    if risk_level == "high":
        steps.append("Consider stopping the conversation for now.")
        steps.append(
            "Talk to a trusted adult — a parent, teacher, or support worker."
        )
        steps.append("Do not delete messages — keep them as evidence.")
        steps.append("Take screenshots before anything changes.")

    if any(s in signals for s in ["Sextortion / leverage with existing content",
                                   "Photo or video request", "Money or financial request",
                                   "In-person meeting request"]):
        steps.append(
            "US: Report to NCMEC CyberTipline at https://report.cybertip.org"
        )
        steps.append(
            "Canada: Report to Canadian Centre for Child Protection at "
            "https://www.cybertip.ca"
        )
        steps.append(
            "If you feel unsafe right now, call or text 988 (US/Canada crisis line)."
        )

    return steps


# ---------------------------------------------------------------------------
# Public ADK tool
# ---------------------------------------------------------------------------

@tool
def score_risk(
    message_text: str,
    context: Optional[str] = None,
) -> dict:
    """
    Analyze a message or profile text for online safety risk signals.

    Applies rule-based pattern matching to detect grooming, scam, sextortion,
    and other harmful behaviour patterns. Returns a structured risk assessment
    that the Safety Agent uses to generate its response.

    Args:
        message_text: The exact text of the message, profile, or request
                      received by the user. Required.
        context:      Optional background information such as where they met
                      the person, what platform was used, or what has happened
                      so far in the conversation. Providing context improves
                      accuracy.

    Returns:
        A dict with keys:
        - risk_level (str):              "low", "medium", or "high"
        - signals (list[str]):           Labels of detected warning signals
        - recommended_next_steps (list[str]): Actionable steps for the agent
        - signal_count (int):            Number of distinct signals found
        - analyzed_text_length (int):    Character count of the analyzed text
    """
    combined_text = message_text
    if context:
        combined_text = f"{message_text}\n\nCONTEXT: {context}"

    detected_signals: list[str] = []
    total_weight: int = 0

    for label, compiled_patterns, weight in _COMPILED_RULES:
        for pattern in compiled_patterns:
            if pattern.search(combined_text):
                if label not in detected_signals:
                    detected_signals.append(label)
                    total_weight += weight
                break  # one match per rule group is enough

    risk_level = _compute_risk_level(total_weight, len(detected_signals), detected_signals)
    next_steps = _build_next_steps(risk_level, detected_signals)

    assessment = RiskAssessment(
        risk_level=risk_level,
        signals=detected_signals,
        recommended_next_steps=next_steps,
    )

    return {
        "risk_level": assessment.risk_level,
        "signals": assessment.signals,
        "recommended_next_steps": assessment.recommended_next_steps,
        "signal_count": assessment.signal_count,
        "analyzed_text_length": len(combined_text),
    }
