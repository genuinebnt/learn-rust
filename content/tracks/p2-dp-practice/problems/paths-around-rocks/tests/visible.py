from anneal_prelude import check, ensure
from solution import count_paths


def test_rock_in_the_middle():
    check('count_paths(["...", ".#.", "..."])', count_paths(["...", ".#.", "..."]), 2)


def test_open_grid():
    check('count_paths(["...", "...", "..."])', count_paths(["...", "...", "..."]), 6)


def test_start_is_a_rock():
    check('count_paths(["#.", ".."])', count_paths(["#.", ".."]), 0)


def test_finish_is_a_rock():
    check('count_paths(["..", ".#"])', count_paths(["..", ".#"]), 0)


def test_single_cell():
    check('count_paths(["."])', count_paths(["."]), 1)


def test_empty_map():
    check('count_paths([])', count_paths([]), 0)
