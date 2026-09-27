use solution::*;

#[test]
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn late_low() {
    check!(r#"prices = [2, 4, 1]"#, max_profit(&[2, 4, 1]), 2);
}

#[test]
fn single() {
    check!(r#"prices = [5]"#, max_profit(&[5]), 0);
}

#[test]
fn flat() {
    check!(r#"prices = [3, 3, 3]"#, max_profit(&[3, 3, 3]), 0);
}

#[test]
fn rising() {
    check!(r#"prices = [1, 2, 3, 4, 5]"#, max_profit(&[1, 2, 3, 4, 5]), 4);
}

#[test]
fn low_after_high() {
    check!(r#"prices = [3, 8, 1, 5]"#, max_profit(&[3, 8, 1, 5]), 5);
}

#[test]
fn extremes() {
    check!(r#"prices = [0, u32::MAX]"#, max_profit(&[0, u32::MAX]), u32::MAX);
}

#[test]
fn extremes_falling() {
    check!(r#"prices = [u32::MAX, 0]"#, max_profit(&[u32::MAX, 0]), 0);
}

#[test]
fn new_low_then_bigger_gain() {
    check!(r#"prices = [5, 7, 1, 9]"#, max_profit(&[5, 7, 1, 9]), 8);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(211);
    for _ in 0..300 {
        let n = rng.below(12);
        let prices: Vec<u32> = rng.vec(n, 0, 30);
        let mut want = 0;
        for i in 0..n {
            for j in i + 1..n {
                want = want.max(prices[j].saturating_sub(prices[i]));
            }
        }
        check!(format!("prices = {prices:?}"), max_profit(&prices), want);
    }
}

#[test]
fn scale_200k() {
    let mut prices: Vec<u32> = (0..200_000).map(|i| 1_000_000 - i).collect();
    prices.push(1_000_000);
    check!("prices = 1000000 down to 800001, then 1000000", max_profit(&prices), 199_999);
}
