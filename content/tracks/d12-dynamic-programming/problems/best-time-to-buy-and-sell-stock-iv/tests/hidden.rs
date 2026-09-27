use solution::*;

#[test]
fn empty_no_trades() {
    check!(r#"k = 0, prices = []"#, max_profit(0, &[]), 0);
}

#[test]
fn two_of_three() {
    check!(r#"k = 2, prices = [1, 5, 2, 6, 3, 7]"#, max_profit(2, &[1, 5, 2, 6, 3, 7]), 9);
}

#[test]
fn three_of_three() {
    check!(r#"k = 3, prices = [1, 5, 2, 6, 3, 7]"#, max_profit(3, &[1, 5, 2, 6, 3, 7]), 12);
}

#[test]
fn four_of_three() {
    check!(r#"k = 4, prices = [1, 5, 2, 6, 3, 7]"#, max_profit(4, &[1, 5, 2, 6, 3, 7]), 12);
}

#[test]
fn falling() {
    check!(r#"k = 3, prices = [7, 6, 4, 3, 1]"#, max_profit(3, &[7, 6, 4, 3, 1]), 0);
}

#[test]
fn one_day() {
    check!(r#"k = 5, prices = [4]"#, max_profit(5, &[4]), 0);
}

#[test]
fn merge_to_save_a_trade() {
    check!(r#"k = 2, prices = [1, 2, 4, 2, 5, 7, 2, 4, 9, 0]"#, max_profit(2, &[1, 2, 4, 2, 5, 7, 2, 4, 9, 0]), 13);
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
    let mut rng = anneal_prelude::Rng::new(1239);
    for _ in 0..300 {
        let n = rng.below(11);
        let prices: Vec<u32> = rng.vec(n, 0, 9);
        let k = rng.int(0, 4) as usize;
        check!(format!("k = {k}, prices = {prices:?}"), max_profit(k, &prices), best(&prices, false, k) as u64);
    }
}

#[test]
fn scale_k_100() {
    let prices: Vec<u32> = (0..20_000u32).map(|i| i * 7919 % 1000).collect();
    check!("k = 100, prices[i] = (7919·i) % 1000, 20000 days", max_profit(100, &prices), 98_700);
}

#[test]
fn scale_huge_k() {
    let prices: Vec<u32> = (0..200_000u32).map(|i| i * 7919 % 10_000).collect();
    check!("k = 100000, prices[i] = (7919·i) % 10000, 200000 days", max_profit(100_000, &prices), 329_588_780);
}
