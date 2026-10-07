from anneal_prelude import check, ensure
from solution import find_a_peak

def is_peak(values, i):
    left = values[i - 1] if i > 0 else float("-inf")
    right = values[i + 1] if i + 1 < len(values) else float("-inf")
    return values[i] > left and values[i] > right


def expect_peak(values):
    i = find_a_peak(list(values))
    ensure(isinstance(i, int) and 0 <= i < len(values), f"find_a_peak({values}) returned {i}, which is not an index")
    ensure(is_peak(values, i), f"find_a_peak({values}) returned {i}, but {values[i]} is not greater than both neighbours")


def test_a_hill_in_the_middle():
    check("find_a_peak([1, 3, 2])", find_a_peak([1, 3, 2]), 1)


def test_rising_to_the_end():
    check("find_a_peak([1, 2, 3, 4])", find_a_peak([1, 2, 3, 4]), 3)


def test_falling_from_the_start():
    check("find_a_peak([4, 3, 2, 1])", find_a_peak([4, 3, 2, 1]), 0)


def test_one_value():
    check("find_a_peak([5])", find_a_peak([5]), 0)


def test_two_peaks_either_is_fine():
    expect_peak([1, 5, 2, 6, 1])
