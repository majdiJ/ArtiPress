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
REQUIRED_JSON_ARTICLE_FIELDS = [
    "article_title",
    "author_slugs",
    "article_image_url",
    "article_strap_line",
    "date.published"
]   
RESERVED_FOLDERS_IN_ARTICLES = [
    "authors",
    ]

def get_nested(data: dict, key: str):
    """
    Retrieve a value from a nested dictionary using a dot-notation key. Returns None if any part of the path is missing.
    
    Args:
        data: The dictionary to traverse.
        key:  The dot-notation key to look up.
    Returns:
        The value at the nested key, or None if any part of the path is missing.
    """
    keys = key.split(".")
    for k in keys:
        if not isinstance(data, dict) or k not in data:
            return None
        data = data[k]
    return data

def validate_json(filepath: str, required_fields: list[str]) -> dict:
    """
    Validate that the JSON file exists, is valid JSON, and contains required fields. Raises FileNotFoundError, ValueError, or KeyError with descriptive messages if validation fails.

    Args:
        filepath:        Path to the JSON file to validate.
        required_fields: List of dot-notation keys that must be present in the JSON.
    Returns:
        The loaded JSON data as a dictionary if validation passes.
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

def get_folders(directory: str, ignore: list[str] = []) -> list[str]:
    """
    Returns a list of top-level folder names within a given directory.

    Args:
        directory: Path to the directory to scan.
        ignore:    List of folder names to exclude.
    Returns:
        A list of folder names (not full paths).
    """
    return [
        entry.name
        for entry in os.scandir(directory)
        if entry.is_dir() and entry.name not in ignore
    ]

def main():
    # Verify that `artipress_data/artipress.config.json` exists and is valid JSON. 
    config_data = validate_json(JSON_CONFIG_FILEPATH, REQUIRED_JSON_CONFIG_FIELDS)
    pass

    # 1. Go through each article folder in `input_articles_folder` and validate that it contains an `article.json` file with the required fields. If any article folder is missing the `article.json` file or if the JSON is invalid or missing required fields, raise an error with a descriptive message indicating which article folder is invalid and what the issue is, stopping the generation process until all issues are resolved.

    #2. For each valid article, generate an article page using the `template_paths.article_page` template and populate it with the article's data from `article.json` and the author's data from `artipress_data/authors/authors.json`. Save the generated article pages to the `generated_output_path` directory, maintaining a clear structure (e.g., `generated_output_path/{article_slug}/index.html`).

    #3. Once all article pages are generated, create an article list page using the `template_paths.article_list` template. This page should list all articles with their title, strap line, and other data, and a link to their respective article page. Save this generated page to the `generated_output_path` directory (e.g., `generated_output_path/index.html`).

    #4. For each author in `artipress_data/authors/authors.json`, generate an author page using the `template_paths.author_page` template and populate it with the author's data and a list of their articles. Save the generated author pages to the `generated_output_path` directory, maintaining a clear structure (e.g., `generated_output_path/authors/{author_slug}/index.html`).

    #5. Once all author pages are generated, update the article list page to include links to the author pages where the author's name, avatar, and other data is displayed.


    # --- 1. Validate article folders and their `article.json` files ---
    
    # Get list of article folders in `input_articles_folder`
    article_folders = get_folders(config_data["input_articles_folder"])

    # Dev: Print the article folders found (for now)
    print("Article folders found:")
    for folder in article_folders:
        print(f"- {folder}")

    # For each article folder, validate the presence and contents of `article.json`
    for folder in article_folders:
        article_json_path = os.path.join(config_data["input_articles_folder"], folder, "article.json")
        try:
            article_data = validate_json(article_json_path, REQUIRED_JSON_ARTICLE_FIELDS)
            print(f"Validated article: {article_data['article_title']}")
        except (FileNotFoundError, ValueError, KeyError) as e:
            # Raise an error with a descriptive message indicating which article folder is invalid and what the issue is
            print(f"Error in article folder '{folder}': {e}")
            # Stop the generation process until all issues are resolved
            return
        
    # --- 2. Generate article pages ---



if __name__ == "__main__":
    main()