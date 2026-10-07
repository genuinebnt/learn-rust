from anneal_prelude import check, ensure
from solution import Ledger

from solution import Ledger


def test_the_example():
    ledger = Ledger()
    ledger.add(3, 100)
    ledger.add(7, -40)
    check("ledger.balance_on(5)", ledger.balance_on(5), 100)
    check("ledger.balance_on(7)", ledger.balance_on(7), 60)
    check("ledger.balance_on(2)", ledger.balance_on(2), 0)


def test_an_empty_ledger():
    check("Ledger().balance_on(10)", Ledger().balance_on(10), 0)


def test_a_day_with_a_transaction_includes_it():
    ledger = Ledger()
    ledger.add(5, 25)
    check("ledger.balance_on(5)", ledger.balance_on(5), 25)


def test_a_query_far_in_the_future():
    ledger = Ledger()
    ledger.add(1, 10)
    ledger.add(2, 20)
    check("ledger.balance_on(10**9)", ledger.balance_on(10**9), 30)


def test_the_balance_can_go_negative():
    ledger = Ledger()
    ledger.add(1, 10)
    ledger.add(4, -25)
    check("ledger.balance_on(4)", ledger.balance_on(4), -15)
