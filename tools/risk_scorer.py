"""
risk_scorer.py
==============
IBM watsonx Orchestrate ADK tool for the Online Safety Companion project.

Checks a message, chat, profile or described situation for scam, grooming,
sextortion and manipulation signals and returns EVIDENCE for the Safety Agent:
a risk level, the signals found (with the exact words), signs that reduce
concern, how the chat changed over time, and one useful follow-up question.

Design notes
- Rule-based on purpose: every decision can be audited.
- The tool is a floor, not a ceiling. The Safety Agent may RAISE the level if
  it sees a clear warning sign the rules missed. It should not lower a HIGH.
- The tool gives no advice. Advice is the Support Agent's job.
"""

import re
from typing import NamedTuple, Optional

from ibm_watsonx_orchestrate.agent_builder.tools import tool


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

# critical = high risk on its own
L_THREAT = "Threat or blackmail"
L_CRED = "Request for password, login code, or account access"
L_SENSITIVE = "Request for card, bank, or ID details"
L_INTIMATE = "Request for private or intimate photos"
L_SECRET = "Request to keep the chat secret"
L_PAYMENT = "Payment by gift card, crypto, or wire"
L_ALONE = "Pressure to meet alone or in private"
# strong = 2 points
L_MONEY = "Money request"
L_IMPERSON = "Pretending to be support or an official"
L_MIGRATE = "Pressure to move to another app"
L_ISOLATE = "Isolation language"
L_NOTELL = "Asks you not to tell anyone"
L_GUILT = "Pressure to prove trust, or guilt"
L_LOVE = "Love-bombing (affection that moves too fast)"
L_PRIZE = "Prize or giveaway offer"
L_PHOTO = "Request for a photo of the user"
L_INJECT = "Instructions aimed at the safety checker"
# minor = 1 point
L_URGENCY = "Fake urgency"
L_PERSONAL = "Personal information request"
L_MEET = "In-person meeting request"
L_OFFER = "Too-good-to-be-true offer"
L_FLATTER = "Excessive flattery"
L_VERIFY = "Avoids or refuses verification"
L_LINK = "Link click request"
L_IDENT = "Inconsistent identity claims"
# story = 2 points, but only when a money or payment request is also present
L_STORY = "Emotional emergency story"

M_VERIFY = "Offers a way to verify"
M_NOPRESS = "Accepts 'no' or shows no pressure"

_CRITICAL, _STRONG, _MINOR, _STORY = "critical", "strong", "minor", "story"
_POINTS = {_STRONG: 2, _MINOR: 1, _STORY: 2}
_FINANCIAL = {L_MONEY, L_PAYMENT}


# ---------------------------------------------------------------------------
# Rule definitions
# "@" inside a pattern means "a short gap inside the same sentence".
# ---------------------------------------------------------------------------

_GAP = r"[^.!?\n]"


class _Rule(NamedTuple):
    label: str
    tier: str
    patterns: tuple
    new_contact_only: bool = False
    skip_if: Optional[re.Pattern] = None
    guard_negation: bool = False


def _c(*patterns: str) -> tuple:
    return tuple(re.compile(p.replace("@", _GAP), re.IGNORECASE) for p in patterns)


_AMOUNT = (
    r"(?:\$\s?\d|\b\d[\d,]*\s?(?:bucks|dollars?|usd|cad|pounds?|euros?)\b"
    r"|\b(?:money|cash|funds)\b)"
)
_PHOTO_WORD = r"(?:pics?|pictures?|photos?|selfies?)"
_PUBLIC_PLACE = re.compile(
    r"\b(library|cafe|coffee shop|campus|class|club|mall|school|cafeteria|"
    r"food court|study group|lab|lobby|server|voice channel|tournament|"
    r"convention|event|stream)\b",
    re.IGNORECASE,
)
_NEGATION = re.compile(r"(never|not\b|n't|cannot|unable|without)", re.IGNORECASE)

