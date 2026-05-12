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
AUTHOR_JSON_PATH = "artipress_data/authors/authors.json"

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

def get_author_info(author_slug: str, authors_json_path: str) -> dict:
    """
    Retrieves author details from a JSON file by their slug.

    Args:
        author_slug: The unique slug identifier for the author (e.g. "john-doe").
        authors_json_path: The file path to the authors JSON file.

    Returns:
        A dict containing the author's details, or an empty dict if not found.
    """
    import json

    with open(authors_json_path, "r", encoding="utf-8") as f:
        authors = json.load(f)

    return next(
        (author for author in authors if author.get("author_slug") == author_slug),
        {}
    )

def make_author_meta_tag(article_data: dict) -> str:
    # Get a list of the article's authors' details using `get_author_info` and the `author_slugs` field in `article_data`. Appened to structured meta tag.
    meta_tags = ""
    for author_slug in article_data["author_slugs"]:
        author_info = get_author_info(author_slug, AUTHOR_JSON_PATH)
        if meta_tags == "":
            meta_tags += f"<meta name=\"author\" content=\"{author_info.get('author_name', 'Unknown Author')}\" />"
        else:
            meta_tags += f"\n<meta name=\"author\" content=\"{author_info.get('author_name', 'Unknown Author')}\" />"

    return meta_tags

def make_author_og_meta_tag(article_data: dict) -> str:
    # Get a list of the article's authors' details using `get_author_info` and the `author_slugs` field in `article_data`. Appened to structured Open Graph meta tag.
    og_meta_tags = ""
    for author_slug in article_data["author_slugs"]:
        author_info = get_author_info(author_slug, AUTHOR_JSON_PATH)
        if og_meta_tags == "":
            og_meta_tags += f"<meta property=\"article:author\" content=\"{base_url}/authors/{author_slug}\" />"
        else:
            og_meta_tags += f"\n<meta property=\"article:author\" content=\"{base_url}/authors/{author_slug}\" />"

    return og_meta_tags

def make_author_ld_json(article_data: dict) -> str:
    # Get a list of the article's authors' details using `get_author_info` and the `author_slugs` field in `article_data`. Appened to structured application/ld+json script tag.
    authors_ld_json = []
    for author_slug in article_data["author_slugs"]:
        author_info = get_author_info(author_slug, AUTHOR_JSON_PATH)
        author_ld_json = {
            "@type": "Person",
            "name": author_info.get("author_name", "Unknown Author"),
            "url": f"{base_url}/authors/{author_slug}"
        }
        authors_ld_json.append(author_ld_json)

    return json.dumps(authors_ld_json, indent=4)

def make_author_html_element(article_data: dict) -> str:
    # Get a list of the article's authors' details using `get_author_info` and the `author_slugs` field in `article_data`. Appened to structured html element.
    html_authors_info = ""
    for author_slug in article_data["author_slugs"]:
        author_info = get_author_info(author_slug, AUTHOR_JSON_PATH)

        if html_authors_info == "":
            html_authors_info += f"<a href='{base_url}/authors/{author_slug}'>{author_info.get('author_name', 'Unknown Author')}</a>"
        else:
            html_authors_info += f", <a href='{base_url}/authors/{author_slug}'>{author_info.get('author_name', 'Unknown Author')}</a>"
    
    return html_authors_info

def generate_article_page(article_id: str, article_data: dict, template: str, output_path: str):

    # Construct author meta tags
    author_meta_tags = make_author_meta_tag(article_data)

    # Construct Open Graph author meta tags
    og_meta_tags_authors = make_author_og_meta_tag(article_data)

    # Construct application/ld+json author structured data
    json_ld_authors = make_author_ld_json(article_data)

    # Construct author HTML element
    html_authors_info = make_author_html_element(article_data)

    # Construct published date
    ISO_published_date = article_data.get("date", {}).get("published", "")
    published_date_element = f'<time class="localised-date" datetime="{ISO_published_date}">{ISO_published_date}</time>'

    # Construct edited date (if it exists and has a value)
    ISO_edited_date = ""
    edited_date_element = ""
    if article_data.get("date", {}).get("edited") not in (None, ""):
        ISO_edited_date = article_data.get("date", {}).get("edited", "")
        edited_date_element = f'Edited on <time class="localised-date" datetime="{ISO_edited_date}">{ISO_edited_date}</time>'

    replacement_vars = {
        "article_title": article_data.get("article_title", "Untitled Article"),
        "website_title": website_title,
        "base_url": base_url,
        "article_id": article_id,
        "article_strap_line": article_data.get("article_strap_line", ""),
        "article_keywords_list": ", ".join(article_data.get("article_keywords", [])),
        "author_meta_tags": author_meta_tags,
        "article_featured_image": article_data.get("article_image_url", ""),
        "article_published_date_iso": ISO_published_date,
        "article_edited_date_iso_iso": ISO_edited_date,
        "og_meta_tags_authors": og_meta_tags_authors,
        "website_favicon": website_favicon,
        "apple_touch_icon": apple_touch_icon,
        "theme_color": theme_color,
        "apple_status_bar_style": apple_status_bar_style,
        "custom_style": custom_style,
        "website_logo": website_logo,
        "json_ld_authors": json_ld_authors,
        "article_authors": html_authors_info,
        "article_published_date": published_date_element,
        "article_edited_date_iso": ISO_edited_date,
        "article_image_url": article_data.get("article_image_url", ""),
        "article_image_alt": article_data.get("article_image_alt", ""),
        "article_content_html": article_data.get("article_content_html", ""),
    }

    pass

def main():
    # Verify that `artipress_data/artipress.config.json` exists and is valid JSON. 
    config_data = validate_json(JSON_CONFIG_FILEPATH, REQUIRED_JSON_CONFIG_FIELDS)
    pass

    # Set global variables
    global base_url
    base_url = config_data.get("base_url", "http://artipress.majdij.com")
    global website_title
    website_title = config_data.get("website_title", "ArtiPress")
    global website_favicon
    website_favicon = config_data.get("website_favicon", "https://artipress.majdij.com/resources/images/favicon.png")
    global apple_touch_icon
    apple_touch_icon = config_data.get("apple_touch_icon", "https://artipress.majdij.com/resources/images/apple-touch-icon.png")
    global theme_color
    theme_color = config_data.get("theme_color", "#000000")
    global apple_status_bar_style
    apple_status_bar_style = config_data.get("apple_status_bar_style", "default")
    global custom_style
    custom_style = config_data.get("custom_style", "")
    global website_logo
    website_logo = config_data.get("website_logo", "https://artipress.majdij.com/resources/images/logo.png")

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