from django.forms import model_to_dict


def model_to_dict_for_api(obj, *args, **kwargs):
    """Call ``django.fors.model_to_dict`` and remove ``None`` values."""
    result = {k: v for k, v in model_to_dict(obj, *args, **kwargs).items() if v is not None}
    for k in list(result.keys()):
        if hasattr(getattr(obj, k), "sodar_uuid"):
            result[k] = str(getattr(obj, k).sodar_uuid)
    return result
