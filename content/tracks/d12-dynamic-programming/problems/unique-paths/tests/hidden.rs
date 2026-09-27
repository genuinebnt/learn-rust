use solution::*;

#[test]
fn one_cell() {
    check!(r#"m = 1, n = 1"#, unique_paths(1, 1), 1);
}

#[test]
fn one_column() {
    check!(r#"m = 100, n = 1"#, unique_paths(100, 1), 1);
}

#[test]
fn two_rows() {
    check!(r#"m = 2, n = 100"#, unique_paths(2, 100), 100);
}

#[test]
fn ten_by_ten() {
    check!(r#"m = 10, n = 10"#, unique_paths(10, 10), 48_620);
}

#[test]
fn symmetric() {
    check!(r#"m = 7, n = 3"#, unique_paths(7, 3), 28);
}

#[test]
fn leetcode_large() {
    check!(r#"m = 23, n = 12"#, unique_paths(23, 12), 193_536_720);
}

#[test]
fn thirty_three() {
    check!(r#"m = 33, n = 33"#, unique_paths(33, 33), 1_832_624_140_942_590_534);
}

#[test]
fn largest_square() {
    check!(r#"m = 34, n = 34"#, unique_paths(34, 34), 7_219_428_434_016_265_740);
}

#[test]
fn random_vs_brute_force() {
    fn count(i: usize, j: usize) -> u64 {
        if i == 0 || j == 0 { 1 } else { count(i - 1, j) + count(i, j - 1) }
    }
    let mut rng = anneal_prelude::Rng::new(1218);
    for _ in 0..300 {
        let m = rng.int(1, 10) as usize;
        let n = rng.int(1, 10) as usize;
        check!(format!("m = {m}, n = {n}"), unique_paths(m, n), count(m - 1, n - 1));
    }
}

#[test]
fn scale_many_grids() {
    // Plain recursion visits every path: about 10¹⁸ of them for 33 × 33.
    let total: u64 = (1..=30).map(|k| unique_paths(k, 30) % 1_000_007).sum();
    check!("sum over m = 1..=30 of unique_paths(m, 30) % 1000007", (total, unique_paths(33, 33)), (12_292_783, 1_832_624_140_942_590_534));
}
