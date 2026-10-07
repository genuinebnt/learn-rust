from anneal_prelude import check, ensure
from solution import minutes_to_burn


def test_two_fires():
    check('minutes_to_burn(["F..", "...", "..F"])', minutes_to_burn(["F..", "...", "..F"]), 2)


def test_one_fire_in_a_row():
    check('minutes_to_burn(["F...."])', minutes_to_burn(["F...."]), 4)


def test_no_grass():
    check('minutes_to_burn(["F#", "#F"])', minutes_to_burn(["F#", "#F"]), 0)


def test_fenced_off_grass():
    check('minutes_to_burn(["F#.", "###"])', minutes_to_burn(["F#.", "###"]), -1)


def test_no_fire_but_grass():
    check('minutes_to_burn(["..."])', minutes_to_burn(["..."]), -1)


def test_detour():
    check('minutes_to_burn(["F#.", "...", "..."])', minutes_to_burn(["F#.", "...", "..."]), 4)
