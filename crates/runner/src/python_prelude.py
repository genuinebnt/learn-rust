"""anneal's helpers for Python practice tests. Tests do `from anneal_prelude import check, ensure`."""


class Mismatch(AssertionError):
    """A check that failed, carrying what the web app shows: the call, what it should be, what it was."""

    def __init__(self, call, got, expected):
        super().__init__(f"{call}: expected {expected}, got {got}")
        self.call, self.got, self.expected = call, got, expected


def check(call, got, expected):
    """Compare `got` with `expected`. `call` is the text of the call under test, e.g. "build_order(3, [(1, 0)])"."""
    if got != expected:
        raise Mismatch(call, repr(got), repr(expected))


def ensure(condition, message):
    """For answers that aren't unique: assert a property, with a message that says what is wrong."""
    if not condition:
        raise AssertionError(message)
