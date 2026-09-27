use solution::*;

#[test]
fn one_spare_hour() {
    check!(r#"[30,11,23,4,20], 6 hours"#, min_eating_speed(&[30, 11, 23, 4, 20], 6), Some(23));
}

#[test]
fn impossible() {
    check!(r#"[1,1,1], 2 hours"#, min_eating_speed(&[1, 1, 1], 2), None);
}

#[test]
fn huge_pile() {
    check!(r#"[10⁹], 2 hours"#, min_eating_speed(&[1_000_000_000], 2), Some(500_000_000));
}

#[test]
fn many_piles() {
    let v = vec![1_000_000_000u32; 100_000];
    check!(r#"10⁵ piles of 10⁹, 10¹⁴ hours"#, min_eating_speed(&v, 100_000_000_000_000), Some(1));
}
