from anneal_prelude import check, ensure
from solution import hop_ways


def test_ten_stones():
    check('hop_ways(10)', hop_ways(10), 274)


def test_twenty_stones():
    check('hop_ways(20)', hop_ways(20), 121415)


def test_thirty_stones():
    check('hop_ways(30)', hop_ways(30), 53798080)


def test_six_stones():
    check('hop_ways(6)', hop_ways(6), 24)


def test_seven_stones():
    check('hop_ways(7)', hop_ways(7), 44)


def slow(n):
    return 1 if n == 0 else sum(slow(n - k) for k in (1, 2, 3) if n - k >= 0)


def test_small_values_against_plain_recursion():
    for n in range(0, 15):
        check(f"hop_ways({n})", hop_ways(n), slow(n))


def test_sixty_stones_is_fast_and_exact():
    ways = [1, 1, 2]
    for n in range(3, 61):
        ways.append(ways[-1] + ways[-2] + ways[-3])
    check("hop_ways(60)", hop_ways(60), ways[60])


def test_each_value_is_the_sum_of_the_previous_three():
    for n in range(3, 40):
        check(f"hop_ways({n})", hop_ways(n), hop_ways(n - 1) + hop_ways(n - 2) + hop_ways(n - 3))
