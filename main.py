"""One-Star Review of Something Essential.

Scores a shortlist of original deadpan one-star reviews against the five
criteria the make.fun judge publishes, and writes the winning line to
/output/entry.txt (or $OUTPUT_PATH when set, for local runs).

The judge's criteria, most important first:
  1. A one-star review of an everyday essential, deadpan and unmistakably
     about the thing itself.
  2. The sharpest true grievance: the small daily annoyance everyone
     recognises but has never seen written down.
  3. Holds the deadpan: one star, no winking, no explaining the joke, no
     exclamation marks doing the work.
  4. Turns in the last few words, so the sting arrives after the complaint
     has been read straight. A turn scores 3 when it reframes the subject
     in the last few words, 2 when it lands but only labels it, 1 when it
     is a single flat word.
  5. Tight and specific: one joke told cleanly, no filler, no second joke
     crowding the first.

Every candidate is a single line of at most 160 characters. The gate the
bounty seals is the same: /output/entry.txt must be UTF-8 text of 1 to 160
characters, not only white space.

Usage: python3 main.py
"""

import json
import os
import sys

MAX_CHARS = 160

# Each candidate carries the author's own scores against the judge's five
# criteria, with a one-line reason for each score. Scores are data, not
# decoration: the ranking below is computed from them.
CANDIDATES = [
    {
        "subject": "Monday",
        "text": (
            "Monday shows up on time every single week and has never once "
            "brought anything good with it. Punctual and useless."
        ),
        "scores": {
            # Monday is named in the bounty brief as an everyday essential.
            "essential": 2,
            # Everyone has felt it: Monday is the only thing that is never
            # late, and it never brings anything with it.
            "grievance": 3,
            # Flat statement of fact, no exclamation, no wink.
            "deadpan": 2,
            # "Punctual and useless" turns Monday's one virtue into the
            # charge itself: the turn reframes the subject.
            "turn": 3,
            # One joke: reliable, and reliably worthless.
            "tight": 1,
        },
        "why": "The turn is three words long and lands after a straight complaint.",
    },
    {
        "subject": "sleep",
        "text": (
            "Sleep takes eight hours a night and still sends me to work "
            "tired. Worst return on investment of my life."
        ),
        "scores": {
            "essential": 2,
            "grievance": 3,
            "deadpan": 2,
            # "Worst return on investment of my life" reframes sleep as a
            # bad investment, but it takes seven words to do it.
            "turn": 3,
            "tight": 1,
        },
        "why": "The most universal grievance of the shortlist, but the turn "
               "explains itself a little more than Monday's does.",
    },
    {
        "subject": "oxygen",
        "text": (
            "Oxygen is free, everywhere, and I still get winded walking up "
            "one flight of stairs. False advertising."
        ),
        "scores": {
            "essential": 2,
            "grievance": 3,
            "deadpan": 2,
            "turn": 2,
            "tight": 1,
        },
        "why": "Sharp and true, but the turn is a label rather than a "
               "reframing of the subject.",
    },
    {
        "subject": "sleep",
        "text": (
            "I give sleep eight hours every night and wake up owing it "
            "more. One star, terrible exchange rate."
        ),
        "scores": {
            "essential": 2,
            "grievance": 2,
            "deadpan": 2,
            "turn": 2,
            "tight": 1,
        },
        "why": "The setup is abstract: nobody literally owes sleep hours, "
               "so the grievance is softer than the tired-morning one.",
    },
    {
        "subject": "gravity",
        "text": (
            "Gravity never drops anything cheap. One star, it clearly has "
            "favourites."
        ),
        "scores": {
            "essential": 2,
            "grievance": 2,
            "deadpan": 2,
            "turn": 2,
            "tight": 1,
        },
        "why": "Witty, but the grievance is an observation, not a daily "
               "annoyance everyone has lived through.",
    },
    {
        "subject": "the sun",
        "text": (
            "The sun is late all winter, burns me in summer, and still gets "
            "a golden-hour photoshoot. Unprofessional."
        ),
        "scores": {
            "essential": 2,
            "grievance": 2,
            "deadpan": 2,
            "turn": 1,
            "tight": 0,
        },
        "why": "Two complaints in one line crowd each other, and the turn "
               "is a single flat word.",
    },
]

# The judge's order is the weight: criterion 1 matters most, then 2, and so
# on. Weights fall off so a win on an early criterion beats a win on a late
# one, the way the judge's brief says to decide.
WEIGHTS = {"essential": 8, "grievance": 4, "deadpan": 2, "turn": 1, "tight": 1}


def gate(text):
    """The sealed gate, restated: 1-160 chars, single line, not blank."""
    if not text or not text.strip():
        return "empty"
    if len(text) > MAX_CHARS:
        return "over %d characters" % MAX_CHARS
    if "\n" in text.strip():
        return "not a single line"
    if "!" in text:
        return "exclamation mark doing the work"
    return None


def total(candidate):
    return sum(
        candidate["scores"][key] * weight
        for key, weight in WEIGHTS.items()
    )


def turn_words(candidate):
    """How many words the turn takes: the sentence after the last full stop."""
    tail = candidate["text"].rsplit(". ", 1)[-1].rstrip(".")
    return len(tail.split())


def rank(candidates):
    """Best first. Ties break toward the shortest turn, then the shortest
    line: the sting should arrive late and leave nothing behind it."""
    def key(candidate):
        return (-total(candidate), turn_words(candidate), len(candidate["text"]))

    return sorted(candidates, key=key)


def main():
    for candidate in CANDIDATES:
        problem = gate(candidate["text"])
        if problem:
            print("reject %r: %s" % (candidate["text"][:40], problem),
                  file=sys.stderr)
            sys.exit(1)
        if candidate["subject"].lower() not in candidate["text"].lower():
            print("reject: review never names its subject", file=sys.stderr)
            sys.exit(1)

    ordered = rank(CANDIDATES)
    for place, candidate in enumerate(ordered, 1):
        print("%d. [%d pts, %d chars] %s -- %s" % (
            place, total(candidate), len(candidate["text"]),
            candidate["text"], candidate["why"]))

    winner = ordered[0]
    out_path = os.environ.get("OUTPUT_PATH", "/output/entry.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(winner["text"])
    print("winner: %s" % winner["text"])
    print("wrote %s (%d chars)" % (out_path, len(winner["text"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
