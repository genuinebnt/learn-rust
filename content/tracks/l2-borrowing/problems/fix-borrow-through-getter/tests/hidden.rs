use solution::*;

#[test]
fn all_expensive() {
    check!(r#"items [100, 200], limit 0"#, { let mut s = Shop::new(vec![100, 200]); s.log_expensive(0); s.log().to_vec() }, vec!["expensive: 100", "expensive: 200"]);
}

#[test]
fn limit_near_max() {
    check!(r#"items [u32::MAX], limit u32::MAX - 1"#, { let mut s = Shop::new(vec![u32::MAX]); s.log_expensive(u32::MAX - 1); s.log().to_vec() }, vec!["expensive: 4294967295"]);
}

#[test]
fn limit_max() {
    check!(r#"items [u32::MAX], limit u32::MAX"#, { let mut s = Shop::new(vec![u32::MAX]); s.log_expensive(u32::MAX); s.log().len() }, 0);
}

#[test]
fn duplicates() {
    check!(r#"items [7, 7], limit 6"#, { let mut s = Shop::new(vec![7, 7]); s.log_expensive(6); s.log().len() }, 2);
}

#[test]
fn called_twice() {
    check!(r#"items [9], limit 5, twice"#, { let mut s = Shop::new(vec![9]); s.log_expensive(5); s.log_expensive(5); s.log().to_vec() }, vec!["expensive: 9", "expensive: 9"]);
}

#[test]
fn zero_price() {
    check!(r#"items [0], limit 0"#, { let mut s = Shop::new(vec![0]); s.log_expensive(0); s.log().len() }, 0);
}

#[test]
fn many() {
    check!(r#"items 0..10000, limit 4999"#, { let mut s = Shop::new((0..10_000).collect()); s.log_expensive(4999); (s.log().len(), s.log()[0].clone()) }, (5000, "expensive: 5000".to_string()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2026);
    for _ in 0..300 {
        let n = rng.below(8);
        let items: Vec<u32> = rng.vec(n, 0, 20);
        let limit = rng.int(0, 20) as u32;
        let want: Vec<String> = items.iter().filter(|&&p| p > limit).map(|p| format!("expensive: {p}")).collect();
        let mut s = Shop::new(items.clone());
        s.log_expensive(limit);
        check!(format!("items {items:?}, limit {limit}"), s.log().to_vec(), want);
    }
}
