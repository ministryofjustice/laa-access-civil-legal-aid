def category_name(code):
    # Get the current blueprint instance
    from app.find_a_legal_advisor import bp

    code = code.upper()

    # Find the matching category
    category = next((cat for cat in bp.categories if cat["code"] == code), None)

    # Return the name if found, otherwise return the code
    return category["name"] if category else code
