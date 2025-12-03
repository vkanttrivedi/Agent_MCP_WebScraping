"""Example: parse Runner.run assistant output and extract YAML snapshots.

Run: python examples/parse_output.py
Requires: PyYAML (added to requirements.txt)
"""
import json
import re
from typing import List, Tuple

import yaml


def extract_output_texts(messages: List[dict]) -> List[str]:
    texts = []
    for m in messages:
        for c in m.get("content", []):
            if c.get("type") == "output_text":
                texts.append(c.get("text", ""))
    return texts


def extract_yaml_blocks(text: str) -> List[str]:
    # finds fenced ```yaml ... ``` blocks
    return re.findall(r"```yaml\n([\s\S]*?)```", text)


def extract_js_code_blocks(text: str) -> List[str]:
    # finds fenced ```js or ```javascript code blocks
    return re.findall(r"```(?:js|javascript)\n([\s\S]*?)```", text)


def extract_screenshot_paths_from_js(code: str) -> List[str]:
    # look for await page.screenshot({ path: 'shot.png' }) patterns
    paths = re.findall(r"page\.screenshot\([^\)]*path\s*:\s*['\"]([^'\"]+)['\"]", code)
    return paths


def extract_image_refs_from_yaml(parsed_yaml) -> List[str]:
    images = []

    def walk(value):
        if isinstance(value, str):
            if re.search(r"\.(png|jpg|jpeg|gif|webp)$", value, re.IGNORECASE):
                images.append(value)
        elif isinstance(value, dict):
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)

    walk(parsed_yaml)
    return images


def extract_screenshots_and_evidence(text: str) -> Tuple[List[str], List[str]]:
    """Return (screenshot_paths, evidence_refs) found in the text.

    - Scans JS code blocks for screenshot calls.
    - Scans YAML snapshots for image filenames and `ref=` markers.
    """
    shots = []
    evidence = []

    # JS code blocks
    for code in extract_js_code_blocks(text):
        shots.extend(extract_screenshot_paths_from_js(code))

    # Generic filename hints (shot.png etc.)
    shots.extend(re.findall(r"[\w\-\./]+\.(?:png|jpg|jpeg|gif|webp)", text))

    # YAML blocks: parse and look for image refs and `ref=` markers
    for block in extract_yaml_blocks(text):
        try:
            parsed = yaml.safe_load(block)
            shots.extend(extract_image_refs_from_yaml(parsed))
            # find inline ref=VALUE tokens inside the block text
            evidence.extend(re.findall(r"ref=([\w\-]+)", block))
        except Exception:
            pass

    # dedupe
    shots = list(dict.fromkeys(shots))
    evidence = list(dict.fromkeys(evidence))
    return shots, evidence


def parse_runner_output(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    outputs = extract_output_texts(data)
    snapshots = []
    for o in outputs:
        for block in extract_yaml_blocks(o):
            try:
                parsed = yaml.safe_load(block)
                snapshots.append(parsed)
            except Exception:
                # ignore malformed YAML blocks
                pass
    return snapshots


if __name__ == "__main__":
    # Example usage: create a small JSON file with the Runner.run response
    example = [
        {
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "### Page Snapshot:\n```yaml\n- generic:\n  - heading \"Example Domain\"\n```",
                }
            ],
        }
    ]

    with open("example_runner_response.json", "w", encoding="utf-8") as ex:
        json.dump(example, ex, indent=2)

    snaps = parse_runner_output("example_runner_response.json")
    print("Parsed snapshots:")
    print(json.dumps(snaps, indent=2))

    # also demonstrate extracting screenshots/evidence from the assistant output
    with open("example_runner_response.json", "r", encoding="utf-8") as ex:
        messages = json.load(ex)
    texts = extract_output_texts(messages)
    for t in texts:
        shots, evid = extract_screenshots_and_evidence(t)
        print("Found screenshots:", shots)
        print("Found evidence refs:", evid)
        # write screenshots manifest for downstream validation
        if shots:
            manifest = {
                "screenshots": shots,
                "source": "examples/parse_output.py",
            }
            with open("screenshots_manifest.json", "w", encoding="utf-8") as mf:
                json.dump(manifest, mf, indent=2)
            print("Wrote screenshots_manifest.json with", len(shots), "entries")
