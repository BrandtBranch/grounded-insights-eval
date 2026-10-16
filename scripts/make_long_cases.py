"""Build data/cases_long.json: longer variants of the base cases, plus long empty transcripts.

The planted "core" interview is kept intact and surrounded by filler exchanges that carry no
insight about the core topic. Deterministic: the same ids always give the same transcripts.

    python scripts/make_long_cases.py
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from insights_eval.models import load_cases
from insights_eval.text import INTERVIEWER_LABELS, _TURN

ROOT = Path(__file__).resolve().parent.parent
BASES = ["retail_stockouts", "hospital_theatres", "saas_churn", "bank_compliance", "plant_changeovers"]
VARIANTS = [
    ("medium", "middle", 700), ("medium", "interleaved", 700),
    ("long", "start", 2000), ("long", "middle", 2000), ("long", "end", 2000), ("long", "interleaved", 2000),
]
EMPTY_TARGETS = [("empty_medium", 600), ("empty_long", 1000)]

# Pleasantries and logistics. No content about the business.
SMALLTALK = [
    ("Before we go on, are you happy for me to keep recording?", "Yes, that's fine, go ahead. I've done a few of these before, so I know roughly how it goes."),
    ("Can I get you some water or a coffee before we continue?", "A coffee would be great, thank you. Just milk, no sugar, and there's no hurry at all."),
    ("Sorry, could you repeat that last part? I missed the end of it.", "Of course. It was a long answer, so don't worry if it rambled a little, I do that sometimes."),
    ("I know it's a busy week, so I really appreciate you making the time.", "No problem at all. I moved a meeting to make room, and honestly it's a nice break from my desk."),
    ("Did you have any trouble finding the room this morning?", "None at all. The reception staff pointed me over, and the signs were pretty clear once I was on the right floor."),
    ("Is it alright if we take a short break soon?", "Sure, whenever suits you. I'm happy to carry on for a while longer if you want to get through a few more questions."),
    ("Just give me a second to check my notes.", "Take your time. I'm in no rush, and I've blocked out the whole morning for this anyway."),
    ("Would you like me to send you a summary of what we discussed afterwards?", "That would be good, yes. Just send it to my work address, and I'll look it over when I have a quiet moment."),
    ("Can you hear me properly? The speaker in this room sometimes crackles.", "I can hear you fine. It crackled a little at the start, but it seems to have settled down now."),
    ("How has your week been so far?", "Busy, but nothing out of the ordinary. Monday was the worst of it, and things have been calmer since then."),
    ("Did you travel in this morning?", "I came by train, and for once it was on time. The carriage was full, but I managed to find a seat by the window."),
    ("Is this still a good time, or are you expecting a call?", "It's fine, I've put my phone on silent. If anything urgent comes up my assistant knows where to find me."),
    ("Let me know if I start running over the time we agreed.", "We have until the top of the hour, so we're fine. After that I do have another commitment, but it's a short walk."),
    ("Do you mind if I ask a couple of background questions first?", "Not at all, ask whatever you need. I'd rather you had the full picture than guessed at the parts I left out."),
    ("I'll keep this fairly informal, so just say if something isn't clear.", "That sounds good to me. I tend to answer more naturally when it feels like a conversation rather than a formal interview."),
    ("Thanks, that's really helpful to hear.", "Happy to help. Let me know if any of it needs more detail, and I can think about it and get back to you."),
    ("Sorry, I lost my place in my notes for a moment.", "No worries at all, I do exactly that in my own meetings. Take as long as you need to find it again."),
    ("Is it all right if I come back to that point a bit later?", "Of course, that's fine. Just remind me if I forget, because I do tend to lose track when the conversation moves on."),
    ("I'll move on to the next topic, if that works for you.", "Go ahead. I'm happy to follow wherever you want to take it, so just steer the conversation as you see fit."),
    ("Could you spell that name for my notes, please?", "Sure, it's the usual spelling, nothing unusual. I'll write it down for you if that's easier than saying it out loud."),
    ("Is the heating always this warm in here?", "Pretty much, yes. It's a running joke in the building, and half the people on this floor keep a small fan at their desk."),
    ("It's raining quite hard outside now, isn't it?", "It has been since early this morning. I got a bit wet on the walk over, but my coat is drying on the hook by the door."),
    ("I'll try not to keep you much longer than planned.", "No rush from my side. I'd much rather we cover things properly than cut the conversation short because of the clock."),
    ("Let me just make sure I've understood you correctly.", "Please do. It's better to check now than to find out later that we were each thinking about something slightly different."),
    ("Are there any questions you'd like to ask me before we continue?", "Not right now, though I might have one or two at the end once I've had a chance to think about the whole conversation."),
    ("Sorry, the call dropped on my end for a second there.", "It was fine here, nothing missed. If it does drop again just give me a moment and I'll wait until you're back."),
    ("Thanks for bearing with all the questions so far.", "That's what I'm here for. It's actually useful for me too, since it makes me say things out loud that I rarely get to."),
    ("Could I ask you to speak up a little? The recorder is across the table.", "Certainly. I tend to trail off at the end of sentences, so do stop me if I become hard to hear on the recording."),
]

# Irrelevant organisational facts. They can tempt an extractor, but have nothing to do with the core topics.
DISTRACTORS = [
    ("Tell me a little about the wider organisation.", "We're a few hundred people spread over three sites. The head office is the largest, and the other two are mostly small teams who've been with us for years."),
    ("What's the culture like day to day?", "Friendly, I'd say. We have a lunch-and-learn series on the first Thursday of every month, and attendance is surprisingly good considering it's over lunchtime."),
    ("Has the office changed much recently?", "We moved floors a couple of years ago to make room for a new team. The new layout is brighter, though the meeting rooms are still in short supply on Tuesdays."),
    ("Who else should I be talking to while I'm here?", "You could try the new finance lead, who joined in the spring. She's settled in quickly and has been a great addition, but I couldn't tell you much about her area."),
    ("Is there anything people complain about that I should know of?", "Parking, mostly. It's been tight ever since the car park was resurfaced and the number of bays went down by a handful, and people get quite passionate about it."),
    ("How do people usually communicate internally?", "We relaunched the intranet in January. People mostly use it for the canteen menu and the staff directory, and the newsletter goes out every other Friday."),
    ("Does the company do much outside the core business?", "We sponsor a local charity run every autumn. About forty colleagues take part, and it's become a bit of a tradition, with a small prize for the best fancy dress."),
    ("What about travel? Do people get out much?", "We changed our booking tool last year, and the new one is much simpler. It cut the number of emails about hotels down considerably, which the assistants were pleased about."),
    ("Was there a company event this year?", "Yes, the annual offsite was in the countryside. The weather was lovely, and the walk on the second morning turned out to be the part everybody remembered afterwards."),
    ("How are the facilities?", "The canteen introduced a vegetarian day on Wednesdays, which went down better than expected. The coffee machine on the third floor still breaks every few weeks, though."),
    ("Do you have any teams based elsewhere?", "A small team in Lisbon handles our invoicing. I've only met them twice, but they sent a lovely card when we hit one of our anniversaries last year."),
    ("How long have you been with the company?", "Just over nine years now. I started in a different role and moved across when the department was reorganised, which seems like a very long time ago."),
    ("Is the building leased or owned?", "Leased. The lease was renewed for another five years last winter, and there was a short debate about whether to move, but in the end everyone was happy to stay."),
    ("What's the commute like for most people?", "Most people come by train or bike. We added secure bike storage last summer, and it filled up within a month, so there's now a waiting list for a space."),
    ("Does the company run any training programmes?", "There's an induction week for new starters with a tour of all the sites. It's popular, although I think people mainly enjoy the free lunch on the last day."),
    ("Any traditions I should know about?", "We have a quiz night every December, with teams drawn from different floors. The reception team won it three years in a row, and nobody has quite forgiven them."),
    ("How do you keep in touch with people on other sites?", "A monthly video call, mostly. It's more social than anything, with a rotating host who picks a theme, and last month's was baking, which went about as well as you'd imagine."),
    ("Has the company changed its branding recently?", "We refreshed the logo two summers ago. It was a modest change, mostly the colours, and the printed stationery took longer to get replaced than anyone expected."),
    ("Is there much staff turnover on the administrative side?", "Not really, no. The reception team has been the same for years, and one of them is about to celebrate twenty years with the company, so there's a cake being planned."),
    ("What do people do for lunch?", "A mix of the canteen and the small cafe across the road. The cafe does a very good soup, and some people have their own table there on Fridays."),
    ("Do you get many visitors to the office?", "A fair number. We have a visitor badge system that was updated last year, and the lobby has a screen that shows the names of people who are expected that day."),
    ("How is the IT equipment generally?", "Laptops get replaced every four years or so. The latest batch arrived in the autumn and people were pleased with the screens, though the chargers are a different story."),
    ("Does the company have a sustainability policy?", "We have a modest one. There's a recycling scheme on each floor, and last year we switched to a green electricity supplier, which was announced at an all-hands meeting."),
    ("What's the company known for in the local area?", "Mostly as a good employer. People tend to stay a long time, and we get a lot of speculative applications, which the recruitment team find both flattering and exhausting."),
    ("Is there anything you'd like to show me on the tour?", "The roof terrace, if the weather holds. It was added two years ago and is the best spot in the building, though it closes the moment it gets properly cold."),
    ("What do you do when you're not working?", "I play in a small amateur orchestra, which takes up most evenings. We have a concert coming up in a few weeks, and I'm still practising the hardest passage."),
    ("How do you usually spend the summer break?", "Usually a week by the coast with the family. Last year the weather was dreadful, but the children didn't mind, and we spent most of the time in the arcade."),
    ("Does the team ever get together outside work?", "Every so often. There's a Friday drinks tradition that started during the lockdowns and has carried on, and it's usually the same dozen people who turn up."),
    ("Do you have a favourite part of the building?", "The old library on the second floor. They kept the shelves when the offices were redone, and it's the quietest room we have, so it's always the first to be booked."),
    ("What was the company like when you joined?", "Smaller and a bit scruffier. We had about half the staff and shared desks in a cramped open room, but there was a lot of goodwill and everyone knew everyone."),
]

# Corporate filler with no concrete content, used for the long empty transcripts.
BUZZWORDS = [
    ("What would you say your top priority is?", "Transformation, really. Leveraging synergies across the organisation and driving value for all of our stakeholders."),
    ("Can you say more about that?", "Sure. It's about being agile and customer-centric, and aligning around our strategic priorities as one team."),
    ("Where do you see the organisation in three years?", "In a great place. We're on a journey and there's a lot of energy, which is wonderful to see."),
    ("What gets in the way?", "Silos, mostly, and the usual complexity. But we're working on breaking them down together."),
    ("Any specific example?", "I'd rather not single anything out. It's really a mindset thing, and culture eats strategy for breakfast."),
    ("How would you describe the culture?", "Collaborative, ambitious and people-first. People really care here, which is our greatest asset."),
    ("What does success look like?", "Delighted customers, engaged employees and sustainable growth. That's the north star we keep coming back to."),
    ("What would you change?", "Honestly, I think we're heading in the right direction. It's about continuing the momentum and staying focused."),
    ("Is there anything you'd like to add?", "Only that I'm optimistic. There's a lot to be proud of and a lot still to do, as always."),
    ("Thanks, that's very clear.", "Great. Happy to elaborate any time, we're always open to dialogue."),
]

# Chatty complaints that sound like findings but have nothing to do with the core topics.
OPINIONS = [
    ("How do you find the new office layout?", "Honestly, a bit grim. The lighting on the fourth floor gives me a headache and I think most people would say the same if you asked them."),
    ("What do you make of the coffee here?", "Terrible, if I'm honest. It's the thing I complain about most, and I've started bringing my own flask in."),
    ("Is there anything about the building you'd change?", "The lifts, definitely. They are always breaking down, and I have walked up seven flights more times than I'd like to admit."),
    ("How's the wifi in the meeting rooms?", "Hopeless, to be frank. It cuts out in the middle of calls, and I've given up trying to share my screen on the second floor."),
    ("Do you use the intranet much?", "As little as possible. The search is useless, and I always end up asking a colleague where something is instead."),
    ("What do you think of the Monday all-staff emails?", "A bit much, honestly. They're far too long and I tend to skim them over a coffee and forget everything by lunchtime."),
    ("How's the canteen these days?", "Overpriced, I'd say. The food is fine but a sandwich costs more than it does across the road, and I don't think that's right."),
    ("Is the commute a problem for you?", "It's the worst part of my day. The trains are crowded and the delays are constant, and I seriously considered moving closer last year."),
    ("Do you like the open-plan layout?", "Not really, no. It's noisy and there's nowhere to take a private call, so I end up in the stairwell more often than not."),
    ("Any thoughts on the new lanyards?", "Pointless, if you ask me. They keep getting caught on chairs, and I can't see who they were meant to help."),
    ("How do you find the printers?", "Dreadful. They jam constantly, and nobody ever replaces the paper, so I've more or less stopped printing anything at all."),
]

# Short interruptions appended to an answer in the interleaved layout.
ASIDES = [
    "Sorry, my phone just buzzed.",
    "Hang on, someone is waving at me through the glass.",
    "Sorry, where was I?",
    "Excuse me, I need to clear my throat.",
    "Sorry, that came out more complicated than I meant.",
    "Anyway, I've lost my train of thought for a second.",
]


def _words(pairs: list[tuple[str, str]]) -> int:
    return sum(len(q.split()) + len(a.split()) for q, a in pairs)


def _render(pairs: list[tuple[str, str]], label: str) -> str:
    return "\n".join(f"Interviewer: {q}\n{label}: {a}" for q, a in pairs)


def _interviewee_label(transcript: str) -> str:
    for line in transcript.splitlines():
        m = _TURN.match(line)
        if m and m.group(1).strip().lower() not in INTERVIEWER_LABELS:
            return m.group(1).strip()
    raise ValueError("no interviewee label found")


def _take(pool: list[tuple[str, str]], target_words: int, rng: random.Random) -> list[tuple[str, str]]:
    shuffled = pool[:]
    rng.shuffle(shuffled)
    taken: list[tuple[str, str]] = []
    for pair in shuffled:
        if _words(taken) >= target_words:
            break
        taken.append(pair)
    if _words(taken) < target_words:
        raise ValueError(f"filler pool too small: {_words(taken)} < {target_words} words")
    return taken


def _exchanges(transcript: str) -> list[list[str]]:
    """Group lines into exchanges, each starting at an interviewer line."""
    groups: list[list[str]] = []
    for line in transcript.splitlines():
        m = _TURN.match(line)
        if m and m.group(1).strip().lower() in INTERVIEWER_LABELS or not groups:
            groups.append([])
        groups[-1].append(line)
    return groups


def _interleave(base_transcript: str, pairs: list[tuple[str, str]], label: str, rng: random.Random) -> str:
    """Spread filler exchanges between the core's exchanges and sometimes append a short aside to an answer.

    Asides go at the end of a turn so every planted evidence span stays intact.
    """
    exchanges = _exchanges(base_transcript)
    for ex in exchanges:
        if len(ex) > 1 and rng.random() < 0.5:
            ex[-1] = f"{ex[-1]} {rng.choice(ASIDES)}"
    gaps = [[] for _ in range(len(exchanges) + 1)]
    for pair in pairs:
        gaps[rng.randrange(len(gaps))].append(pair)
    out: list[str] = []
    for i, gap in enumerate(gaps):
        if gap:
            out.append(_render(gap, label))
        if i < len(exchanges):
            out.append("\n".join(exchanges[i]))
    return "\n".join(out)


def padded_case(base, length: str, position: str, target: int) -> dict:
    rng = random.Random(f"{base.id}-{length}-{position}")
    label = _interviewee_label(base.transcript)
    pairs = _take(SMALLTALK + DISTRACTORS + OPINIONS, target - base.words, rng)
    if position == "interleaved":
        transcript = _interleave(base.transcript, pairs, label, rng)
    else:
        if position == "start":
            before, after = [], pairs
        elif position == "end":
            before, after = pairs, []
        else:
            half = len(pairs) // 2
            before, after = pairs[:half], pairs[half:]
        parts = [p for p in (_render(before, label) if before else "", base.transcript, _render(after, label) if after else "") if p]
        transcript = "\n".join(parts)
    return {
        "id": f"{base.id}__{length}_{position}",
        "title": f"{base.title} ({length}, {position})",
        "kind": "padded",
        "group": base.id,
        "position": position,
        "expect_none": False,
        "transcript": transcript,
        "planted": [p.model_dump() for p in base.planted],
        "distractors": [answer for _, answer in pairs],
    }


def empty_case(case_id: str, target: int) -> dict:
    rng = random.Random(case_id)
    pairs = _take(SMALLTALK + BUZZWORDS, target, rng)
    return {
        "id": case_id,
        "title": f"Small talk and buzzwords, no insight (~{target} words)",
        "kind": "empty_long",
        "expect_none": True,
        "transcript": _render(pairs, "Director"),
        "planted": [],
    }


def main() -> None:
    bases = {c.id: c for c in load_cases(ROOT / "data" / "cases.json")}
    out = [padded_case(bases[b], length, position, target) for b in BASES for length, position, target in VARIANTS]
    out += [empty_case(cid, target) for cid, target in EMPTY_TARGETS]
    path = ROOT / "data" / "cases_long.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for c in out:
        print(f"{c['id']:<45} {len(c['transcript'].split()):>5} words")


if __name__ == "__main__":
    main()
