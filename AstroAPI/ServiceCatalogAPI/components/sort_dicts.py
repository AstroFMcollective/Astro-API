def sort_dicts(dict: dict, order: list) -> dict:
    """
        Sorts a dictionary based on the order of keys provided in the list.

        Use this in the Global Interface to ensure that the order of keys in the dictionary matches the specified (general) order.
        Also applicable in other places.
    """
    new_dict = {}
    for key in order:
        if key in dict:
            new_dict[key] = dict[key]
    return new_dict