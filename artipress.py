import json
import os

JSON_CONFIG_FILEPATH = "artipress_data/artipress.config.json"
REQUIRED_JSON_CONFIG_FIELDS = [
    "template_paths.article_list",
    "template_paths.article_page",
    "template_paths.author_page",
    "input_articles_folder",
    "generated_output_path",
]

def get_nested(data: dict, key: str):
    """Traverse a dot-notation key like 'template_paths.article_list'."""
    keys = key.split(".")
    for k in keys:
        if not isinstance(data, dict) or k not in data:
            return None
        data = data[k]
    return data

def validate_json(filepath: str, required_fields: list[str]) -> dict:
    """
    Validate that the JSON file exists, is valid JSON, and contains required fields.
    Raises FileNotFoundError, ValueError, or KeyError with descriptive messages if validation fails.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"JSON file not found: {filepath}")

    with open(filepath, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file '{filepath}': {e}")

    missing = [f for f in required_fields if get_nested(data, f) is None]
    if missing:
        raise KeyError(f"JSON is missing required fields: {missing}")

    return data

def main():
    # Verify that `artipress_data/artipress.config.json` exists and is valid JSON. 
    data = validate_json(JSON_CONFIG_FILEPATH, REQUIRED_JSON_CONFIG_FIELDS)
    pass

if __name__ == "__main__":
    main()