_RULES: list = [
    # ---------------- critical ----------------
    _Rule(L_THREAT, _CRITICAL, _c(
        r"\b(?:i have|i got|i saved|i kept)\b@{0,25}\b(?:your|ur)\b@{0,25}\b"
        r"(?:pics?|pictures?|photos?|videos?|screenshots?|nudes?|chats?|messages|secrets?)\b",
        r"\b(?:i'?ll|i will|i'?m going to|gonna|will|he'?ll|she'?ll|they'?ll)\b@{0,20}\b"
        r"(?:send|post|share|show|expose|leak|tell|release)\b@{0,40}\b"
        r"(?:pics?|pictures?|photos?|videos?|screenshots?|nudes?|chats?|messages|everyone|"
        r"your (?:parents|friends|family|school))\b",
        r"\beveryone (?:will|is going to|'?ll) (?:see|know|find out)\b",
        r"\b(?:pay|send|give)\b@{0,30}\bor (?:i'?ll|i will|else|they'?ll|we'?ll)\b@{0,25}\b"
        r"(?:share|post|leak|expose|tell|send|hurt|show|report)\b",
        r"\bif you (?:don'?t|do not|refuse|say no|tell anyone)\b@{0,40}\b"
        r"(?:share|post|leak|expose|send|tell|hurt|report)\b",
    )),
    _Rule(L_CRED, _CRITICAL, _c(
        r"\b(?:send|give|tell|share|read|text|forward|enter|type|what'?s|what is|need)\b@{0,30}\b"
        r"(?:password|passcode|login|log-?in|pin|verification code|security code|otp|2fa|"
        r"one.?time (?:code|password))\b",
        r"\bcode\b@{0,20}\b(?:we|i|they|he|she) (?:just )?(?:sent|texted|emailed)\b",
        r"\blog ?in (?:with|to|using|through)\b@{0,25}\b"
        r"(?:bank|account|steam|discord|instagram|paypal|facebook|google|apple)\b",
        r"\b(?:install|download|open)\b@{0,15}\b(?:anydesk|teamviewer|remote access|quick ?support)\b",
    )),
    _Rule(L_SENSITIVE, _CRITICAL, _c(
        r"\b(?:send|give|tell|share|show|upload|need|what'?s|what is)\b@{0,30}\b"
        r"(?:card number|debit card|credit card|bank (?:account|details|info|information|login)|"
        r"account number|routing number|ssn|social security|sin number|passport|"
        r"driver'?s? licen[cs]e|id (?:card|photo|picture|scan)|photo of (?:your |my |an? |the )?id)\b",
        r"\b(?:send|give|show|upload)\b@{0,20}\b(?:your|my|an?|the) id\b",
    )),
    _Rule(L_INTIMATE, _CRITICAL, _c(
        r"\b(?:nudes?|naked|nsfw|sexy " + _PHOTO_WORD + r"|intimate " + _PHOTO_WORD +
        r"|private " + _PHOTO_WORD + r")\b",
        r"\b(?:without|take off)\b@{0,10}\b(?:clothes|shirt)\b",
    )),
    _Rule(L_SECRET, _CRITICAL, _c(
        r"\b(?:keep|keeping)\b@{0,15}\b(?:this|it|us|that|our (?:chat|chats|talk|conversation|"
        r"friendship|relationship))\b@{0,15}\b(?:secret|private|between us|quiet)\b",
        r"\b(?:don'?t|do not|never)\b@{0,10}\b(?:tell|mention|say|show|talk)\b@{0,25}\b"
        r"(?:your (?:parents?|mom|mum|dad|family|friends?|teacher|school))\b",
        r"\bbetween (?:us|you and me)\b",
        r"\b(?:delete|erase)\b@{0,15}\b(?:this|these|our|the)\b@{0,10}\b(?:chats?|messages?|conversation)\b",
        r"\b(?:our|this) (?:little )?secret\b",
    )),
    _Rule(L_PAYMENT, _CRITICAL, _c(
        r"\b(?:send|buy|get|need|want|purchase|pay|give|load|scratch)\b@{0,40}\bgift ?cards?\b",
        r"\bin gift ?cards?\b",
        r"\bgift ?cards?\b@{0,25}\b(?:code|number|pin|picture|photo|receipt)\b",
        r"\b(?:send|transfer|pay|buy|deposit|invest|wire)\b@{0,40}\b"
        r"(?:bitcoin|btc|crypto(?:currency)?|ethereum|usdt|tether|western union|moneygram|wire transfer)\b",
        r"\b(?:bitcoin|btc|crypto(?:currency)?|ethereum|usdt|tether)\b@{0,30}\b(?:wallet|address)\b",
    )),
    _Rule(L_ALONE, _CRITICAL, _c(
        r"\b(?:come|meet)\b@{0,30}\b(?:alone|by yourself|just (?:us|the two of us|you and me)|"
        r"without (?:your )?(?:friends?|parents?|family|anyone))\b",
        r"\b(?:pick you up|come get you)\b@{0,40}\b(?:alone|secret|late|private)\b",
        r"\bsomewhere (?:quiet|private|alone)\b",
    )),

    # ---------------- strong ----------------
    _Rule(L_MONEY, _STRONG, _c(
        r"\b(?:send|transfer|wire|give|lend|loan|borrow|spare|need)\b@{0,40}" + _AMOUNT,
        r"\b(?:ask(?:s|ed|ing)?|want(?:s|ed)?|need(?:s|ed)?|request(?:s|ed|ing)?)\b@{0,20}" + _AMOUNT,
        r"\b(?:short|low) on (?:money|cash|funds)\b",
        r"\bpay (?:you|me)? ?back\b",
        r"\b(?:send|transfer|pay)\b@{0,30}\b(?:cash ?app|venmo|zelle|paypal|e-?transfer|interac)\b",
    )),
    _Rule(L_IMPERSON, _STRONG, _c(
        r"\b(?:i'?m|i am|this is|we are|we'?re)\b@{0,8}\b(?:from|with)\b@{0,8}\b(?:steam|discord|"
        r"support|bank|police|government|tech support|microsoft|apple|paypal|amazon|"
        r"customer service|security team|admin|moderator|staff)\b",
        r"\b(?:steam|discord|microsoft|apple|paypal|amazon) (?:support|staff|security|team|admin|"
        r"moderator|agent)\b",
        r"\byour (?:account|device|computer|card|bank|steam account|discord account|paypal)\b@{0,25}\b"
        r"(?:was|has been|is|got)\b@{0,15}\b(?:hacked|compromised|suspended|locked|blocked|frozen|"
        r"at risk|banned)\b",
    )),
    _Rule(L_MIGRATE, _STRONG, _c(
        r"\b(?:move|switch|come|join|add me|find me|message me|contact me|text me|dm me|talk|chat|"
        r"text|speak|continue)\b@{0,40}\b(?:telegram|whatsapp|snapchat|snap|kik|wickr|viber|signal|"
        r"line app|skype|another app|different app|private chat)\b",
        r"\b(?:telegram|whatsapp|snapchat|kik|wickr|signal)\b@{0,40}\b(?:better|safer|private|"
        r"secret|easier|cleaner|instead)\b",
    )),
    _Rule(L_NOTELL, _STRONG, _c(
        r"\b(?:don'?t|do not|never)\b@{0,10}\b(?:tell|mention|say|show|talk)\b@{0,25}\b(?:anyone|anybody|others?)\b",
    )),
    _Rule(L_ISOLATE, _STRONG, _c(
        r"\bonly i (?:understand|get|care about|love)\b",
        r"\bno one (?:else )?(?:gets|understands|cares about|knows) you\b",
        r"\b(?:your|ur) (?:parents?|family|friends?|mom|mum|dad)\b@{0,20}\b(?:don'?t|do not|won'?t|"
        r"wouldn'?t) (?:get|understand|care about|love|know) (?:you|us|this)\b",
        r"\b(?:parents?|family)\b@{0,30}\b(?:won'?t understand|wouldn'?t understand|would freak|"
        r"will freak|get angry|not get it)\b",
        r"\b(?:stay away from|stop talking to|avoid|ignore)\b@{0,10}\b(?:your )?(?:friends?|family|parents?)\b",
        r"\b(?:don'?t|do not) (?:need|trust) (?:them|your (?:friends?|family|parents?))\b",
    )),
    _Rule(L_GUILT, _STRONG, _c(
        r"\bif you (?:really |truly )?(?:trust|trusted|care|cared|loved|were my friend|are my friend|love me)\b",
        r"\bprove (?:it|that|you|your)\b@{0,15}\b(?:trust|love|care|friend|loyal)",
        r"\bwhy (?:don'?t|do not|can'?t|won'?t) you trust me\b",
        r"\bafter (?:all|everything) (?:i'?ve|i have|we'?ve|we have) (?:done|been through|shared)\b",
        r"\byou owe me\b",
        r"\bor i'?ll stop (?:being|talking|being friends)\b",
        r"\byou'?re the only (?:one|person) i (?:trust|can ask|have)\b",
    )),
    _Rule(L_LOVE, _STRONG, _c(
        r"\bi love you already\b",
        r"\bi'?ve never felt (?:this|like this|this way)\b",
        r"\b(?:you'?re|you are) my (?:soulmate|everything|world|one and only)\b",
        r"\bmeant to be together\b",
        r"\blove at first sight\b",
        r"\bdestiny (?:brought|led) us\b",
        r"\bcan'?t live without you\b",
    )),
    _Rule(L_LOVE, _STRONG, _c(
        r"\bi love you\b",
        r"\bfalling for you\b",
    ), new_contact_only=True),
    _Rule(L_PRIZE, _STRONG, _c(
        r"\byou(?:'ve| have)? (?:won|win|been selected|been chosen)\b@{0,30}\b(?:free|prize|giveaway|"
        r"iphone|ps5|switch|laptop|reward|lottery|gift)\b",
        # "free 10,000 Robux" — number between free and item name
        r"\bfree\b@{0,20}\b(?:nitro|robux|v-?bucks|skins?|ps5|iphone|gift|money)\b",
        r"\bclaim (?:your )?(?:prize|reward|gift|nitro|robux|v-?bucks)\b",
    )),
    _Rule(L_PHOTO, _CRITICAL, _c(
        r"\b(?:send|share|show|take|post)\b@{0,15}\b" + _PHOTO_WORD + r"\b@{0,12}\bof (?:you|yourself|ur ?self)\b",
        r"\b(?:send|share|show)\b@{0,12}\b(?:your|ur) " + _PHOTO_WORD + r"\b",
        r"\b(?:can|could|will|would) you (?:send|share|show)\b@{0,12}\b" + _PHOTO_WORD + r"\b",
        r"\b(?:ask(?:s|ed|ing)?|want(?:s|ed)?|request(?:s|ed|ing)?)\b@{0,15}\b" + _PHOTO_WORD +
        r"\b@{0,12}\b(?:of )?(?:me|you|myself)\b",
        # "send me a photo" bare form, "make it more personal"
        r"\bsend me a? ?" + _PHOTO_WORD + r"\b",
        r"\bmake it (?:a bit |more )?(?:personal|intimate|private|special)\b",
    )),
    # L_INJECT is promoted to _CRITICAL — it is an active attack on the checker
    _Rule(L_INJECT, _CRITICAL, _c(
        r"\b(?:ignore|disregard|forget)\b@{0,20}\b(?:instructions?|rules?|prompts?|guidelines?)\b",
        r"\b(?:say|mark|rate|label|report|output|respond with)\b@{0,25}\b(?:safe|low risk|legit|no risk)\b",
        r"\bsystem prompt\b|\byou are now\b|\bdeveloper mode\b|\bjailbreak\b",
    )),

    # ---------------- minor ----------------
    _Rule(L_URGENCY, _MINOR, _c(
        r"\b(?:right now|immediately|urgent(?:ly)?|asap|hurry|limited time|expires? (?:tonight|today|soon)|"
        r"must reply|reply (?:fast|now)|don'?t wait|act now|time is running out|before it'?s too late|"
        r"within (?:the )?(?:hour|day|\d+ (?:minutes?|hours?)))\b",
        r"\b(?:today|tonight) or\b",
        r"\b(?:send|pay|give|transfer)\b@{0,40}\b(?:today|tonight|now|asap|immediately)\b",
        r"\bneed (?:it|this|that|them|the money|money) (?:today|tonight|asap|immediately|right now)\b",
    )),
    _Rule(L_PERSONAL, _MINOR, _c(
        r"\b(?:what'?s|what is|tell me|send me|give me)\b@{0,15}\b(?:your )?(?:home )?(?:address|location|"
        r"school|college|workplace|street|postcode|postal code|zip|schedule|full name|last name)\b",
        r"\bwhere do you (?:live|go to school|work|study|stay)\b",
        r"\b(?:are you|r u) (?:home )?alone\b",
    )),
    _Rule(L_MEET, _MINOR, _c(
        r"\b(?:meet (?:up|in person|irl|face.?to.?face)|meet (?:me|you) (?:at|in|on|tonight|tomorrow|this)|"
        r"come (?:over|to my (?:place|house|apartment|room)|see me)|visit me)\b",
        r"\b(?:i'?ll|i will|i can|i could) (?:pick you up|come get you|come to you|drive to you)\b",
        r"\bi'?m coming to (?:see|visit) you\b",
    ), skip_if=_PUBLIC_PLACE, guard_negation=True),
    _Rule(L_OFFER, _MINOR, _c(
        r"\b(?:guaranteed (?:returns?|profit|income|money)|risk.?free|double your|triple your|get rich|"
        r"easy money|passive income)\b",
        r"\b(?:earn|make|get paid)\b@{0,15}(?:\$\s?\d[\d,]*|\d[\d,]*\s?(?:bucks|dollars|usd))\s?"
        r"(?:a|per|each|every) (?:day|hour|week)\b",
        r"\bno interview\b",
        r"\b(?:trading|forex|crypto)\b@{0,30}\b(?:teach|mentor|signals?|profit|earn|guaranteed)\b",
        r"\b(?:modeling|modelling|casting|influencer|brand deal|sponsorship)\b@{0,30}\b"
        r"(?:offer|opportunity|contract|audition|job)\b",
    )),
    _Rule(L_FLATTER, _MINOR, _c(
        r"\bso mature for your age\b",
        r"\byou(?:'re| are| seem) (?:so )?(?:special|different from (?:other|all|everyone)|"
        r"not like (?:other|the others|them))\b",
        r"\bnot like other (?:girls|guys|people|boys)\b",
    )),
    _Rule(L_VERIFY, _MINOR, _c(
        r"\b(?:camera|webcam|mic|microphone|phone)\b@{0,15}\b(?:broken|not working|doesn'?t work|dead|"
        r"cracked|busted)\b",
        r"\b(?:can'?t|cannot|won'?t|unable to|not allowed to|don'?t want to)\b(?! wait)@{0,20}\b"
        r"(?:video|voice call|call|face ?time|show my face)\b",
        r"\b(?:doesn'?t|don'?t|does not|do not) (?:let|allow) me (?:use|have|make)\b@{0,20}\b(?:phone|calls?|video)\b",
        r"\bwhy do you need (?:a |to )?(?:call|video|proof|see|verify)\b",
        r"\bno need for (?:a )?(?:call|video|proof)\b",
    )),
    _Rule(L_LINK, _MINOR, _c(
        r"\b(?:click|tap|open|follow|visit|go to)\b@{0,25}\b(?:link|url|website|site)\b",
        r"\b(?:bit\.ly|tinyurl\.com|t\.co|cutt\.ly|rb\.gy|is\.gd)\b",
    )),
    _Rule(L_IDENT, _MINOR, _c(
        r"\bi (?:lied|wasn'?t honest|was lying)\b@{0,20}\b(?:about|when)\b@{0,20}\b(?:age|name|who i am|"
        r"where i live|myself)\b",
        r"\bi'?m (?:actually|really) (?:\d{2}|older|a (?:guy|girl|man|woman|boy))\b",
        r"\bmy (?:real|actual) (?:name|age)\b",
    )),

    # ---------------- story (counts only with a money/payment request) ----------------
    _Rule(L_STORY, _STORY, _c(
        r"\b(?:dad|mom|mum|father|mother|parents?|brother|sister|grand(?:ma|pa|mother|father)|son|"
        r"daughter|wife|husband|aunt|uncle)\b@{0,20}\b(?:is|got|get|gets|was|are|has)\b@{0,15}\b"
        r"(?:sick|ill|in (?:the )?hospital|dying|arrested|in trouble|injured|in an accident|in jail)\b",
        r"\b(?:lose|losing|lost) my (?:apartment|house|home|job|place|flat)\b",
        r"\b(?:evict(?:ed|ion)|can'?t pay|hospital bills?|medical bills?|surgery|funeral|rent is due|bills are)\b",
        r"\b(?:bank|account|card)\b@{0,12}\b(?:frozen|locked|blocked|suspended)\b",
        r"\b(?:stuck|stranded)\b@{0,20}\b(?:airport|abroad|overseas|border|customs|country)\b",
        r"\bemergency\b",
    )),
]

