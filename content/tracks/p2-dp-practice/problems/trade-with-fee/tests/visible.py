from anneal_prelude import check, ensure
from solution import best_profit_with_fee


def test_several_trades():
    check('best_profit_with_fee([1, 3, 2, 8, 4, 9], 2)', best_profit_with_fee([1, 3, 2, 8, 4, 9], 2), 8)


def test_prices_only_fall():
    check('best_profit_with_fee([5, 4, 3], 1)', best_profit_with_fee([5, 4, 3], 1), 0)


def test_one_day():
    check('best_profit_with_fee([7], 1)', best_profit_with_fee([7], 1), 0)


def test_fee_too_big():
    check('best_profit_with_fee([1, 3], 5)', best_profit_with_fee([1, 3], 5), 0)


def test_no_fee_takes_every_rise():
    check('best_profit_with_fee([1, 3, 2, 8, 4, 9], 0)', best_profit_with_fee([1, 3, 2, 8, 4, 9], 0), 13)


def test_empty():
    check('best_profit_with_fee([], 1)', best_profit_with_fee([], 1), 0)
