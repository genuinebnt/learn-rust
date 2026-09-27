use solution::*;

#[test]
fn chunks_zero() {
    check!(r#"[1, 2] on 0 threads"#, parallel_sum(&[1, 2], 0), 3);
}

#[test]
fn more_threads_than_items() {
    check!(r#"[5, 6] on 10 threads"#, parallel_sum(&[5, 6], 10), 11);
}

#[test]
fn uneven_chunks() {
    check!(r#"1..=10 on 3 threads"#, parallel_sum(&(1..=10).collect::<Vec<u64>>(), 3), 55);
}

#[test]
fn big_values() {
    check!(r#"[u32::MAX as u64; 4]"#, parallel_sum(&[u32::MAX as u64; 4], 2), 4 * u32::MAX as u64);
}

#[test]
fn count_empty() {
    check!(r#"count_later([])"#, count_later(&[]).join().unwrap(), 0);
}

#[test]
fn count_whitespace_kinds() {
    check!(r#"count_later(["a\tb\nc  "])"#, count_later(&["a\tb\nc  ".to_string()]).join().unwrap(), 3);
}

#[test]
fn spawn_named_returns_value() {
    check!(r#"spawn_named returning a String"#, spawn_named("s", || "done".to_string()).join().unwrap(), "done".to_string());
}

#[test]
fn spawn_named_panics_are_caught() {
    check!(r#"a job that panics"#, spawn_named("p", || -> u8 { panic!("boom") }).join().is_err(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6312);
    for _ in 0..100 {
        let n = rng.below(40);
        let data: Vec<u64> = rng.vec(n, 0, 1000);
        let chunks = rng.below(6);
        check!(format!("parallel_sum({data:?}, {chunks})"), parallel_sum(&data, chunks), data.iter().sum::<u64>());
    }
}

#[test]
fn big_input() {
    let data: Vec<u64> = (0..1_000_000).collect();
    check!("0..1000000 on 8 threads", parallel_sum(&data, 8), 499_999_500_000);
}
