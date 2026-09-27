use solution::*;

/// The book as a list of resting orders in arrival order, and each level's last update.
#[derive(Default)]
struct Model {
    live: Vec<(OrderId, Side, u32, u64)>,
    touched: std::collections::HashMap<(Side, u32), u64>,
}

impl Model {
    fn gone(&mut self, side: Side, price: u32) {
        if !self.live.iter().any(|o| o.1 == side && o.2 == price) {
            self.touched.remove(&(side, price));
        }
    }

    fn cancel(&mut self, id: OrderId, ts: u64) -> bool {
        let Some(i) = self.live.iter().position(|o| o.0 == id) else {
            return false;
        };
        let (_, side, price, _) = self.live.remove(i);
        self.touched.insert((side, price), ts);
        self.gone(side, price);
        true
    }

    fn execute(&mut self, taker: Side, qty: u64, ts: u64) -> Vec<Fill> {
        let side = taker.opposite();
        let mut left = qty;
        let mut fills = Vec::new();
        while left > 0 {
            let prices = self.live.iter().filter(|o| o.1 == side).map(|o| o.2);
            let best = if side == Side::Bid { prices.max() } else { prices.min() };
            let Some(price) = best else {
                break;
            };
            let i = self.live.iter().position(|o| o.1 == side && o.2 == price).unwrap();
            let take = self.live[i].3.min(left);
            fills.push(Fill { maker: self.live[i].0, price, qty: take });
            left -= take;
            self.touched.insert((side, price), ts);
            if take == self.live[i].3 {
                self.live.remove(i);
                self.gone(side, price);
            } else {
                self.live[i].3 -= take;
            }
        }
        fills
    }

    fn orders_at(&self, side: Side, price: u32) -> Vec<(OrderId, u64)> {
        self.live.iter().filter(|o| o.1 == side && o.2 == price).map(|o| (o.0, o.3)).collect()
    }
}

/// Every level of `book` in 95..=105 against the model: (qty, count, last_update), the queue, the bests.
fn compare(book: &Book, model: &Model, ctx: &str) {
    for side in [Side::Bid, Side::Ask] {
        for price in 95..=105 {
            let got = book.level(side, price).map(|l| (l.price(), l.qty(), l.count(), l.last_update()));
            let queue = model.orders_at(side, price);
            let want = (!queue.is_empty()).then(|| (price, queue.iter().map(|o| o.1).sum::<u64>(), queue.len(), model.touched.get(&(side, price)).copied()));
            check!(format!("{ctx}: level({side:?}, {price})"), got, want);
            check!(format!("{ctx}: orders_at({side:?}, {price})"), book.orders_at(side, price), queue);
        }
        let prices = model.live.iter().filter(|o| o.1 == side).map(|o| o.2);
        let want = if side == Side::Bid { prices.max() } else { prices.min() };
        check!(format!("{ctx}: best({side:?})"), book.best(side).map(|l| l.price()), want);
    }
    check!(format!("{ctx}: len()"), book.len(), model.live.len());
}

