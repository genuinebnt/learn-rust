import random

from anneal_prelude import check, ensure
from solution import paint_region


def test_corner_to_corner_snake():
    check('paint_region([[1, 1, 1], [0, 0, 1], [1, 1, 1]], 0, 0, 8)', paint_region([[1, 1, 1], [0, 0, 1], [1, 1, 1]], 0, 0, 8), [[8, 8, 8], [0, 0, 8], [8, 8, 8]])


def test_click_in_the_middle():
    check('paint_region([[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1, 1, 5)', paint_region([[0, 0, 0], [0, 1, 0], [0, 0, 0]], 1, 1, 5), [[0, 0, 0], [0, 5, 0], [0, 0, 0]])


def test_click_on_a_border_cell():
    check('paint_region([[1, 0], [1, 0]], 1, 1, 2)', paint_region([[1, 0], [1, 0]], 1, 1, 2), [[1, 2], [1, 2]])


def test_painting_zero():
    check('paint_region([[3, 3], [3, 3]], 1, 0, 0)', paint_region([[3, 3], [3, 3]], 1, 0, 0), [[0, 0], [0, 0]])


def test_paint_into_a_neighbouring_colour():
    check('paint_region([[1, 2], [1, 2]], 0, 0, 2)', paint_region([[1, 2], [1, 2]], 0, 0, 2), [[2, 2], [2, 2]])


def test_the_input_is_not_changed():
    picture = [[1, 1], [1, 0]]
    before = [row[:] for row in picture]
    paint_region(picture, 0, 0, 9)
    check("the picture passed in", picture, before)


def test_random_pictures_against_a_set_based_reference():
    rng = random.Random(3)
    for _ in range(200):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        picture = [[rng.randint(0, 2) for _ in range(cols)] for _ in range(rows)]
        r, c, colour = rng.randrange(rows), rng.randrange(cols), rng.randint(0, 3)
        old = picture[r][c]
        region, frontier = {(r, c)}, [(r, c)]
        while frontier:
            x, y = frontier.pop()
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= n[0] < rows and 0 <= n[1] < cols and n not in region and picture[n[0]][n[1]] == old:
                    region.add(n)
                    frontier.append(n)
        want = [[colour if (i, j) in region else picture[i][j] for j in range(cols)] for i in range(rows)]
        check(f"paint_region({picture}, {r}, {c}, {colour})", paint_region([row[:] for row in picture], r, c, colour), want)


def test_a_large_picture_is_fast():
    picture = [[0] * 200 for _ in range(200)]
    out = paint_region(picture, 100, 100, 1)
    check("sum of a fully repainted 200 x 200 picture", sum(map(sum, out)), 200 * 200)
