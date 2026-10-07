from anneal_prelude import check, ensure
from solution import distance_to_exit


def test_two_exits():
    check('distance_to_exit(["E..", ".#.", "..E"])', distance_to_exit(["E..", ".#.", "..E"]), [[0, 1, 2], [1, -1, 1], [2, 1, 0]])


def test_one_exit_in_a_corridor():
    check('distance_to_exit(["E...."])', distance_to_exit(["E...."]), [[0, 1, 2, 3, 4]])


def test_walled_off_floor():
    check('distance_to_exit(["E#.", "##.", "..."])', distance_to_exit(["E#.", "##.", "..."]), [[0, -1, -1], [-1, -1, -1], [-1, -1, -1]])


def test_no_exit():
    check('distance_to_exit(["..", ".."])', distance_to_exit(["..", ".."]), [[-1, -1], [-1, -1]])


def test_only_exits():
    check('distance_to_exit(["EE"])', distance_to_exit(["EE"]), [[0, 0]])


def test_empty():
    check('distance_to_exit([])', distance_to_exit([]), [])
