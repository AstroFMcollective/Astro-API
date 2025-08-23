def dom_to_markdown(node):
    """Recursively convert Genius' DOM-like JSON node into markdown text."""
    if isinstance(node, str):
        return node # Plain text
    
    if not isinstance(node, dict):
        return ""
    
    tag = node.get("tag", "")
    children = node.get("children", [])
    attributes = node.get("attributes", {})
    
    # Recursively process children
    content = "".join(dom_to_markdown(child) for child in children)
    
    # Handle tags
    if tag == "p":
        return f"\n\n{content.strip()}\n\n"
    elif tag == "em":
        return f"*{content}*"
    elif tag == "strong":
        return f"**{content}**"
    elif tag == "a":
        href = attributes.get("href", "#")
        return f"[{content}]({href})"
    elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(tag[1])
        return f"\n\n{'#' * level} {content.strip()}\n\n"
    elif tag == "br":
        return "  \n"
    else:
        return content  # Fallback: just render children

def json_to_markdown(data):
    dom = data.get("dom", {})
    return dom_to_markdown(dom).strip()