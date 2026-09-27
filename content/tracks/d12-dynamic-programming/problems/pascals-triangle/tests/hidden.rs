use solution::*;

#[test]
fn zero_rows() {
    check!(r#"num_rows = 0"#, generate(0), Vec::<Vec<u64>>::new());
}

#[test]
fn one_row() {
    check!(r#"num_rows = 1"#, generate(1), vec![vec![1u64]]);
}

#[test]
fn three_rows() {
    check!(r#"num_rows = 3"#, generate(3), vec![vec![1], vec![1, 1], vec![1, 2, 1]]);
}

#[test]
fn row_lengths() {
    check!(r#"num_rows = 10, row lengths"#, generate(10).iter().map(|r| r.len()).collect::<Vec<_>>(), (1..=10).collect::<Vec<usize>>());
}

#[test]
fn leetcode_max_middle() {
    check!(r#"num_rows = 30, middle of the last row"#, generate(30)[29][14], 77_558_760);
}

#[test]
fn past_factorials() {
    check!(r#"num_rows = 22, middle of the last row"#, generate(22)[21][10], 352_716);
}

#[test]
fn past_u32() {
    check!(r#"num_rows = 60, middle of the last row"#, generate(60)[59][29], 59_132_290_782_430_712);
}

#[test]
fn last_row_sum() {
    check!(r#"num_rows = 60, sum of the last row"#, generate(60)[59].iter().sum::<u64>(), 1u64 << 59);
}

#[test]
fn random_vs_brute_force() {
    fn choose(n: u64, k: u64) -> u64 {
        let mut c: u128 = 1;
        for i in 0..k {
            c = c * (n - i) as u128 / (i + 1) as u128;
        }
        c as u64
    }
    let mut rng = anneal_prelude::Rng::new(1204);
    for _ in 0..200 {
        let n = rng.below(61);
        let want: Vec<Vec<u64>> = (0..n as u64).map(|r| (0..=r).map(|k| choose(r, k)).collect()).collect();
        check!(format!("num_rows = {n}"), generate(n), want);
    }
}
