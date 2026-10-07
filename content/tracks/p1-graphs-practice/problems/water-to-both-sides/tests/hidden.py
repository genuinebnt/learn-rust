import random

from anneal_prelude import check, ensure
from solution import drains_to_both


def test_a_ridge_in_the_middle():
    check('drains_to_both([[1, 5, 1]])', drains_to_both([[1, 5, 1]]), [(0, 1)])


def test_a_valley_traps_the_water():
    check('drains_to_both([[5, 1, 5]])', drains_to_both([[5, 1, 5]]), [])


def test_two_rows():
    check('drains_to_both([[3, 3, 3], [1, 1, 1]])', drains_to_both([[3, 3, 3], [1, 1, 1]]), [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)])


def test_empty():
    check('drains_to_both([])', drains_to_both([]), [])


def test_flat_row():
    check('drains_to_both([[2, 2, 2]])', drains_to_both([[2, 2, 2]]), [(0, 0), (0, 1), (0, 2)])


def test_descending_row():
    check('drains_to_both([[3, 2, 1]])', drains_to_both([[3, 2, 1]]), [(0, 0)])


def test_single_column_tower():
    check('drains_to_both([[4], [3], [2], [1]])', drains_to_both([[4], [3], [2], [1]]), [(0, 0), (1, 0), (2, 0), (3, 0)])


def reference(h):
    rows, cols = len(h), len(h[0]) if h else 0

    def reaches(r, c, want_col):
        seen, stack = {(r, c)}, [(r, c)]
        while stack:
            x, y = stack.pop()
            if y == want_col:
                return True
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= n[0] < rows and 0 <= n[1] < cols and n not in seen and h[n[0]][n[1]] <= h[x][y]:
                    seen.add(n)
                    stack.append(n)
        return False

    return [(r, c) for r in range(rows) for c in range(cols) if reaches(r, c, 0) and reaches(r, c, cols - 1)]


def test_random_maps_against_a_search_from_every_cell():
    rng = random.Random(21)
    for _ in range(250):
        rows, cols = rng.randint(1, 5), rng.randint(1, 6)
        h = [[rng.randint(1, 4) for _ in range(cols)] for _ in range(rows)]
        check(f"drains_to_both({h})", drains_to_both([row[:] for row in h]), reference(h))
