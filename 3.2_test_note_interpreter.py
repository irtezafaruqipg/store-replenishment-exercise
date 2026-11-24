from pathlib import Path
from runpy import run_path

# Load the validator without running the note classification script.
script = Path(__file__).parent / "3.1_note_interpreter.py"
validate_response = run_path(str(script))["validate_response"]

reply = '{"category": "promotion", "needs_review": false}'
assert validate_response(reply) == {
    "category": "promotion",
    "needs_review": False,
}
print("PASS: Accepted a promotion with no manual review")

reply = '{"category": "instruction_attempt", "needs_review": true}'
assert validate_response(reply) == {
    "category": "instruction_attempt",
    "needs_review": True,
}
print("PASS: Accepted an instruction attempt flagged for review")

invalid_examples = [
    ("broken JSON", '{"category":'),
    ("a list instead of an object", '["promotion", false]'),
    ("a missing review flag", '{"category": "promotion"}'),
    ("an unknown category", '{"category": "urgent", "needs_review": true}'),
    ("a review flag given as text", '{"category": "shelf_gap", "needs_review": "true"}'),
    (
        "an instruction attempt without a review flag set to true",
        '{"category": "instruction_attempt", "needs_review": false}',
    ),
    (
        "an extra order quantity",
        '{"category": "instruction_attempt", "needs_review": true, "order_units": 10000}',
    ),
]

for name, reply in invalid_examples:
    assert validate_response(reply) is None, f"Expected to reject {name}"
    print(f"PASS: Rejected {name}")

print("\nAll 9 validation examples passed.")