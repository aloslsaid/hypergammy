import json
from pathlib import Path


def test_category_configuration_is_valid():
    root = Path(__file__).resolve().parents[1]
    categories = json.loads((root / "categories.json").read_text(encoding="utf-8"))
    ids = [item["category_id"] for item in categories]
    assert len(ids) == 34
    assert len(ids) == len(set(ids))
    for item in categories:
        assert item["required_features"]
        assert item["group_id"]
        assert item["reference_path"].startswith("reference_images/")
