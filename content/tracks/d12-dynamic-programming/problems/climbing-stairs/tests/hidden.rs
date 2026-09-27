use solution::*;

#[test]
fn one_step() {
    check!(r#"n = 1"#, climb_stairs(1), 1);
}

#[test]
fn ten() {
    check!(r#"n = 10"#, climb_stairs(10), 89);
}

#[test]
fn twenty() {
    check!(r#"n = 20"#, climb_stairs(20), 10_946);
}

#[test]
fn leetcode_max() {
    check!(r#"n = 45"#, climb_stairs(45), 1_836_311_903);
}

#[test]
fn past_u32() {
    check!(r#"n = 50"#, climb_stairs(50), 20_365_011_074);
}

#[test]
fn eighty() {
    check!(r#"n = 80"#, climb_stairs(80), 37_889_062_373_143_906);
}

#[test]
fn largest() {
    check!(r#"n = 90"#, climb_stairs(90), 4_660_046_610_375_530_309);
}

#[test]
fn random_vs_brute_force() {
    fn ways(n: u32) -> u64 {
        if n <= 1 { 1 } else { ways(n - 1) + ways(n - 2) }
    }
    let mut rng = anneal_prelude::Rng::new(1202);
    for _ in 0..300 {
        let n = rng.int(1, 22) as u32;
        check!(format!("n = {n}"), climb_stairs(n), ways(n));
    }
}

#[test]
fn scale_90_many_times() {
    // Plain recursion is about 10¹⁹ calls here.
    check!("n = 90, called 1000 times", (0..1000).map(|_| climb_stairs(90)).min(), Some(4_660_046_610_375_530_309));
}
