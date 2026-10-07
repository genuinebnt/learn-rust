import random

from anneal_prelude import check, ensure
from solution import Ledger

from solution import Ledger


def test_before_the_first_day():
    ledger = Ledger()
    ledger.add(10, 5)
    check("ledger.balance_on(9)", ledger.balance_on(9), 0)


def test_between_two_days():
    ledger = Ledger()
    ledger.add(1, 1)
    ledger.add(10, 10)
    check("ledger.balance_on(5)", ledger.balance_on(5), 1)


def test_queries_between_additions():
    ledger = Ledger()
    ledger.add(2, 5)
    check("balance after the first add", ledger.balance_on(10), 5)
    ledger.add(4, 6)
    check("balance after the second add", ledger.balance_on(10), 11)


def test_two_transactions_on_neighbouring_days():
    ledger = Ledger()
    ledger.add(1, 3)
    ledger.add(2, 4)
    check("ledger.balance_on(1)", ledger.balance_on(1), 3)
    check("ledger.balance_on(2)", ledger.balance_on(2), 7)


def test_zero_amounts():
    ledger = Ledger()
    ledger.add(1, 0)
    ledger.add(2, 0)
    check("ledger.balance_on(2)", ledger.balance_on(2), 0)


def test_negative_days_are_fine():
    ledger = Ledger()
    ledger.add(-5, 7)
    ledger.add(-1, 3)
    check("ledger.balance_on(-3)", ledger.balance_on(-3), 7)


def test_random_ledgers_against_a_running_sum():
    rng = random.Random(46)
    for _ in range(100):
        ledger, entries, day = Ledger(), [], 0
        for _ in range(30):
            day += rng.randint(1, 4)
            amount = rng.randint(-50, 50)
            ledger.add(day, amount)
            entries.append((day, amount))
            q = rng.randint(-2, day + 3)
            check(f"ledger.balance_on({q})", ledger.balance_on(q), sum(a for d, a in entries if d <= q))


def test_a_hundred_thousand_transactions_and_questions_are_fast():
    ledger = Ledger()
    for day in range(1, 100_001):
        ledger.add(day, 1)
    total = 0
    for q in range(0, 100_001, 1):
        total += ledger.balance_on(q)
    check("sum of 100001 balance_on answers", total, sum(range(0, 100_001)))