# Signs that lower concern. Never applied when a critical signal is present.
_MITIGATORS: list = [
    (M_VERIFY, 2, _c(
        r"\b(?:call|text|talk to|ask|check with)\b@{0,15}\b(?:my|his|her) (?:mom|mum|dad|parents?|"
        r"brother|sister|teacher|friend|family)\b",
        r"\bi can (?:send|give) you (?:my|his|her)\b@{0,15}\b(?:number|mom|mum|dad|parents?)\b",
        r"\b(?:sure|ok|okay|yes|of course)\b@{0,15}\b(?:video|voice) ?call\b",
        r"\b(?:video|voice|phone) ?call\b@{0,20}\b(?:sure|ok|okay|yes|tonight|tomorrow|anytime)\b",
        r"\byou can (?:call|verify|check|ask)\b",
    )),
    (M_NOPRESS, 1, _c(
        r"\bno (?:pressure|worries|problem|rush|stress)\b",
        r"\b(?:totally|completely) fine\b",
        r"\bonly if you want\b",
        r"\bwhatever you prefer\b",
        r"\bi'?ll figure it out\b",
        r"\bdon'?t feel (?:bad|pressured|obligated)\b",
    )),
]


# ---------------------------------------------------------------------------
# Text preparation
# ---------------------------------------------------------------------------

