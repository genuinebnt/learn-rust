use solution::*;

#[test]
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn rising() {
    check!(r#"prices = [1, 2, 4]"#, max_profit(&[1, 2, 4]), 3);
}

#[test]
fn dip_first() {
    check!(r#"prices = [2, 1, 4]"#, max_profit(&[2, 1, 4]), 3);
}

#[test]
fn skip_a_small_trade() {
    check!(r#"prices = [6, 1, 6, 4, 3, 0, 2]"#, max_profit(&[6, 1, 6, 4, 3, 0, 2]), 7);
}

#[test]
fn one_trade_beats_two() {
    check!(r#"prices = [1, 4, 2]"#, max_profit(&[1, 4, 2]), 3);
}

#[test]
fn flat() {
    check!(r#"prices = [3, 3, 3]"#, max_profit(&[3, 3, 3]), 0);
}

#[test]
fn mixed() {
    check!(r#"prices = [3, 3, 5, 0, 0, 3, 1, 4]"#, max_profit(&[3, 3, 5, 0, 0, 3, 1, 4]), 6);
}

#[test]
fn big_swings() {
    check!(r#"prices = [0, 10000] × 1000"#, max_profit(&[0u32, 10_000].repeat(1000)), 5_000_000);
}

#[test]
fn random_vs_brute_force() {
    fn best(p: &[u32], holding: bool) -> i64 {
        match p {
            [] => 0,
            [x, rest @ ..] => {
                let x = *x as i64;
                let wait = best(rest, holding);
                if holding {
                    wait.max(x + best(rest.get(1..).unwrap_or(&[]), false))
                } else {
                    wait.max(-x + best(rest, true))
                }
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(1236);
    for _ in 0..300 {
        let n = rng.below(11);
        let prices: Vec<u32> = rng.vec(n, 0, 9);
        check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, false) as u64);
    }
}

#[test]
fn scale_200k() {
    let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
    check!("prices[i] = (7919·i) % 10000, 200000 days", max_profit(&prices), 329_588_780);
}
