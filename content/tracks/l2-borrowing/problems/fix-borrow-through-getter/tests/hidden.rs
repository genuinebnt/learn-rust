use solution::*;

#[test]
fn empty_shop() {
    let mut s = Shop::new(vec![], 50);
    check!(r#"no items"#, (flag_expensive(&mut s, 0), s.sale(0), s.log().len()), (0, 0, 0));
}

#[test]
fn sale_then_flag() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    s.sale(0);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; sale from 0; flag above 35"#, (flag_expensive(&mut s, 35), s.log().len()), (2, 5));
}

#[test]
fn zero_discount() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 0);
    check!(r#"discount 0; sale"#, (s.sale(0), s.items()[2].price), (0, 300));
}

#[test]
fn full_discount() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 100);
    check!(r#"discount 100; sale from 40"#, (s.sale(40), s.items().iter().map(|i| i.price).collect::<Vec<_>>()), (2, vec![5, 0, 0]));
}

#[test]
fn sale_twice() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; sale from 300 twice"#, (s.sale(300), s.sale(300), s.items()[2].price), (1, 0, 270));
}

#[test]
fn big_price() {
    let mut s = Shop::new(vec![shop::Item { name: "x".into(), price: 42949672 }], 50);
    check!(r#"price u32::MAX / 100, discount 50"#, (s.sale(0), s.items()[0].price), (1, 21474836));
}

#[test]
fn flag_none() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; flag above 1000"#, (flag_expensive(&mut s, 1000), s.log().len()), (0, 0));
}

#[test]
fn log_keeps_order() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    flag_expensive(&mut s, 0);
    flag_expensive(&mut s, 100);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; flag above 0; flag above 100"#, s.log().to_vec(), ["expensive: pen", "expensive: lamp", "expensive: desk", "expensive: desk"].map(String::from).to_vec());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6229);
    for _ in 0..300 {
        let n = rng.below(6);
        let prices: Vec<u32> = rng.vec(n, 0, 200);
        let disc = rng.below(101) as u32;
        let (min, limit) = (rng.below(200) as u32, rng.below(200) as u32);
        let mut s = Shop::new(prices.iter().enumerate().map(|(i, &p)| shop::Item { name: format!("i{i}"), price: p }).collect(), disc);
        let mut log = Vec::new();
        let mut changed = 0;
        let mut after = prices.clone();
        for (i, p) in after.iter_mut().enumerate() {
            if *p >= min {
                let new = *p - *p * disc / 100;
                log.push(format!("i{i}: {p} -> {new}"));
                if new != *p {
                    changed += 1;
                }
                *p = new;
            }
        }
        let mut flagged = 0;
        for (i, p) in after.iter().enumerate() {
            if *p > limit {
                log.push(format!("expensive: i{i}"));
                flagged += 1;
            }
        }
        let got = (s.sale(min), flag_expensive(&mut s, limit));
        let got_prices: Vec<u32> = s.items().iter().map(|i| i.price).collect();
        check!(format!("prices {prices:?}, discount {disc}; sale({min}); flag_expensive({limit})"), (got, got_prices, s.log().to_vec()), ((changed, flagged), after, log));
    }
}
