import random

from anneal_prelude import check, ensure
from solution import enclosed_lake_tiles


def test_two_separate_lakes():
    check('enclosed_lake_tiles([".......", ".~.~~..", ".......", "......."])', enclosed_lake_tiles([".......", ".~.~~..", ".......", "......."]), 3)


def test_diagonal_water_is_separate():
    check('enclosed_lake_tiles(["...", ".~.", "..."])', enclosed_lake_tiles(["...", ".~.", "..."]), 1)


def test_border_touch_only_at_a_corner_tile():
    check('enclosed_lake_tiles(["~..", "...", "..."])', enclosed_lake_tiles(["~..", "...", "..."]), 0)


def test_empty():
    check('enclosed_lake_tiles([])', enclosed_lake_tiles([]), 0)


def test_a_ring_of_water_around_land():
    check('enclosed_lake_tiles(["......", ".~~~~.", ".~..~.", ".~~~~.", "......"])', enclosed_lake_tiles(["......", ".~~~~.", ".~..~.", ".~~~~.", "......"]), 10)


def test_a_lake_inside_land():
    check('enclosed_lake_tiles(["....", ".~~.", "...."])', enclosed_lake_tiles(["....", ".~~.", "...."]), 2)


def test_one_row_is_all_border():
    check('enclosed_lake_tiles(["~.~"])', enclosed_lake_tiles(["~.~"]), 0)


def reference(m):
    rows, cols = len(m), len(m[0]) if m else 0
    total = 0
    for r in range(rows):
        for c in range(cols):
            if m[r][c] != "~":
                continue
            seen, stack, edge = {(r, c)}, [(r, c)], False
            while stack:
                x, y = stack.pop()
                if x in (0, rows - 1) or y in (0, cols - 1):
                    edge = True
                for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= n[0] < rows and 0 <= n[1] < cols and m[n[0]][n[1]] == "~" and n not in seen:
                        seen.add(n)
                        stack.append(n)
            total += 0 if edge else 1
    return total


def test_random_maps_against_a_per_tile_search():
    rng = random.Random(4)
    for _ in range(200):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        m = ["".join(rng.choice("~.") for _ in range(cols)) for _ in range(rows)]
        check(f"enclosed_lake_tiles({m})", enclosed_lake_tiles(m), reference(m))
