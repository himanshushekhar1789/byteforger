import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_candidates():
    with open(DATA_DIR / "candidates.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        return data["candidates"]


def load_curriculum():
    with open(DATA_DIR / "curriculum.json", "r", encoding="utf-8") as file:
        return json.load(file)