use solution::*;

#[test]
fn single() {
    check!(r#"xs = [5.0]"#, { let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[5.0]); (s.values, s.total, s.max) }, (vec![5.0], 5.0, 5.0));
}

#[test]
fn appends_to_existing() {
    check!(r#"values [1.0], xs = [2.0, 3.0]"#, { let mut s = Stats { values: vec![1.0], total: 1.0, max: 1.0 }; s.record_all(&[2.0, 3.0]); s.values }, vec![1.0, 2.0, 3.0]);
}

#[test]
fn max_from_xs() {
    check!(r#"max 0.0, xs = [0.5, 0.25]"#, { let mut s = Stats { values: vec![], total: 0.0, max: 0.0 }; s.record_all(&[0.5, 0.25]); s.max }, 0.5);
}

#[test]
fn order_kept() {
    check!(r#"xs = [3.0, 1.0, 2.0]"#, { let mut s = Stats { values: vec![], total: 0.0, max: 0.0 }; s.record_all(&[3.0, 1.0, 2.0]); s.values }, vec![3.0, 1.0, 2.0]);
}

#[test]
fn duplicates() {
    check!(r#"xs = [2.0, 2.0]"#, { let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[2.0, 2.0]); (s.values.len(), s.total, s.max) }, (2, 4.0, 2.0));
}

#[test]
fn many() {
    check!(r#"1000 × 1.0"#, { let mut s = Stats { values: vec![], total: 0.0, max: 0.0 }; s.record_all(&vec![1.0; 1000]); (s.values.len(), s.total, s.max) }, (1000, 1000.0, 1.0));
}

#[test]
fn called_twice() {
    check!(r#"xs = [1.0], then [4.0]"#, { let mut s = Stats { values: vec![], total: 0.0, max: f64::MIN }; s.record_all(&[1.0]); s.record_all(&[4.0]); (s.values, s.total, s.max) }, (vec![1.0, 4.0], 5.0, 4.0));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2024);
    for _ in 0..300 {
        let n0 = rng.below(4);
        let v0: Vec<f64> = (0..n0).map(|_| rng.int(-50, 50) as f64).collect();
        let total0 = rng.int(-100, 100) as f64;
        let max0 = rng.int(-60, 60) as f64;
        let k = rng.below(6);
        let xs: Vec<f64> = (0..k).map(|_| rng.int(-50, 50) as f64).collect();
        let mut s = Stats { values: v0.clone(), total: total0, max: max0 };
        s.record_all(&xs);
        let mut values = v0.clone();
        values.extend(&xs);
        let want = (values, total0 + xs.iter().sum::<f64>(), xs.iter().fold(max0, |m, &x| m.max(x)));
        check!(format!("values {v0:?}, total {total0}, max {max0}, xs = {xs:?}"), (s.values, s.total, s.max), want);
    }
}
