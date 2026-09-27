use solution::*;

#[test]
fn zero() {
    check!(r#"n = 0"#, (fib_memo(0), fib_table(0)), (0, 0));
}

#[test]
fn one() {
    check!(r#"n = 1"#, (fib_memo(1), fib_table(1)), (1, 1));
}

#[test]
fn five() {
    check!(r#"n = 5"#, (fib_memo(5), fib_table(5)), (5, 5));
}

#[test]
fn thirty() {
    check!(r#"n = 30"#, (fib_memo(30), fib_table(30)), (832_040, 832_040));
}

#[test]
fn past_i32() {
    check!(r#"n = 47"#, (fib_memo(47), fib_table(47)), (2_971_215_073, 2_971_215_073));
}

#[test]
fn ninety() {
    check!(r#"n = 90"#, (fib_memo(90), fib_table(90)), (2_880_067_194_370_816_120, 2_880_067_194_370_816_120));
}

#[test]
fn largest_that_fits() {
    check!(r#"n = 93"#, (fib_memo(93), fib_table(93)), (12_200_160_415_121_876_738, 12_200_160_415_121_876_738));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1201);
    for _ in 0..300 {
        let n = rng.below(94) as u32;
        let (mut a, mut b) = (0u128, 1u128);
        for _ in 0..n {
            (a, b) = (b, a + b);
        }
        let want = a as u64;
        check!(format!("n = {n}"), (fib_memo(n), fib_table(n)), (want, want));
    }
}

#[test]
fn every_n_satisfies_the_recurrence() {
    for n in 2..=93u32 {
        check!(format!("n = {n}"), fib_memo(n), fib_memo(n - 1) + fib_memo(n - 2));
        check!(format!("n = {n}"), fib_table(n), fib_table(n - 1) + fib_table(n - 2));
    }
}

#[test]
fn scale_memo_at_93() {
    // Without the memo this is about 10¹⁹ calls.
    check!("n = 93, called 1000 times", (0..1000).map(|_| fib_memo(93)).max(), Some(12_200_160_415_121_876_738));
}
