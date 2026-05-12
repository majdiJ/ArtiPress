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

author = get_author_info("john-doe", "artipress_data/authors/authors.json")

if author:
    print(author["author_name"])   # "John Doe"
    print(author["author_role"])   # "Senior Writer"
else:
    print("Author not found")