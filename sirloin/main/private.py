def query_to_list(query, remove_id=True):
    return [obj_to_dict(entry, remove_id) for entry in query]


def obj_to_dict(obj, remove_id=True):
    result = dict()
    for key, value in vars(obj).items():
        if key.startswith("_") or (remove_id and key == "id"):
            continue
        result[key] = value
    return result
