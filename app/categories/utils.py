def get_items_with_divisor(items):
    output = []
    for _ in items:
        output.append(dict())
    output[-2]["divider"] = "or"
    return output


def check_radio_field(question, answer, items):
    if not items:
        items = []
        for _ in items:
            items.append(dict())

    for question_num in range(len(question.choices)):
        if question.choices[question_num][0] == answer:
            items[question_num]["checked"] = True
    return items


def print_routing_map(routing_map, indent=0):
    """
    Pretty prints the routing map with proper indentation.

    Args:
        routing_map (dict): The routing map to print
        indent (int): Current indentation level
    """
    indent_str = "  " * indent

    for key, value in routing_map.items():
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            print_routing_map(value, indent + 1)
        else:
            print(f"{indent_str}{key}: {value}")


def flatten_paths(d):
    """Convert nested dictionary into list of paths, including the final result"""
    paths = []

    def collect_path(current_dict, current_path):
        for key, value in current_dict.items():
            # Skip Form and Traversal entries
            if "Form" in key or "Traversal" in key:
                if isinstance(value, dict):
                    collect_path(value, current_path)
                continue

            new_path = current_path + [key]

            if isinstance(value, dict):
                collect_path(value, new_path)
            else:
                # Include the final result/destination
                paths.append(new_path + [value])

    collect_path(d, [])
    return paths
