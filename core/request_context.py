from threading import local

_state = local()


def set_current_request(request) -> None:
    _state.request = request


def get_current_request():
    return getattr(_state, "request", None)


def clear_current_request() -> None:
    if hasattr(_state, "request"):
        delattr(_state, "request")
