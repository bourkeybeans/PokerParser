import re
from datetime import datetime
from typing import List, Dict, Any, Tuple

# ----------------------------
# Regex patterns (precompiled)
# ----------------------------
HEADER_RE = re.compile(
    r"PokerStars Hand #(?P<hand_id>\d+):.* - (?P<datetime>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) ET"
)

SEAT_RE = re.compile(
    r"Seat (?P<seat>\d+): (?P<name>.+) \(\$(?P<stack>[\d\.]+) in chips\)"
)

ACTION_RE = re.compile(
    r"^(?P<player>[^:]+): (?P<action>posts small blind|posts big blind|calls|raises|bets|checks|folds|shows|mucks|collected)(?: \$?(?P<amount>[\d\.]+))?"
)

# ----------------------------
# Helpers
# ----------------------------

def split_into_blocks(raw_text: str) -> List[str]:
    """
    Split full hand history file into individual hand blocks.
    """
    blocks = []
    current = []
    for line in raw_text.splitlines():
        if line.startswith("PokerStars Hand #") and current:
            blocks.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def parse_hand(raw_text: str) -> Dict[str, Any]:
    """
    Parse a single hand into structured data.
    """
    hand = {
        "id": None,
        "datetime": None,
        "players": [],
        "actions": []
    }

    errors: List[str] = []

    try:
        # Header
        header = HEADER_RE.search(raw_text)
        if header:
            hand["id"] = int(header.group("hand_id"))
            hand["datetime"] = datetime.strptime(header.group("datetime"), "%Y/%m/%d %H:%M:%S")
        else:
            errors.append("Header not found")

        # Seats / players
        for m in SEAT_RE.finditer(raw_text):
            hand["players"].append({
                "seat": int(m.group("seat")),
                "name": m.group("name"),
                "stack_start": float(m.group("stack"))
            })

        # Actions
        for line in raw_text.splitlines():
            m = ACTION_RE.match(line.strip())
            if m:
                action = {
                    "player": m.group("player"),
                    "action": m.group("action"),
                    "amount": float(m.group("amount")) if m.group("amount") else None
                }
                hand["actions"].append(action)

    except Exception as e:
        errors.append(str(e))

    return {
        "hand": hand,
        "errors": errors
    }


def parse_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a full hand history file into structured hands.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    blocks = split_into_blocks(raw_text)

    parsed_hands = []
    for block in blocks:
        result = parse_hand(block)
        parsed_hands.append(result)

    return parsed_hands
