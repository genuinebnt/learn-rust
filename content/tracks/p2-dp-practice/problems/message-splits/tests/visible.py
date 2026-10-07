from anneal_prelude import check, ensure
from solution import count_splits


def test_three_digits():
    check('count_splits("123", 26)', count_splits("123", 26), 3)


def test_zeros_block_pieces():
    check('count_splits("100", 100)', count_splits("100", 100), 1)


def test_empty_message():
    check('count_splits("", 9)', count_splits("", 9), 1)


def test_single_digits_only():
    check('count_splits("123", 9)', count_splits("123", 9), 1)


def test_impossible():
    check('count_splits("0", 9)', count_splits("0", 9), 0)


def test_two_digit_pieces():
    check('count_splits("2626", 26)', count_splits("2626", 26), 4)
