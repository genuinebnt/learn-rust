use solution::*;

#[test]
fn zero_amount() {
    check!(r#"coins = [7], amount = 0"#, coin_change(&[7], 0), Some(0));
}

#[test]
fn no_coins_zero() {
    check!(r#"coins = [], amount = 0"#, coin_change(&[], 0), Some(0));
}

#[test]
fn greedy_dead_end() {
    check!(r#"coins = [4, 5], amount = 8"#, coin_change(&[4, 5], 8), Some(2));
}

#[test]
fn leetcode_big() {
    check!(r#"coins = [186, 419, 83, 408], amount = 6249"#, coin_change(&[186, 419, 83, 408], 6249), Some(20));
}

#[test]
fn unsorted_coins() {
    check!(r#"coins = [2, 5, 10, 1], amount = 27"#, coin_change(&[2, 5, 10, 1], 27), Some(4));
}

#[test]
fn unreachable() {
    check!(r#"coins = [3, 7], amount = 11"#, coin_change(&[3, 7], 11), None);
}

#[test]
fn also_unreachable() {
    check!(r#"coins = [3, 5], amount = 7"#, coin_change(&[3, 5], 7), None);
}

#[test]
fn huge_coin() {
    check!(r#"coins = [2147483647], amount = 2"#, coin_change(&[2_147_483_647], 2), None);
}

#[test]
fn many_ones() {
    check!(r#"coins = [1], amount = 10000"#, coin_change(&[1], 10_000), Some(10_000));
}

#[test]
fn random_vs_brute_force() {
    // Try every count of the first coin, then recurse on the rest.
    fn fewest(coins: &[u32], amount: u32) -> Option<u32> {
        match coins {
            [] => (amount == 0).then_some(0),
            [c, rest @ ..] => (0..=amount / c).filter_map(|k| fewest(rest, amount - k * c).map(|n| n + k)).min(),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1210);
    for _ in 0..300 {
        let k = rng.int(0, 3) as usize;
        let mut coins: Vec<u32> = rng.vec(k, 1, 12);
        coins.sort_unstable();
        coins.dedup();
        let amount = rng.int(0, 40) as u32;
        check!(format!("coins = {coins:?}, amount = {amount}"), coin_change(&coins, amount), fewest(&coins, amount));
    }
}

#[test]
fn scale_amount_100k() {
    let coins = [7, 23, 51, 97, 211, 479, 983, 1999, 4001, 7919, 9973, 10007];
    check!("coins = [7, 23, 51, 97, 211, 479, 983, 1999, 4001, 7919, 9973, 10007], amount = 100000", coin_change(&coins, 100_000), Some(14));
}