#[test]
fn sweep_both_levels() {
    let mut book = Book::new("X");
    book.add(Side::Ask, 100, 2, 1);
    book.add(Side::Ask, 101, 3, 2);
    let fills = book.execute(Side::Bid, 10, 3);
    check!(r#"asks 2 @ 100, 3 @ 101; execute(Bid, 10) takes everything"#, (fills.len(), fills.iter().map(|f| f.qty).sum::<u64>(), book.best(Side::Ask).is_none(), book.len()), (2, 5, true, 0));
}

#[test]
fn best_bid_is_highest() {
    let mut book = Book::new("X");
    for p in [90, 95, 93] {
        book.add(Side::Bid, p, 1, 1);
    }
    check!(r#"bids at 90, 95, 93"#, book.best(Side::Bid).map(|l| l.price()), Some(95));
}

#[test]
fn stale_id_after_reuse() {
    let mut book = Book::new("X");
    let a = book.add(Side::Ask, 50, 4, 1);
    book.cancel(a, 2);
    let b = book.add(Side::Ask, 50, 9, 3);
    let again = book.cancel(a, 4);
    check!(r#"add a, cancel a, add b (reusing a's slot), cancel a again"#, (again, book.orders_at(Side::Ask, 50), book.len(), a != b), (false, vec![(b, 9)], 1, true));
}

#[test]
fn filled_order_cant_cancel() {
    let mut book = Book::new("X");
    let m = book.add(Side::Bid, 10, 5, 1);
    book.execute(Side::Ask, 5, 2);
    check!(r#"bid m 5 @ 10; execute(Ask, 5); cancel m"#, (book.cancel(m, 3), book.len(), book.level(Side::Bid, 10).is_none()), (false, 0, true));
}

#[test]
fn partial_fill_touches_level() {
    let mut book = Book::new("X");
    book.add(Side::Ask, 7, 10, 1);
    book.execute(Side::Bid, 4, 9);
    check!(r#"ask 10 @ 7 at t=1; execute(Bid, 4) at t=9"#, book.level(Side::Ask, 7).map(|l| (l.qty(), l.count(), l.last_update())), Some((6, 1, Some(9))));
}

#[test]
fn extremes() {
    let mut book = Book::new("X");
    book.add(Side::Bid, u32::MAX, 1 << 62, u64::MAX);
    book.add(Side::Ask, 0, 1, 0);
    check!(r#"bid u32::MAX with qty 2⁶²; ask 0 with qty 1"#, (book.best(Side::Bid).map(|l| (l.price(), l.qty())), book.best(Side::Ask).map(|l| l.price())), (Some((u32::MAX, 1 << 62)), Some(0)));
}

#[test]
fn cancel_unknown() {
    let mut other = Book::new("Y");
    other.add(Side::Bid, 1, 1, 1);
    let foreign = other.add(Side::Bid, 1, 1, 1);
    let mut book = Book::new("X");
    book.add(Side::Bid, 1, 1, 1);
    check!(r#"cancel an id from another book"#, (book.cancel(foreign, 1), book.len()), (false, 1));
}

#[test]
fn sides_are_separate() {
    let mut book = Book::new("X");
    book.add(Side::Bid, 100, 3, 1);
    book.add(Side::Ask, 100, 4, 1);
    check!(r#"bid and ask at the same price 100"#, (book.level(Side::Bid, 100).map(|l| l.qty()), book.level(Side::Ask, 100).map(|l| l.qty())), (Some(3), Some(4)));
}

#[test]
fn cancel_is_constant_time() {
    let mut book = Book::with_capacity("X", 100_000);
    let mut ids: Vec<OrderId> = (0..100_000u64).map(|t| book.add(Side::Bid, 500, 1, t)).collect();
    let mut rng = anneal_prelude::Rng::new(8211);
    rng.shuffle(&mut ids);
    let cancelled = ids.iter().filter(|&&id| book.cancel(id, 1)).count();
    check!("100000 orders at one price, cancelled in random order", (cancelled, book.len(), book.best(Side::Bid).is_none()), (100_000, 0, true));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(8210);
    for _ in 0..60 {
        let mut book = Book::new("BTC-USD");
        let mut model = Model::default();
        let mut ever: Vec<OrderId> = Vec::new();
        let mut log = Vec::new();
        for ts in 1..=40u64 {
            let side = if rng.bool() { Side::Bid } else { Side::Ask };
            match rng.below(5) {
                0 | 1 => {
                    let price = rng.int(95, 105) as u32;
                    let qty = rng.int(1, 9) as u64;
                    log.push(format!("add({side:?}, {price}, {qty})"));
                    let id = book.add(side, price, qty, ts);
                    check!(format!("{}: the id is new", log.join(", ")), ever.contains(&id), false);
                    ever.push(id);
                    model.live.push((id, side, price, qty));
                    model.touched.insert((side, price), ts);
                }
                2 | 3 if !ever.is_empty() => {
                    let id = *rng.pick(&ever);
                    log.push(format!("cancel(#{})", ever.iter().position(|&x| x == id).unwrap()));
                    check!(log.join(", "), book.cancel(id, ts), model.cancel(id, ts));
                }
                _ => {
                    let qty = rng.int(1, 25) as u64;
                    log.push(format!("execute({side:?}, {qty})"));
                    check!(log.join(", "), book.execute(side, qty, ts), model.execute(side, qty, ts));
                }
            }
            compare(&book, &model, &log.join(", "));
        }
    }
}
