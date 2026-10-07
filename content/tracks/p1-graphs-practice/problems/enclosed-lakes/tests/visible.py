from anneal_prelude import check, ensure
from solution import enclosed_lake_tiles


def test_one_lake_tile():
    check('enclosed_lake_tiles(["~~~~~", "~...~", "~.~.~", "~...~", "~~~~~"])', enclosed_lake_tiles(["~~~~~", "~...~", "~.~.~", "~...~", "~~~~~"]), 1)


def test_no_water():
    check('enclosed_lake_tiles(["...", "..."])', enclosed_lake_tiles(["...", "..."]), 0)


def test_all_border_water():
    check('enclosed_lake_tiles(["~~", "~~"])', enclosed_lake_tiles(["~~", "~~"]), 0)


def test_lake_with_two_tiles():
    check('enclosed_lake_tiles([".....", ".~~..", ".....", "....."])', enclosed_lake_tiles([".....", ".~~..", ".....", "....."]), 2)


def test_connected_to_the_edge_by_a_channel():
    check('enclosed_lake_tiles([".~...", ".~~..", "....."])', enclosed_lake_tiles([".~...", ".~~..", "....."]), 0)
