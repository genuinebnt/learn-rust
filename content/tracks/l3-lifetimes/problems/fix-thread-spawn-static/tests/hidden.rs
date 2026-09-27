use solution::*;

#[test]
fn zero_chunks() {
    check!(r#"[1, 2, 3], 0 threads"#, parallel_sum(&[1, 2, 3], 0), 6);
}

#[test]
fn single() {
    check!(r#"[42], 4 threads"#, parallel_sum(&[42], 4), 42);
}

#[test]
fn one_thread() {
    let data: Vec<u64> = (1..=10).collect();
    check!(r#"1..=10, 1 thread"#, parallel_sum(&data, 1), 55);
}

#[test]
fn remainder_chunk() {
    let data: Vec<u64> = (1..=10).collect();
    check!(r#"10 values, 3 threads"#, parallel_sum(&data, 3), 55);
}

#[test]
fn large_values() {
    check!(r#"[u64::MAX / 4; 3], 3 threads"#, parallel_sum(&[u64::MAX / 4; 3], 3), 3 * (u64::MAX / 4));
}

#[test]
fn zeros() {
    check!(r#"[0; 100], 7 threads"#, parallel_sum(&[0; 100], 7), 0);
}

#[test]
fn empty_zero_threads() {
    check!(r#"[], 0 threads"#, parallel_sum(&[], 0), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(315);
    for _ in 0..200 {
        let n = rng.below(20);
        let data: Vec<u64> = rng.vec(n, 0, 1_000_000);
        let chunks = rng.below(8);
        check!(format!("data = {data:?}, chunks = {chunks}"), parallel_sum(&data, chunks), data.iter().sum::<u64>());
    }
}

#[test]
fn more_threads_than_items() {
    check!(r#"[1, 2, 3], 10 threads"#, parallel_sum(&[1, 2, 3], 10), 6);
}

#[test]
fn big() {
    let data = vec![1u64; 1_000_000];
    check!(r#"10⁶ ones, 8 threads"#, parallel_sum(&data, 8), 1_000_000);
}
