use solution::*;

#[test]
fn zero_amount() {
    check!(r#"amount = 0, coins = [7]"#, change(0, &[7]), 1);
}

#[test]
fn no_coins_zero() {
    check!(r#"amount = 0, coins = []"#, change(0, &[]), 1);
}

#[test]
fn no_coins() {
    check!(r#"amount = 5, coins = []"#, change(5, &[]), 0);
}

#[test]
fn coin_too_big() {
    check!(r#"amount = 1, coins = [2]"#, change(1, &[2]), 0);
}

#[test]
fn even_coins_odd_amount() {
    check!(r#"amount = 7, coins = [2, 4]"#, change(7, &[2, 4]), 0);
}

#[test]
fn one_two_three() {
    check!(r#"amount = 12, coins = [1, 2, 3]"#, change(12, &[1, 2, 3]), 19);
}

#[test]
fn us_cents() {
    check!(r#"amount = 100, coins = [1, 5, 10, 25, 50]"#, change(100, &[1, 5, 10, 25, 50]), 292);
}

#[test]
fn leetcode_large() {
    check!(r#"amount = 500, coins = [3, 5, 7, 8, 9, 10, 11]"#, change(500, &[3, 5, 7, 8, 9, 10, 11]), 35_502_874);
}

#[test]
fn random_vs_brute_force() {
    // Try every count of the first coin, then recurse on the rest.
    fn count(coins: &[u32], amount: u32) -> u64 {
        match coins {
            [] => (amount == 0) as u64,
            [c, rest @ ..] => (0..=amount / c).map(|k| count(rest, amount - k * c)).sum(),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1212);
    for _ in 0..300 {
        let k = rng.int(0, 4) as usize;
        let mut coins: Vec<u32> = rng.vec(k, 1, 10);
        coins.sort_unstable();
        coins.dedup();
        rng.shuffle(&mut coins);
        let amount = rng.int(0, 30) as u32;
        check!(format!("amount = {amount}, coins = {coins:?}"), change(amount, &coins), count(&coins, amount));
    }
}

#[test]
fn scale_amount_5000() {
    let coins = [1, 2, 5, 10, 20, 50, 100, 200, 500];
    check!("amount = 5000, coins = [1, 2, 5, 10, 20, 50, 100, 200, 500]", change(5000, &coins), 18_682_149_631_801);
}