_CURLY = str.maketrans({
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"', "\u00a0": " ",
})
_USER_LABELS = {"you", "me", "user", "myself", "i", "human"}
_SPEAKER = re.compile(r"^([A-Za-z][\w .'\-]{0,24}?)\s*:\s*(.+)$")


def _normalize(text: str) -> str:
    """Fix phone-style quotes so patterns like don't match don't."""
    return re.sub(r"[ \t]+", " ", text.translate(_CURLY)).strip()


def _split_lines(text: str) -> list:
    """Return the other person's lines. Lines labelled 'You:' are dropped so
    the user's own words are never counted as warning signs."""
    lines = []
    for raw in re.split(r"[\r\n]+", text):
        raw = raw.strip()
        if not raw:
            continue
        m = _SPEAKER.match(raw)
        if m:
            if m.group(1).strip().lower() in _USER_LABELS:
                continue
            raw = m.group(2).strip()
        if raw:
            lines.append(raw)
    return lines


# ---------------------------------------------------------------------------
# Relationship context
# ---------------------------------------------------------------------------

_NUM_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "few": 3, "couple": 2, "couple of": 2, "several": 4,
}
_UNIT_DAYS = {"hour": 1 / 24, "day": 1, "week": 7, "month": 30, "year": 365}
_DURATION = re.compile(
    r"\b(\d+|an?|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|few|"
    r"couple(?: of)?|several)\s+(hour|day|week|month|year)s?\b", re.IGNORECASE)
