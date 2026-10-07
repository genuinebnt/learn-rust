import random

from anneal_prelude import check, ensure
from solution import fewest_knight_moves


def test_two_jumps():
    check('fewest_knight_moves((0, 0), (2, 0))', fewest_knight_moves((0, 0), (2, 0)), 2)


def test_corner_to_corner_of_a_three_by_three():
    check('fewest_knight_moves((0, 0), (2, 2), 3)', fewest_knight_moves((0, 0), (2, 2), 3), 4)


def test_center_of_three_by_three_is_cut_off():
    check('fewest_knight_moves((0, 0), (1, 1), 3)', fewest_knight_moves((0, 0), (1, 1), 3), -1)


def test_same_square_on_a_big_board():
    check('fewest_knight_moves((50, 60), (50, 60), 200)', fewest_knight_moves((50, 60), (50, 60), 200), 0)


def test_two_diagonal_squares_away():
    check('fewest_knight_moves((0, 0), (3, 3))', fewest_knight_moves((0, 0), (3, 3)), 2)


def reference(start, goal, size):
    dist = {start: 0}
    frontier = [start]
    while frontier:
        nxt = []
        for r, c in frontier:
            for dr, dc in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
                n = (r + dr, c + dc)
                if 0 <= n[0] < size and 0 <= n[1] < size and n not in dist:
                    dist[n] = dist[(r, c)] + 1
                    nxt.append(n)
        frontier = nxt
    return dist.get(goal, -1)


def test_every_pair_on_a_five_by_five_board():
    size = 5
    cells = [(r, c) for r in range(size) for c in range(size)]
    for start in cells[::3]:
        for goal in cells:
            check(f"fewest_knight_moves({start}, {goal}, {size})", fewest_knight_moves(start, goal, size), reference(start, goal, size))


def test_random_pairs_on_random_boards():
    rng = random.Random(31)
    for _ in range(200):
        size = rng.randint(1, 9)
        start = (rng.randrange(size), rng.randrange(size))
        goal = (rng.randrange(size), rng.randrange(size))
        check(f"fewest_knight_moves({start}, {goal}, {size})", fewest_knight_moves(start, goal, size), reference(start, goal, size))


def test_a_big_board_is_fast():
    check("fewest_knight_moves((0, 0), (199, 199), 200)", fewest_knight_moves((0, 0), (199, 199), 200), reference((0, 0), (199, 199), 200))
