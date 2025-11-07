from .seruti import generate as seruti_generate
from .susenas import generate as susenas_generate


def get_generator(name: str):
    key = (name or '').lower()
    if key == 'seruti':
        return seruti_generate
    if key == 'susenas':
        return susenas_generate
    return None
