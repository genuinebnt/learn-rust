from anneal_prelude import check, ensure
from solution import paint_region


def test_bucket_fill():
    check('paint_region([[1, 1, 0], [1, 0, 0], [1, 1, 1]], 0, 0, 7)', paint_region([[1, 1, 0], [1, 0, 0], [1, 1, 1]], 0, 0, 7), [[7, 7, 0], [7, 0, 0], [7, 7, 7]])


def test_same_colour_changes_nothing():
    check('paint_region([[2, 2], [2, 3]], 0, 0, 2)', paint_region([[2, 2], [2, 3]], 0, 0, 2), [[2, 2], [2, 3]])


def test_one_cell():
    check('paint_region([[5]], 0, 0, 9)', paint_region([[5]], 0, 0, 9), [[9]])


def test_stops_at_other_colours():
    check('paint_region([[1, 2, 1]], 0, 0, 4)', paint_region([[1, 2, 1]], 0, 0, 4), [[4, 2, 1]])


def test_diagonal_stays():
    check('paint_region([[1, 0], [0, 1]], 0, 0, 3)', paint_region([[1, 0], [0, 1]], 0, 0, 3), [[3, 0], [0, 1]])