_JUST_MET = re.compile(r"\b(?:yesterday|just met|just started|brand new)\b", re.IGNORECASE)
_NEVER_MET = re.compile(
    r"\b(?:never|haven'?t|have not|not yet)\b@{0,15}\b(?:met|seen|video ?called|called)\b|"
    r"\bonly (?:talk|talked|chat|chatted|speak|spoke|play|played|know each other|met)\b@{0,15}\bonline\b|"
    r"\bonline only\b|\bnever met in person\b".replace("@", _GAP), re.IGNORECASE)


def _known_days(text: str) -> Optional[float]:
    best = None
    for m in _DURATION.finditer(text):
        raw = m.group(1).lower()
        n = int(raw) if raw.isdigit() else _NUM_WORDS.get(raw, 1)
        days = n * _UNIT_DAYS[m.group(2).lower()]
        best = days if best is None else max(best, days)
    if best is None and _JUST_MET.search(text):
        best = 1
    return best


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _rule_hits(rule: _Rule, line: str) -> bool:
    for pat in rule.patterns:
        m = pat.search(line)
        if not m:
            continue
        if rule.skip_if is not None and rule.skip_if.search(line):
            continue
        if rule.guard_negation and _NEGATION.search(line[max(0, m.start() - 25):m.start()]):
            continue
        return True
    return False


