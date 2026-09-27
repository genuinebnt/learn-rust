use solution::*;

#[test]
fn flat() {
    check!(r#"prices = [3, 3, 3]"#, max_profit(&[3, 3, 3]), 0);
}

#[test]
fn two_days_up() {
    check!(r#"prices = [1, 2]"#, max_profit(&[1, 2]), 1);
}

#[test]
fn two_days_down() {
    check!(r#"prices = [2, 1]"#, max_profit(&[2, 1]), 0);
}

#[test]
fn zigzag() {
    check!(r#"prices = [2, 1, 2, 0, 1]"#, max_profit(&[2, 1, 2, 0, 1]), 2);
}

#[test]
fn drop_between_rises() {
    check!(r#"prices = [3, 2, 6, 5, 0, 3]"#, max_profit(&[3, 2, 6, 5, 0, 3]), 7);
}

#[test]
fn zero_to_max() {
    check!(r#"prices = [0, 4294967295]"#, max_profit(&[0, u32::MAX]), 4_294_967_295);
}

#[test]
fn past_u32() {
    check!(r#"prices = [0, 4294967295, 0, 4294967295]"#, max_profit(&[0, u32::MAX, 0, u32::MAX]), 8_589_934_590);
}

#[test]
fn plateau_then_rise() {
    check!(r#"prices = [1, 1, 1, 9]"#, max_profit(&[1, 1, 1, 9]), 8);
}

#[test]
fn random_vs_brute_force() {
    // Every choice of buy/sell/wait on every day.
    fn best(prices: &[u32], holding: Option<u32>) -> i64 {
        let Some((&p, rest)) = prices.split_first() else { return 0 };
        let wait = best(rest, holding);
        let act = match holding {
            None => best(rest, Some(p)),
            Some(bought) => p as i64 - bought as i64 + best(rest, None),
        };
        wait.max(act)
    }
    let mut rng = anneal_prelude::Rng::new(806);
    for _ in 0..300 {
        let n = rng.below(10);
        let prices: Vec<u32> = rng.vec(n, 0, 12);
        check!(format!("prices = {prices:?}"), max_profit(&prices), best(&prices, None) as u64);
    }
}

#[test]
fn scale_200k() {
    let prices: Vec<u32> = (0..200_000).map(|i| if i % 2 == 0 { 0 } else { u32::MAX }).collect();
    check!("prices = [0, 4294967295, …] (200000 days)", max_profit(&prices), 429_496_729_500_000);
}
