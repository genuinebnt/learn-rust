from anneal_prelude import check, ensure
from solution import fewest_knight_moves


def test_one_jump():
    check('fewest_knight_moves((0, 0), (1, 2))', fewest_knight_moves((0, 0), (1, 2)), 1)


def test_already_there():
    check('fewest_knight_moves((3, 3), (3, 3))', fewest_knight_moves((3, 3), (3, 3)), 0)


def test_opposite_corners():
    check('fewest_knight_moves((0, 0), (7, 7))', fewest_knight_moves((0, 0), (7, 7)), 6)


def test_adjacent_square_takes_three():
    check('fewest_knight_moves((0, 0), (0, 1))', fewest_knight_moves((0, 0), (0, 1)), 3)


def test_tiny_board_unreachable():
    check('fewest_knight_moves((0, 0), (1, 1), 2)', fewest_knight_moves((0, 0), (1, 1), 2), -1)


def test_one_by_one():
    check('fewest_knight_moves((0, 0), (0, 0), 1)', fewest_knight_moves((0, 0), (0, 0), 1), 0)
