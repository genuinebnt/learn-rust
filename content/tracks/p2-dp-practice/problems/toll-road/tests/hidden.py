import random

from anneal_prelude import check, ensure
from solution import cheapest_trip


def test_skipping_the_expensive_middle():
    check('cheapest_trip([1, 50, 50, 1, 50, 50, 1])', cheapest_trip([1, 50, 50, 1, 50, 50, 1]), 3)


def test_every_stop_costs_one():
    check('cheapest_trip([1, 1, 1, 1, 1, 1, 1])', cheapest_trip([1, 1, 1, 1, 1, 1, 1]), 3)


def test_a_cheap_stop_is_not_always_worth_it():
    check('cheapest_trip([2, 1, 9, 9, 1, 1])', cheapest_trip([2, 1, 9, 9, 1, 1]), 4)


def test_long_road():
    check('cheapest_trip([1] * 99)', cheapest_trip([1] * 99), 33)


def test_two_stops():
    check('cheapest_trip([2, 5])', cheapest_trip([2, 5]), 2)


def test_three_stops():
    check('cheapest_trip([9, 1, 1])', cheapest_trip([9, 1, 1]), 9)


def test_four_stops_the_third_is_cheap():
    check('cheapest_trip([3, 9, 9, 1])', cheapest_trip([3, 9, 9, 1]), 4)


def reference(tolls):
    n = len(tolls)
    if n == 0:
        return 0
    best = float("inf")

    def go(i, paid):
        nonlocal best
        paid += tolls[i]
        if i >= n - 3:
            best = min(best, paid)
        for k in (1, 2, 3):
            if i + k < n:
                go(i + k, paid)

    go(0, 0)
    return best


def test_random_roads_against_trying_every_route():
    rng = random.Random(2)
    for _ in range(300):
        tolls = [rng.randint(0, 9) for _ in range(rng.randint(0, 9))]
        check(f"cheapest_trip({tolls})", cheapest_trip(tolls), reference(tolls))
