use solution::*;

#[test]
fn empty() {
    check!(r#"prices = []"#, max_profit(&[]), 0);
}

#[test]
fn leetcode_ten() {
    check!(r#"prices = [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]"#, max_profit(&[1, 2, 4, 2, 5, 7, 2, 4, 9, 0]), 13);
}

#[test]
fn two_small() {
    check!(r#"prices = [2, 1, 2, 0, 1]"#, max_profit(&[2, 1, 2, 0, 1]), 2);
}

#[test]
fn two_trades() {
    check!(r#"prices = [3, 2, 6, 5, 0, 3]"#, max_profit(&[3, 2, 6, 5, 0, 3]), 7);
}

#[test]
fn flat() {
    check!(r#"prices = [4, 4, 4, 4]"#, max_profit(&[4, 4, 4, 4]), 0);
}

#[test]
fn one_big_rise() {
    check!(r#"prices = [0, 100000]"#, max_profit(&[0, 100_000]), 100_000);
}

#[test]
fn many_swings() {
    check!(r#"prices = [0, 100000] × 1000"#, max_profit(&[0u32, 100_000].repeat(1000)), 200_000);
}

#[test]
fn random_vs_brute_force() {
    fn best(p: &[u32], holding: bool, left: usize) -> i64 {
        match p {
            [] => 0,
            [x, rest @ ..] => {
                let x = *x as i64;
                let wait = best(rest, holding, left);
                if holding {
                    wait.max(x + best(rest, false, left))
                } else if left > 0 {
                    wait.max(-x + best(rest, true, left - 1))
                } else {
                    wait
                }
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(1238);
    for _ in 0..300 {
        let n = rng.below(11);
        let prices: Vec<u32> = rng.vec(n, 0, 9);
        check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, false, 2) as u64);
    }
}

#[test]
fn scale_200k() {
    let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
    check!("prices[i] = (7919·i) % 10000, 200000 days", max_profit(&prices), 19_998);
}
