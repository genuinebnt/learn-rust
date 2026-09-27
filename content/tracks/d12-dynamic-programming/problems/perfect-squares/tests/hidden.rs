use solution::*;

#[test]
fn one() {
    check!(r#"n = 1"#, num_squares(1), 1);
}

#[test]
fn two() {
    check!(r#"n = 2"#, num_squares(2), 2);
}

#[test]
fn three() {
    check!(r#"n = 3"#, num_squares(3), 3);
}

#[test]
fn four() {
    check!(r#"n = 4"#, num_squares(4), 1);
}

#[test]
fn greedy_trap() {
    check!(r#"n = 43"#, num_squares(43), 3);
}

#[test]
fn form_4k_times_7() {
    check!(r#"n = 28"#, num_squares(28), 4);
}

#[test]
fn leetcode_max() {
    check!(r#"n = 10000"#, num_squares(10_000), 1);
}

#[test]
fn just_below() {
    check!(r#"n = 9999"#, num_squares(9_999), 4);
}

#[test]
fn random_vs_brute_force() {
    // Lagrange and Legendre: 1 if square, 2 if a sum of two squares, 4 if n = 4^a(8b + 7), else 3.
    fn want(n: u32) -> u32 {
        let is_square = |x: u32| (0..=x).take_while(|r| r * r <= x).any(|r| r * r == x);
        if is_square(n) {
            return 1;
        }
        if (1..).take_while(|a| a * a <= n).any(|a| is_square(n - a * a)) {
            return 2;
        }
        let mut m = n;
        while m % 4 == 0 {
            m /= 4;
        }
        if m % 8 == 7 { 4 } else { 3 }
    }
    let mut rng = anneal_prelude::Rng::new(1211);
    for _ in 0..300 {
        let n = rng.int(1, 2000) as u32;
        check!(format!("n = {n}"), num_squares(n), want(n));
    }
}

#[test]
fn scale_100k() {
    check!("n = 99999, then n = 100000", (num_squares(99_999), num_squares(100_000)), (4, 2));
}
