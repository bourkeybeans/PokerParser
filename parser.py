import re
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Precompiled regex patterns
HEADER_RE = re.compile(
    r"PokerStars Hand #(?P<hand_id>\d+):.* - (?P<datetime>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ET"
)
SEAT_RE = re.compile(r"Seat (?P<seat>\d+): (?P<name>.+) \(\$(?P<stack>[\d\.]+) in chips\)")
ACTION_RE = re.compile(
    r"^(?P<player>[^:]+): (?P<action>posts small blind|posts big blind|calls|raises|bets|checks|folds|shows|mucks|collected)(?: \$?(?P<amount>[\d\.]+))?"
)


def split_into_blocks(raw_text: str) -> List[str]:
    """Break a hand history file into individual hands."""
    blocks, current = [], []
    for line in raw_text.splitlines():
        if line.startswith("PokerStars Hand #") and current:
            blocks.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def parse_hand(raw_text: str) -> Dict[str, Any]:
    """Parse one hand into structured dict."""
    hand = {"id": None, "datetime": None, "players": [], "actions": []}
    errors: List[str] = []

    try:
        # Header
        header = HEADER_RE.search(raw_text)
        if header:
            hand["id"] = int(header.group("hand_id"))
            hand["datetime"] = datetime.strptime(header.group("datetime"), "%Y/%m/%d %H:%M:%S")
        else:
            errors.append("Missing header")

        # Players
        for m in SEAT_RE.finditer(raw_text):
            hand["players"].append(
                {"seat": int(m.group("seat")), "name": m.group("name"), "stack_start": float(m.group("stack"))}
            )

        # Actions
        for line in raw_text.splitlines():
            m = ACTION_RE.match(line.strip())
            if m:
                hand["actions"].append(
                    {
                        "player": m.group("player"),
                        "action": m.group("action"),
                        "amount": float(m.group("amount")) if m.group("amount") else None,
                    }
                )
    except Exception as e:
        errors.append(str(e))

    return {"hand": hand, "errors": errors}


def parse_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse an entire hand history file."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    return [parse_hand(block) for block in split_into_blocks(raw_text)]


def main():
    parser = argparse.ArgumentParser(description="PokerStars hand history parser")
    parser.add_argument("input", help="Input hand history file")
    parser.add_argument("--json", help="Write parsed output to JSON")
    args = parser.parse_args()

    hands = parse_file(args.input)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(hands, f, indent=2, default=str)
        print(f"Parsed {len(hands)} hands → saved to {args.json}")
    else:
        print(json.dumps(hands, indent=2, default=str))


if __name__ == "__main__":
    main()