def _scan(lines: list, new_contact: bool) -> dict:
    """label -> (tier, line_index, quote) for the first line that matches."""
    found: dict = {}
    for i, line in enumerate(lines):
        for rule in _RULES:
            if rule.label in found:
                continue
            if rule.new_contact_only and not new_contact:
                continue
            if _rule_hits(rule, line):
                found[rule.label] = (rule.tier, i, line[:140])
    return found


def _mitigation(lines: list) -> tuple:
    labels, points = [], 0
    for label, weight, patterns in _MITIGATORS:
        if any(p.search(line) for line in lines for p in patterns):
            labels.append(label)
            points += weight
    return labels, min(points, 3)


def _assess(message_text: str, context: Optional[str] = None) -> dict:
    text = _normalize(message_text or "")
    ctx = _normalize(context or "")
    limitations = (
        "Rule-based keyword check. It can miss paraphrased or subtle manipulation. "
        "Treat it as evidence, not a final verdict."
    )

    lines = _split_lines(text) if re.search(r"[A-Za-z]{3}", text) else []
    if not lines:
        return {
            "risk_level": "no_content", "score": 0, "signals": [], "signal_details": [],
            "reassuring_signs": [], "change_over_time": "none", "relationship_notes": [],
            "missing_info": "Can you paste the other person's messages?",
            "confidence": "low", "limitations": limitations, "signal_count": 0,
            "analyzed_text_length": len(text),
        }

    rel_text = f"{ctx}\n{text}"
    days = _known_days(rel_text)
    new_contact = days is not None and days <= 30
    never_met = bool(_NEVER_MET.search(rel_text))

    found = _scan(lines, new_contact)

    # An emergency story alone is not a warning sign. It only matters when
    # money or a payment is also being requested.
    if L_STORY in found and not any(l in found for l in _FINANCIAL):
        del found[L_STORY]

    critical = [l for l, (tier, _, _) in found.items() if tier == _CRITICAL]
    raw = sum(_POINTS.get(tier, 0) for tier, _, _ in found.values())
    mit_labels, mit_points = _mitigation(lines)

    if not found:
        level, adjusted = "low", 0
    elif critical:
        level, adjusted = "high", raw
    else:
        adjusted = max(raw - mit_points, 1)
        level = "high" if adjusted >= 3 else "medium"

    # Change over time (needs a real chat)
    change = "none"
    if found and len(lines) >= 4:
        first = min(idx for _, idx, _ in found.values())
        if first >= 1:
            change = (f"The first warning sign appears in message {first + 1} of {len(lines)}. "
                      "Earlier messages had none.")

    notes = []
    if never_met:
        notes.append("The user has not met this person in person.")
    if days is not None:
        notes.append(f"Known for about {int(round(days))} day(s)." if days >= 1
                     else "Known for less than a day.")

    # One useful follow-up question
    if found and never_met and L_VERIFY not in found and M_VERIFY not in mit_labels:
        missing = "Has this person ever agreed to a voice or video call with you?"
    elif found and days is None:
        missing = "How long have you known this person?"
    else:
        missing = "none"

    letters = len(re.findall(r"[A-Za-z]", text))
    if letters < 25:
        confidence = "low"
    elif not found:
        confidence = "medium"
    elif critical or adjusted >= 4:
        confidence = "high"
    else:
        confidence = "medium"

    order = {_CRITICAL: 0, _STRONG: 1, _STORY: 1, _MINOR: 2}
    details = sorted(
        ({"signal": l, "strength": t, "quote": q, "message_number": i + 1}
         for l, (t, i, q) in found.items()),
        key=lambda d: order[d["strength"]],
    )

    return {
        "risk_level": level,
        "score": adjusted,
        "signals": [d["signal"] for d in details],
        "signal_details": details,
        "reassuring_signs": mit_labels,
        "change_over_time": change,
        "relationship_notes": notes,
        "missing_info": missing,
        "confidence": confidence,
        "limitations": limitations,
        "signal_count": len(details),
        "analyzed_text_length": len(text),
    }


