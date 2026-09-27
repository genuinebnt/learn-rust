use solution::*;

#[test]
fn drop_everything() {
    let mut c = Cart::new();
    check!(r#"add 3, 4; drop_above 0"#, { c.add(3); c.add(4); (c.drop_above(0), c.items(), c.total()) }, (2, vec![], 0));
}

#[test]
fn zero_price() {
    let mut c = Cart::new();
    check!(r#"add 0; double"#, { c.add(0); c.double_all(); (c.total(), c.log()) }, (0, ["[1] add 0", "[1] double 0 -> 0"].map(String::from).to_vec()));
}

#[test]
fn add_after_drop() {
    let mut c = Cart::new();
    check!(r#"add 9, 1; drop_above 5; add 2"#, { c.add(9); c.add(1); c.drop_above(5); c.add(2); c.log() }, ["[1] add 9", "[2] add 1", "[2] drop 9", "[2] add 2"].map(String::from).to_vec());
}

#[test]
fn keeps_order() {
    let mut c = Cart::new();
    check!(r#"add 1, 9, 2, 8, 3; drop_above 5"#, { for p in [1, 9, 2, 8, 3] { c.add(p); } c.drop_above(5); c.items() }, vec![1, 2, 3]);
}

#[test]
fn large_prices() {
    let mut c = Cart::new();
    check!(r#"add 1 << 30; double"#, { c.add(1 << 30); c.double_all(); (c.total(), c.items()) }, (1 << 31, vec![1 << 31]));
}

#[test]
fn readers_side_by_side() {
    let mut c = Cart::new();
    check!(r#"add 2; items, total and log read together"#, { c.add(2); let (i, t, l) = (c.items(), c.total(), c.log()); (i, t, l.len()) }, (vec![2], 2, 1));
}

#[test]
fn double_then_drop() {
    let mut c = Cart::new();
    check!(r#"add 3, 6; double; drop_above 10"#, { c.add(3); c.add(6); c.double_all(); (c.drop_above(10), c.items(), c.total()) }, (1, vec![6], 6));
}

#[test]
fn log_count_is_before_dropping() {
    let mut c = Cart::new();
    check!(r#"add 20, 30, 40; drop_above 25"#, { for p in [20, 30, 40] { c.add(p); } c.drop_above(25); c.log()[3..].to_vec() }, ["[3] drop 30", "[3] drop 40"].map(String::from).to_vec());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6235);
    for _ in 0..300 {
        let mut c = Cart::new();
        let (mut items, mut log): (Vec<u32>, Vec<String>) = (vec![], vec![]);
        let mut ops = Vec::new();
        for _ in 0..8 {
            match rng.below(3) {
                0 => {
                    let p = rng.below(20) as u32;
                    c.add(p);
                    items.push(p);
                    log.push(format!("[{}] add {p}", items.len()));
                    ops.push(format!("add {p}"));
                }
                1 => {
                    c.double_all();
                    let n = items.len();
                    for p in items.iter_mut() {
                        log.push(format!("[{n}] double {p} -> {}", *p * 2));
                        *p *= 2;
                    }
                    ops.push("double_all".to_string());
                }
                _ => {
                    let max = rng.below(30) as u32;
                    let n = items.len();
                    let before = items.len();
                    for p in items.iter().filter(|&&p| p > max) {
                        log.push(format!("[{n}] drop {p}"));
                    }
                    items.retain(|&p| p <= max);
                    ops.push(format!("drop_above {max}"));
                    check!(ops.join(", "), c.drop_above(max), before - items.len());
                }
            }
        }
        let total: u32 = items.iter().sum();
        check!(format!("{}; state", ops.join(", ")), (c.items(), c.total(), c.log()), (items, total, log));
    }
}

#[test]
fn big_cart() {
    let mut c = Cart::new();
    for i in 0..100_000 {
        c.add(i % 10);
    }
    c.double_all();
    let dropped = c.drop_above(10);
    check!("100000 items of 0..9, doubled, drop above 10", (dropped, c.total(), c.log().len()), (40_000, 300_000, 240_000));
}
