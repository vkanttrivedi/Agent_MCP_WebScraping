"""Small runnable harness that parses `test_harness/example_runner_response.json`.

Usage (PowerShell):

  python test_harness/run_parse_example.py

This imports `examples.parse_output.parse_runner_output` and prints parsed snapshots
and any discovered screenshots/evidence.
"""
import json
import os
from examples.parse_output import parse_runner_output, extract_output_texts, extract_screenshots_and_evidence


def main():
    here = os.path.dirname(__file__)
    sample = os.path.join(here, "example_runner_response.json")
    print("Parsing:", sample)
    snaps = parse_runner_output(sample)
    print("Parsed snapshots:")
    print(json.dumps(snaps, indent=2))

    # also extract screenshots/evidence from output_text
    with open(sample, "r", encoding="utf-8") as f:
        messages = json.load(f)
    texts = extract_output_texts(messages)
    for t in texts:
        shots, evid = extract_screenshots_and_evidence(t)
        print("Found screenshots:", shots)
        print("Found evidence refs:", evid)


if __name__ == "__main__":
    main()
