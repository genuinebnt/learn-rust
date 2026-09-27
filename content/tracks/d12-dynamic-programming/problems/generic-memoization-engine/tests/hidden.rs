use solution::*;
use std::cell::Cell;

#[test]
fn starts_empty() {
    let m = Memo::<u8, u8>::new(|_, x| x);
    check!(r#"a new memo: (len, is_empty)"#, (m.len(), m.is_empty()), (0, true));
}

#[test]
fn not_empty_after_get() {
    let mut m = Memo::<u8, u8>::new(|_, x| x);
    m.get(3);
    check!(r#"one get, then (len, is_empty)"#, (m.len(), m.is_empty()), (1, false));
}

#[test]
fn fibonacci_150_u128() {
    let mut fib = Memo::<u64, u128>::new(|m, n| if n < 2 { n as u128 } else { m.get(n - 1) + m.get(n - 2) });
    check!(r#"fib via Memo<u64, u128>, n = 150"#, fib.get(150), 9_969_216_677_189_303_386_214_405_760_200);
}

#[test]
fn string_keys() {
    let words = ["cat", "cats", "and", "sand", "dog"];
    let mut ways = Memo::<String, u64>::new(|m, s| {
        if s.is_empty() {
            return 1;
        }
        words.iter().filter(|w| s.starts_with(*w)).map(|w| m.get(s[w.len()..].to_string())).sum()
    });
    check!(r#"ways to split "catsanddog" into [cat, cats, and, sand, dog], key = the rest of the string"#, ways.get("catsanddog".to_string()), 2);
}

#[test]
fn string_keys_sixty() {
    let words = ["a", "aa"];
    let mut ways = Memo::<String, u64>::new(|m, s| {
        if s.is_empty() {
            return 1;
        }
        words.iter().filter(|w| s.starts_with(*w)).map(|w| m.get(s[w.len()..].to_string())).sum()
    });
    check!(r#"ways to split 60 × 'a' into [a, aa]"#, ways.get("a".repeat(60)), 2_504_730_781_961);
}

#[test]
fn option_values() {
    let coins = [1u32, 5, 6, 8];
    let mut fewest = Memo::<u32, Option<u32>>::new(|m, amount| {
        if amount == 0 {
            return Some(0);
        }
        coins.iter().filter(|&&c| c <= amount).filter_map(|&c| m.get(amount - c)).min().map(|k| k + 1)
    });
    let other = [5u32, 7];
    let mut none = Memo::<u32, Option<u32>>::new(|m, amount| {
        if amount == 0 {
            return Some(0);
        }
        other.iter().filter(|&&c| c <= amount).filter_map(|&c| m.get(amount - c)).min().map(|k| k + 1)
    });
    check!(r#"fewest coins from [1, 5, 6, 8] for 11, and from [5, 7] for 3"#, (fewest.get(11), none.get(3)), (Some(2), None));
}

#[test]
fn each_key_once_in_recursion() {
    let calls = Cell::new(0);
    let mut fib = Memo::<u64, u64>::new(|m, n| {
        calls.set(calls.get() + 1);
        if n < 2 { n } else { m.get(n - 1) + m.get(n - 2) }
    });
    check!(r#"fib(30) through a counting wrapper: (answer, calls, len)"#, (fib.get(30), calls.get(), fib.len()), (832_040, 31, 31));
}

#[test]
fn cache_survives_between_gets() {
    let calls = Cell::new(0);
    let mut fib = Memo::<u64, u64>::new(|m, n| {
        calls.set(calls.get() + 1);
        if n < 2 { n } else { m.get(n - 1) + m.get(n - 2) }
    });
    fib.get(20);
    fib.get(25);
    check!(r#"fib.get(20), then fib.get(25): calls to f in total"#, calls.get(), 26);
}

#[test]
fn random_vs_brute_force() {
    // Ways to make `amount` from coins[i..], memoised on (i, amount), against a bottom-up table.
    let mut rng = anneal_prelude::Rng::new(1254);
    for _ in 0..200 {
        let k = rng.int(1, 4) as usize;
        let coins: Vec<u32> = rng.vec(k, 1, 9);
        let amount = rng.int(0, 40) as u32;
        let mut ways = Memo::<(usize, u32), u64>::new(|m, (i, a)| {
            if a == 0 {
                1
            } else if i == coins.len() {
                0
            } else {
                m.get((i + 1, a)) + if coins[i] <= a { m.get((i, a - coins[i])) } else { 0 }
            }
        });
        let mut table = vec![0u64; amount as usize + 1];
        table[0] = 1;
        for &c in &coins {
            for x in c as usize..=amount as usize {
                table[x] += table[x - c as usize];
            }
        }
        check!(format!("coins = {coins:?}, amount = {amount}"), ways.get((0, amount)), table[amount as usize]);
    }
}

#[test]
fn scale_grid_300() {
    let mut paths = Memo::<(u32, u32), u64>::new(|m, (r, c)| {
        if r == 0 || c == 0 { 1 } else { (m.get((r - 1, c)) + m.get((r, c - 1))) % 1_000_000_007 }
    });
    check!("grid paths to (300, 300) mod 1e9+7: (answer, keys cached)", (paths.get((300, 300)), paths.len()), (272_165_270, 90_000 + 600));
}