# ---------------------------------------------------------------------------
# Public ADK tool
# ---------------------------------------------------------------------------

@tool
def score_risk(message_text: str, context: Optional[str] = None) -> dict:
    """
    Check a message, chat, profile or described situation for online safety
    warning signs such as scams, grooming, sextortion, manipulation, pressure
    for money, photos, passwords or secrecy.

    Paste the other person's messages as they were written. Lines that start
    with "You:" are ignored so the user's own words are not counted.

    Args:
        message_text: The exact messages or the situation described by the user.
                      Required.
        context: Optional background, for example the platform, how long the
                 user has known the person, and whether they have met in person.

    Returns:
        A dict with:
        - risk_level (str): "low", "medium", "high", or "no_content"
        - score (int): points after reassuring signs are applied
        - signals (list[str]): warning signs found, strongest first
        - signal_details (list[dict]): signal, strength, exact quote, message number
        - reassuring_signs (list[str]): signs that lower concern
        - change_over_time (str): when warning signs first appeared, or "none"
        - relationship_notes (list[str]): facts from the context
        - missing_info (str): one useful follow-up question, or "none"
        - confidence (str): "low", "medium", or "high"
        - limitations (str): reminder that this is a rule-based check
        - signal_count (int): number of signals found
        - analyzed_text_length (int): characters analyzed
    """
    return _assess(message_text, context)