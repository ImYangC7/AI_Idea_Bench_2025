import json
import sys
import os

from utils.header import ConfigReader
from utils.llms_api import APIHelper


DATA_PATH = "/data/yc/AI_Idea_Bench_2025/target_paper_data.json"
CONFIG_PATH = "/data/yc/SciPIP/configs/datasets.yaml"
SAMPLE_SIZE = 3


def load_backgrounds(path, limit):
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    backgrounds = []
    for item in records:
        summary = item.get("summary")
        bg = None
        if isinstance(summary, dict):
            bg = summary.get("revised_topic") or summary.get("topic")
        elif isinstance(summary, str):
            bg = summary
        if bg:
            backgrounds.append(bg)
        if len(backgrounds) >= limit:
            break
    return backgrounds


def main():
    print(f"Loading backgrounds from: {DATA_PATH}")
    backgrounds = load_backgrounds(DATA_PATH, SAMPLE_SIZE)
    print(f"Loaded {len(backgrounds)} backgrounds")
    if not backgrounds:
        print("No backgrounds found. Check summary fields in the input file.")
        sys.exit(1)

    config = ConfigReader.load(CONFIG_PATH)
    api_helper = APIHelper(config)

    for idx, bg in enumerate(backgrounds):
        print(f"\n=== Sample {idx} background ===")
        print(bg)
        entities = api_helper.generate_entity_list(bg)
        print(f"Entities: {entities}")


if __name__ == "__main__":
    main()

