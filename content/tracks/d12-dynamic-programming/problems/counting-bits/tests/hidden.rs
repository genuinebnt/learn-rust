use solution::*;

#[test]
fn zero() {
    check!(r#"n = 0"#, count_bits(0), vec![0]);
}

#[test]
fn one() {
    check!(r#"n = 1"#, count_bits(1), vec![0, 1]);
}

#[test]
fn seven() {
    check!(r#"n = 7"#, count_bits(7), vec![0, 1, 1, 2, 1, 2, 2, 3]);
}

#[test]
fn power_of_two() {
    check!(r#"n = 16, last value"#, count_bits(16)[16], 1);
}

#[test]
fn all_ones() {
    check!(r#"n = 1023, last value"#, count_bits(1023)[1023], 10);
}

#[test]
fn length() {
    check!(r#"n = 100, length"#, count_bits(100).len(), 101);
}

#[test]
fn largest() {
    check!(r#"n = 1000000, last value"#, count_bits(1_000_000)[1_000_000], 7);
}

#[test]
fn largest_all_ones_below() {
    check!(r#"n = 1000000, value at 2^19 - 1"#, count_bits(1_000_000)[(1 << 19) - 1], 19);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1205);
    for _ in 0..200 {
        let n = rng.below(300);
        let want: Vec<u32> = (0..=n).map(|i| i.count_ones()).collect();
        check!(format!("n = {n}"), count_bits(n), want);
    }
}

#[test]
fn scale_million() {
    let bits = count_bits(1_000_000);
    let total: u64 = bits.iter().map(|&b| b as u64).sum();
    check!("n = 1000000, total of all counts", (bits.len(), total), (1_000_001, 9_884_999));
}
