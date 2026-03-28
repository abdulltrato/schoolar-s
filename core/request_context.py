from threading import local
from contextlib import contextmanager

_state = local()


def set_current_request(request) -> None:
    _state.request = request


def get_current_request():
    return getattr(_state, "request", None)


def clear_current_request() -> None:
    if hasattr(_state, "request"):
        delattr(_state, "request")


@contextmanager
def suspend_current_request():
    """
    Temporarily clears the current request from thread-local storage.

    This is useful for internal operations (e.g., cross-tenant transfers) where
    model-level request-based tenant enforcement would otherwise prevent moving
    records between tenants within a single HTTP request.
    """

    previous = get_current_request()
    clear_current_request()
    try:
        yield previous
    finally:
        if previous is not None:
            set_current_request(previous)
