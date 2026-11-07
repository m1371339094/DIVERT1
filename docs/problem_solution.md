# Problem and Solution

**Project:** Online Safety Companion
**Track:** IBM watsonx Orchestrate hackathon
**Word count:** ~480

---

## The Problem

Young people aged 18–19 who are neurodivergent — including those with autism,
ADHD, or other conditions — face a significantly elevated risk of online harm.
Predators, romance scammers, and sextortion actors actively target this group
because social cues that signal manipulation are harder to read, and trust can
be established more quickly.

The harms are serious and well-documented: financial loss from gift-card and
cryptocurrency scams, emotional damage from romance fraud, and lasting
psychological harm from grooming and sextortion. Existing online safety tools
are designed for a general adult audience. Their language is abstract, their
advice is non-specific, and they frequently place the burden of action on the
person who was targeted — creating shame and discouraging disclosure.

Young people rarely tell anyone. They worry about being blamed, having their
phone taken away, or getting the other person in trouble. This silence allows
harm to escalate.

---

## The Solution

**Online Safety Companion** is a conversational AI assistant built on
IBM watsonx Orchestrate. It is designed for a user persona called "Ralph":
an 18-year-old neurodivergent young adult who has met someone online and
wants to check whether the situation is safe.

The assistant:

- **Meets the user where they are.** It communicates in short, plain sentences
  with no idioms or sarcasm. It never blames the user. It explicitly tells
  them: "You are not in trouble."

- **Gathers information without overwhelm.** It asks one question at a time
  and never repeats a question the user already answered. It waits until the
  user shares real content (a message, a profile, a request) before running
  any analysis.

- **Uses structured multi-agent analysis.** A dedicated Safety Agent applies a
  rule-based risk scorer and cross-references a curated knowledge base covering
  grooming, scams, sextortion, and platform-migration pressure. A Support Agent
  then translates the result into plain language and generates 2–3 concrete
  options the user can choose from.

- **Never makes the decision.** Every response ends with "The choice is yours."
  The assistant respects the user's autonomy.

- **Escalates appropriately.** When photos, money transfers, threats, or
  in-person meeting requests are detected, the assistant provides immediate
  resources: NCMEC CyberTipline, cybertip.ca, the 988 crisis line.

---

## Impact

A neurodivergent young adult who suspects something is wrong can open a chat,
paste a message, and receive a calm, clear, non-judgmental assessment within
seconds. They are given real options and draft wording to start a conversation
with a trusted adult if they choose to. The barrier to getting help drops
significantly.

The architecture is also extensible: the knowledge base, signal rules, and
agent instructions can be updated as new patterns emerge — without redeploying
the core infrastructure.
