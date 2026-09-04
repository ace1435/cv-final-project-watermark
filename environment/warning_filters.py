import warnings

entries = []


def apply():
    warnings.simplefilter("error")
    for library, message, reason in entries:
        warnings.filterwarnings("ignore", message=message, module=library)
