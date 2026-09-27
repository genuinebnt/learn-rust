use solution::*;

#[test]
fn two_values() {
    check!(r#"0..=1, always true"#, last_true(0, 1, |_| true), Some(1));
}

#[test]
fn none() {
    check!(r#"5..=9, never true"#, last_true(5, 9, |_| false), None);
}

#[test]
fn top_of_range() {
    check!(r#"u32::MAX - 1..=u32::MAX, always true"#, last_true(u32::MAX - 1, u32::MAX, |_| true), Some(u32::MAX));
}

#[test]
fn whole_range_true() {
    check!(r#"0..=u32::MAX, always true"#, last_true(0, u32::MAX, |_| true), Some(u32::MAX));
}

#[test]
fn boundary_at_2_31() {
    check!(r#"0..=u32::MAX, x < 2³¹"#, last_true(0, u32::MAX, |x| x < 2_147_483_648), Some(2_147_483_647));
}

#[test]
fn only_lo_true() {
    check!(r#"0..=u32::MAX, x == 0"#, last_true(0, u32::MAX, |x| x == 0), Some(0));
}

#[test]
fn few_calls() {
    let calls = std::cell::Cell::new(0);
    let found = last_true(0, u32::MAX, |x| {
        calls.set(calls.get() + 1);
        x <= 2_147_483_648
    });
    check!(r#"0..=u32::MAX, x ≤ 2³¹; count pred calls"#, (found, calls.get() <= 34), (Some(2_147_483_648), true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(415);
    for i in 0..400 {
        let lo = if i % 2 == 0 { rng.int(0, 50) as u32 } else { u32::MAX - rng.int(0, 50) as u32 };
        let hi = lo.saturating_add(rng.int(0, 20) as u32);
        let edge = lo.saturating_add(rng.int(0, 25) as u32).saturating_sub(2);
        let pred = |x: u32| x <= edge;
        let want = (lo..=hi).filter(|&x| pred(x)).last();
        check!(format!("lo = {lo}, hi = {hi}, pred = x <= {edge}"), last_true(lo, hi, pred), want);
    }
}
