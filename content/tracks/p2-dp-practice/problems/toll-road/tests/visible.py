from anneal_prelude import check, ensure
from solution import cheapest_trip


def test_mixed_tolls():
    check('cheapest_trip([5, 1, 1, 9, 1])', cheapest_trip([5, 1, 1, 9, 1]), 6)


def test_drive_past_the_end():
    check('cheapest_trip([4, 7, 2])', cheapest_trip([4, 7, 2]), 4)


def test_no_stops():
    check('cheapest_trip([])', cheapest_trip([]), 0)


def test_one_stop():
    check('cheapest_trip([9])', cheapest_trip([9]), 9)


def test_all_zero():
    check('cheapest_trip([0, 0, 0, 0])', cheapest_trip([0, 0, 0, 0]), 0)


def test_two_stops():
    check('cheapest_trip([3, 8])', cheapest_trip([3, 8]), 3)
