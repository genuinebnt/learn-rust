use solution::*;

#[test]
fn zero_one() {
    check!(r#"0 and 1"#, (isqrt(0), isqrt(1)), (0, 1));
}

#[test]
fn two_and_three() {
    check!(r#"2 and 3"#, (isqrt(2), isqrt(3)), (1, 1));
}

#[test]
fn u32_max() {
    check!(r#"u32::MAX and 2³²"#, (isqrt(u64::from(u32::MAX)), isqrt(1 << 32)), (65_535, 65_536));
}

#[test]
fn big_square_and_neighbours() {
    check!(r#"10¹⁸ − 1, 10¹⁸, 10¹⁸ + 1"#, (isqrt(999_999_999_999_999_999), isqrt(1_000_000_000_000_000_000), isqrt(1_000_000_000_000_000_001)), (999_999_999, 1_000_000_000, 1_000_000_000));
}

#[test]
fn scale_squares_sweep() {
    // r² and r² − 1 for r in 1..=100000.
    let bad = (1..=100_000u64).filter(|&r| isqrt(r * r) != r || isqrt(r * r - 1) != r - 1).count();
    check!("isqrt(r²) and isqrt(r² − 1) for r in 1..=100000: how many are wrong", bad, 0);
}

#[test]
fn random_vs_brute_force() {
    // r is right exactly when r² ≤ x < (r + 1)², checked in u128.
    let mut rng = anneal_prelude::Rng::new(404);
    for i in 0..3000 {
        let x = match i % 3 {
            0 => rng.int(0, 10_000) as u64,
            1 => rng.next_u64(),
            _ => { let r = rng.next_u64() >> 32; (r * r).wrapping_add(rng.int(-1, 1) as u64) }
        };
        let r = u128::from(isqrt(x));
        check!(format!("x = {x}"), r * r <= u128::from(x) && u128::from(x) < (r + 1) * (r + 1), true);
    }
}

#[test]
fn max() {
    check!(r#"u64::MAX"#, isqrt(u64::MAX), 4_294_967_295);
}

#[test]
fn near_square() {
    check!(r#"(2³² − 1)² and one less"#, (isqrt(18_446_744_065_119_617_025), isqrt(18_446_744_065_119_617_024)), (4_294_967_295, 4_294_967_294));
}
