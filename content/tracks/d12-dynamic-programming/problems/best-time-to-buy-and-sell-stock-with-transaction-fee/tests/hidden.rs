use solution::*;

#[test]
fn empty() {
    check!(r#"prices = [], fee = 0"#, max_profit(&[], 0), 0);
}

#[test]
fn break_even() {
    check!(r#"prices = [1, 5], fee = 4"#, max_profit(&[1, 5], 4), 0);
}

#[test]
fn just_worth_it() {
    check!(r#"prices = [1, 5], fee = 3"#, max_profit(&[1, 5], 3), 1);
}

#[test]
fn falling() {
    check!(r#"prices = [9, 8, 7, 1, 2], fee = 3"#, max_profit(&[9, 8, 7, 1, 2], 3), 0);
}

#[test]
fn hold_through_dips() {
    check!(r#"prices = [4, 5, 2, 4, 3, 3, 1, 2, 5, 4], fee = 1"#, max_profit(&[4, 5, 2, 4, 3, 3, 1, 2, 5, 4], 1), 4);
}

#[test]
fn big_values() {
    check!(r#"prices = [0, 50000] × 1000, fee = 1"#, max_profit(&[0u32, 50_000].repeat(1000), 1), 49_999_000);
}

#[test]
fn huge_fee() {
    check!(r#"prices = [0, 50000], fee = 50000"#, max_profit(&[0, 50_000], 50_000), 0);
}

#[test]
fn random_vs_brute_force() {
    fn best(p: &[u32], fee: i64, holding: bool) -> i64 {
        match p {
            [] => 0,
            [x, rest @ ..] => {
                let x = *x as i64;
                let wait = best(rest, fee, holding);
                if holding { wait.max(x - fee + best(rest, fee, false)) } else { wait.max(-x + best(rest, fee, true)) }
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(1237);
    for _ in 0..300 {
        let n = rng.below(11);
        let prices: Vec<u32> = rng.vec(n, 0, 9);
        let fee = rng.int(0, 4) as u32;
        check!(format!("prices = {prices:?}, fee = {fee}"), max_profit(&prices, fee), best(&prices, fee as i64, false) as u64);
    }
}

#[test]
fn scale_200k() {
    let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
    check!("prices[i] = (7919·i) % 10000, 200000 days, fee = 50", max_profit(&prices, 50), 327_507_780);
}
