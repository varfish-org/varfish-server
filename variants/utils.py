import importlib


def class_from_string(dot_path):
    """Load a class from the given dot path."""
    if "." in dot_path:
        module_name, class_name = dot_path.rsplit(".", 1)
    else:
        module_name = "."
        class_name = dot_path
    m = importlib.import_module(module_name)
    return getattr(m, class_name)
