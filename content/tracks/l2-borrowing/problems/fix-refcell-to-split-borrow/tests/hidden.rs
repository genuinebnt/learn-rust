use solution::*;

#[test]
fn single() {
    check!(r#"add 7; double"#, { let mut c = Cart::new(); c.add(7); c.double_all(); (c.items(), c.total()) }, (vec![14], 14));
}

#[test]
fn zero_price() {
    check!(r#"add 0; double"#, { let mut c = Cart::new(); c.add(0); c.double_all(); (c.items(), c.total()) }, (vec![0], 0));
}

#[test]
fn duplicates() {
    check!(r#"add 3, 3; double"#, { let mut c = Cart::new(); c.add(3); c.add(3); c.double_all(); (c.items(), c.total()) }, (vec![6, 6], 12));
}

#[test]
fn large() {
    check!(r#"add 2^30; double"#, { let mut c = Cart::new(); c.add(1 << 30); c.double_all(); (c.items(), c.total()) }, (vec![1 << 31], 1 << 31));
}

#[test]
fn many() {
    check!(r#"1000 × add 1; double"#, { let mut c = Cart::new(); for _ in 0..1000 { c.add(1); } c.double_all(); (c.items().len(), c.total()) }, (1000, 2000));
}

#[test]
fn new_is_empty() {
    check!(r#"new cart"#, { let c = Cart::new(); (c.items(), c.total()) }, (vec![], 0));
}

#[test]
fn three_doubles() {
    check!(r#"add 1, 2; double 3 times"#, { let mut c = Cart::new(); c.add(1); c.add(2); c.double_all(); c.double_all(); c.double_all(); (c.items(), c.total()) }, (vec![8, 16], 24));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2033);
    for _ in 0..300 {
        let mut c = Cart::new();
        let mut items: Vec<u32> = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(10);
        for _ in 0..n {
            if rng.below(3) == 0 {
                c.double_all();
                items.iter_mut().for_each(|p| *p *= 2);
                log.push("double".to_string());
            } else {
                let p = rng.below(100) as u32;
                c.add(p);
                items.push(p);
                log.push(format!("add {p}"));
            }
        }
        let total: u32 = items.iter().sum();
        check!(log.join(", "), (c.items(), c.total()), (items, total));
    }
}
