from anneal_prelude import check, ensure
from solution import count_rooms


def test_two_rooms():
    check('count_rooms(["..#..", "..#..", "###.."])', count_rooms(["..#..", "..#..", "###.."]), 2)


def test_no_floor():
    check('count_rooms(["###", "###"])', count_rooms(["###", "###"]), 0)


def test_one_big_room():
    check('count_rooms(["...", "...", "..."])', count_rooms(["...", "...", "..."]), 1)


def test_diagonal_is_not_connected():
    check('count_rooms([".#", "#."])', count_rooms([".#", "#."]), 2)


def test_empty_plan():
    check('count_rooms([])', count_rooms([]), 0)


def test_single_tile():
    check('count_rooms(["."])', count_rooms(["."]), 1)
