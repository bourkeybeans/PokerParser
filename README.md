# PokerParser

A lightweight hand history parser for PokerStars.  
Takes raw `.txt` hand history files and outputs structured JSON with players, stacks, and actions.

## Features
- Splits a history file into individual hands  
- Extracts hand ID, timestamp, players, stacks, and actions  
- Outputs clean JSON that’s easy to use in other tools  

## Install
Clone the repo and install locally:

```bash
git clone https://github.com/yourname/pokerparser.git
cd pokerparser
pip install -e .
```

(or just run `parser.py` directly with Python)

## Usage

### As a library
```python
from parser import parse_file

hands = parse_file("session.txt")
print(f"Parsed {len(hands)} hands")

for h in hands[:2]:
    print(h["hand"]["id"], len(h["hand"]["players"]), len(h["hand"]["actions"]))
```

### From the command line
```bash
python parser.py session.txt --json out.json
```

Outputs structured hands as JSON.

## Example output
```json
{
  "hand": {
    "id": 257563713105,
    "datetime": "2023-05-10 20:00:00",
    "players": [
      {"seat": 1, "name": "Alice", "stack_start": 100.0},
      {"seat": 2, "name": "Bob", "stack_start": 95.0}
    ],
    "actions": [
      {"player": "Alice", "action": "posts small blind", "amount": 0.5},
      {"player": "Bob", "action": "posts big blind", "amount": 1.0},
      {"player": "Alice", "action": "calls", "amount": 1.0}
    ]
  },
  "errors": []
}
```

## Status
- Currently supports **PokerStars** hand history format  
- More sites/formats can be added (Party, GG, etc.)  
- Early version — expect edge cases  

## License
MIT
