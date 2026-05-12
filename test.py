import re

def render_template(template: str, variables: dict) -> str:
    def replacer(match):
        key = match.group(1).strip()
        if key not in variables:
            raise KeyError(f"Template variable '{key}' not found in provided dictionary")
        return str(variables[key])

    return re.sub(r'\{html_var\((\w+)\)\}', replacer, template)

template = """
    <meta property="og:url" content="{html_var(base_url)}/articles/{html_var(article_id)}">
    <meta property="article:author" content="{html_var(base_url)}/authors/{html_var(article_author_slug)}" />
"""

variables = {
    "base_url": "example.com",
    "article_id": "42",
    "article_author_slug": "john-doe",
}

print(render_template(template, variables))