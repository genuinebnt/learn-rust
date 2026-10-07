import random

from anneal_prelude import check, ensure
from solution import count_splits


def test_a_zero_that_attaches_to_a_ten():
    check('count_splits("1020", 20)', count_splits("1020", 20), 1)


def test_same_digit_many_times():
    check('count_splits("1111", 11)', count_splits("1111", 11), 5)


def test_biggest_is_one_digit_and_zero_appears():
    check('count_splits("1203", 9)', count_splits("1203", 9), 0)


def test_big_pieces():
    check('count_splits("123456", 1000)', count_splits("123456", 1000), 24)


def test_piece_larger_than_biggest():
    check('count_splits("99", 50)', count_splits("99", 50), 1)


def test_leading_zero():
    check('count_splits("05", 99)', count_splits("05", 99), 0)


def reference(digits, biggest):
    if not digits:
        return 1
    total = 0
    for i in range(1, len(digits) + 1):
        piece = digits[:i]
        if piece[0] != "0" and int(piece) <= biggest:
            total += reference(digits[i:], biggest)
    return total


def test_random_messages_against_trying_every_cut():
    rng = random.Random(12)
    for _ in range(400):
        digits = "".join(rng.choice("0123456789") if rng.random() < 0.4 else rng.choice("12") for _ in range(rng.randint(0, 9)))
        biggest = rng.choice([9, 10, 26, 99, 100, 255, 1000])
        check(f"count_splits({digits!r}, {biggest})", count_splits(digits, biggest), reference(digits, biggest))


def test_a_long_message_is_fast():
    total = count_splits("1" * 60, 1000)
    ensure(total > 10**15, "there are enormously many ways to cut sixty ones into pieces of up to three digits")
