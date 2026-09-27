use solution::*;

#[test]
fn flag_expensive_example() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; flag above 30"#, (flag_expensive(&mut s, 30), s.log().to_vec()), (2, vec!["expensive: lamp".to_string(), "expensive: desk".to_string()]));
}

#[test]
fn sale_example() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; sale from 40"#, (s.sale(40), s.items().iter().map(|i| i.price).collect::<Vec<_>>(), s.log().to_vec()), (2, vec![5, 36, 270], vec!["lamp: 40 -> 36".to_string(), "desk: 300 -> 270".to_string()]));
}

#[test]
fn sale_rounds_down() {
    let mut s = Shop::new(vec![shop::Item { name: "x".into(), price: 15 }], 10);
    check!(r#"price 15, discount 10%"#, (s.sale(0), s.items()[0].price), (1, 14));
}

#[test]
fn unchanged_price_not_counted() {
    let mut s = Shop::new(vec![shop::Item { name: "x".into(), price: 5 }], 10);
    check!(r#"price 5, discount 10%"#, (s.sale(0), s.log().to_vec()), (0, vec!["x: 5 -> 5".to_string()]));
}

#[test]
fn limit_is_strict() {
    let mut s = Shop::new(vec![shop::Item { name: "pen".into(), price: 5 }, shop::Item { name: "lamp".into(), price: 40 }, shop::Item { name: "desk".into(), price: 300 }], 10);
    check!(r#"pen 5, lamp 40, desk 300; discount 10%; flag above 40"#, flag_expensive(&mut s, 40), 1);
}
