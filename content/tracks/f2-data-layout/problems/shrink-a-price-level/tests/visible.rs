use solution::*;

#[test]
fn level_is_32_bytes() {
    check!(r#"size_of::<PriceLevel>()"#, std::mem::size_of::<PriceLevel>(), 32);
}

#[test]
fn price_time_priority() {
    let mut book = Book::new("ETH-USD");
    let _a = book.add(Side::Ask, 101, 5, 1);
    let b = book.add(Side::Ask, 100, 3, 2);
    let c = book.add(Side::Ask, 100, 4, 3);
    let fills = book.execute(Side::Bid, 6, 4);
    check!(r#"asks: a 5 @ 101, b 3 @ 100, c 4 @ 100; execute(Bid, 6)"#, (fills, book.best(Side::Ask).map(|l| (l.price(), l.qty(), l.count())), book.orders_at(Side::Ask, 100)), (vec![Fill { maker: b, price: 100, qty: 3 }, Fill { maker: c, price: 100, qty: 3 }], Some((100, 1, 1)), vec![(c, 1)]));
}

#[test]
fn cancel_from_the_middle() {
    let mut book = Book::new("ETH-USD");
    let x = book.add(Side::Bid, 99, 1, 1);
    let y = book.add(Side::Bid, 99, 2, 2);
    let z = book.add(Side::Bid, 99, 3, 3);
    let first = book.cancel(y, 7);
    let second = book.cancel(y, 8);
    check!(r#"bids x, y, z at 99 (qty 1, 2, 3); cancel y twice"#, (first, second, book.orders_at(Side::Bid, 99), book.level(Side::Bid, 99).map(|l| (l.qty(), l.count(), l.last_update()))), (true, false, vec![(x, 1), (z, 3)], Some((4, 2, Some(7)))));
}

#[test]
fn no_allocation_at_a_level() {
    let mut book = Book::with_capacity("ETH-USD", 1000);
    book.add(Side::Bid, 100, 1, 0);
    let mut ids = Vec::with_capacity(600);
    let (_, n) = anneal_prelude::allocs(|| {
        for t in 0..500 {
            ids.push(book.add(Side::Bid, 100, 1 + t % 7, t));
        }
        for i in 0..200 {
            book.cancel(ids[i * 2], 600);
        }
        for t in 0..100 {
            book.add(Side::Bid, 100, 2, 700 + t);
        }
    });
    check!(r#"with_capacity(1000): first order at 100, then 500 adds, 200 cancels, 100 adds at 100: allocations"#, (n.count, book.len(), book.level(Side::Bid, 100).map(|l| l.count())), (0, 401, Some(401)));
}

#[test]
fn symbol_and_empty_book() {
    let mut book = Book::new("ETH-USD");
    let fills = book.execute(Side::Ask, 5, 1);
    check!(r#"Book::new("ETH-USD"), then execute(Ask, 5)"#, (book.symbol(), book.best(Side::Bid).is_none(), book.is_empty(), fills), ("ETH-USD", true, true, vec![]));
}

#[test]
fn partial_fill_keeps_its_place() {
    let mut book = Book::new("ETH-USD");
    let a = book.add(Side::Ask, 100, 5, 1);
    let fills = book.execute(Side::Bid, 2, 2);
    let b = book.add(Side::Ask, 100, 1, 3);
    check!(r#"ask a 5 @ 100; execute(Bid, 2); then ask b 1 @ 100"#, (fills, book.orders_at(Side::Ask, 100)), (vec![Fill { maker: a, price: 100, qty: 2 }], vec![(a, 3), (b, 1)]));
}
