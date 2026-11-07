# Demo Script — Online Safety Companion

**Format:** 3-minute video
**Presenter:** [Your name]
**Project:** Online Safety Companion — IBM watsonx Orchestrate Hackathon

---

## Overview

| Segment | Time | Content |
|---|---|---|
| Problem | 0:00 – 0:40 | Who Ralph is; why this matters |
| Live demo | 0:40 – 2:40 | Three live conversations |
| Impact | 2:40 – 3:00 | What changes; what's next |

---

## 0:00 – 0:40 | The Problem (40 seconds)

**[On screen: plain slide — "Ralph is 18. He met someone online."]**

> "Meet Ralph. He's 18, neurodivergent, and he met someone in an online game.
> The person is friendly — really friendly. They want to move the conversation
> to Telegram, and they said not to tell his parents.
>
> Ralph isn't sure if something is wrong. He doesn't want to make a fuss.
> He doesn't want to get anyone in trouble.
>
> Existing tools aren't built for Ralph. The language is too abstract. The
> advice tells him what he 'should' do. And he's worried he'll be blamed.
>
> We built Online Safety Companion — a multi-agent assistant on IBM watsonx
> Orchestrate — so Ralph can get a calm, clear answer in plain English,
> without judgment, in under a minute."

---

## 0:40 – 2:40 | Live Demo (120 seconds)

**[Switch to screen share: watsonx Orchestrate chat window open]**

---

### Demo 1 — High-risk: Platform migration + secrecy (0:40 – 1:20)

**[Type as Ralph]**

> Ralph types:
> *"Hi. I met someone on Discord and they've been really nice.
> Today they said: 'Add me on Telegram, it's more private,
> and don't tell your parents — they wouldn't understand.'
> Is this okay?"*

**[Pause 3 seconds — agent responds]**

> "The agent greeted Ralph, noticed he already gave full context, and went
> straight to work — no redundant questions.
> It called the Safety Agent, which detected three signals: platform migration
> pressure, secrecy from family, and love-bombing.
> The Support Agent translated that into two options.
> The final reply is short, plain, and ends with 'The choice is yours.' —
> Ralph makes the call."

**[Point to the on-screen reply — highlight the warning signs and options]**

---

### Demo 2 — Sextortion (1:20 – 1:55)

**[Type as Ralph]**

> Ralph types:
> *"Someone is threatening me. They said:
> 'I have your pictures. Send me $200 in Bitcoin by tomorrow
> or I'll send them to everyone.'"*

**[Pause 3 seconds — agent responds]**

> "This time the agent opens with: 'This was not your fault.'
> It still runs the full analysis — sextortion signal, money request, fake urgency —
> all detected as HIGH risk.
> The reply includes: stop replying, keep the evidence, screenshot,
> the NCMEC CyberTipline, the Canadian Centre for Child Protection, and the 988
> crisis line.
> And it still ends with 'The choice is yours.' — because Ralph is in control."

---

### Demo 3 — Benign chat (LOW) (1:55 – 2:20)

**[Type as Ralph]**

> Ralph types:
> *"Someone from my gaming server said:
> 'GG! Do you play ranked? What's your favourite map?'
> Is this okay?"*

**[Pause 3 seconds — agent responds]**

> "No signals. Risk level: LOW.
> The agent reassures Ralph this looks like a normal friendly conversation —
> and still gently reminds him it's good to stay alert over time.
> No alarm. No drama. Just a calm, honest answer."

---

### Architecture callout (2:20 – 2:40)

**[Switch to architecture diagram from README]**

> "Three agents, one tool, three knowledge documents.
> The orchestrator gathers context. The Safety Agent scores risk.
> The Support Agent explains it. The orchestrator writes one clear reply.
> Built entirely on IBM watsonx Orchestrate using the native ADK —
> with IBM granite-3-3-8b-instruct as the model for all three agents."

---

## 2:40 – 3:00 | Impact and Close (20 seconds)

**[Back to plain slide: "The choice is yours."]**

> "Ralph gets an answer in under 60 seconds. In plain English. Without blame.
> With real options and real resources.
>
> The knowledge base and signal rules are easy to update as new patterns emerge.
> The same architecture could support other vulnerable groups: older adults
> targeted by scams, teenagers on social media, anyone who just isn't sure.
>
> Online Safety Companion. Built with IBM watsonx Orchestrate and IBM Bob.
> Thank you."

---

## Production notes

- Use a clean browser window with no personal bookmarks visible.
- Pre-type the messages in a text file and paste them — avoids typos live.
- Demo conversations should be tested end-to-end at least twice before recording.
- Captions recommended for accessibility.
- Total runtime target: 2 minutes 55 seconds to 3 minutes 00 seconds.
