use solution::*;

#[test]
fn window_too_big() {
    check!(r#"v = [1, 2], k = 3"#, max_window_sum(&[1, 2], 3), None);
}

#[test]
fn chunks_empty() {
    check!(r#"v = [], size = 3"#, chunk_sums(&[], 3), Vec::<i32>::new());
}

#[test]
fn window_on_empty() {
    check!(r#"v = [], k = 1"#, max_window_sum(&[], 1), None);
}

#[test]
fn all_negative_windows() {
    check!(r#"v = [-3, -1, -2], k = 2"#, max_window_sum(&[-3, -1, -2], 2), Some(-3));
}

#[test]
fn chunk_size_one() {
    check!(r#"v = [4, -5], size = 1"#, chunk_sums(&[4, -5], 1), vec![4, -5]);
}

#[test]
fn exact_multiple() {
    check!(r#"v = [1, 2, 3, 4], size = 2"#, chunk_sums(&[1, 2, 3, 4], 2), vec![3, 7]);
}

#[test]
fn k_equals_len() {
    check!(r#"v = [1, 2, 3], k = 3"#, max_window_sum(&[1, 2, 3], 3), Some(6));
}

#[test]
fn best_window_last() {
    check!(r#"v = [1, 1, 1, 9, 9], k = 2"#, max_window_sum(&[1, 1, 1, 9, 9], 2), Some(18));
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MAX, i32::MIN], size = 1, k = 1"#, (chunk_sums(&[i32::MAX, i32::MIN], 1), max_window_sum(&[i32::MIN, i32::MAX], 1)), (vec![i32::MAX, i32::MIN], Some(i32::MAX)));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2310);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -50, 50);
        let size = rng.below(4) + 1;
        let k = rng.below(5) + 1;
        let mut want_chunks = Vec::new();
        let mut i = 0;
        while i < n {
            want_chunks.push(v[i..(i + size).min(n)].iter().sum::<i32>());
            i += size;
        }
        let mut want_max: Option<i32> = None;
        for s in 0..n {
            if s + k <= n {
                let sum: i32 = v[s..s + k].iter().sum();
                want_max = Some(want_max.map_or(sum, |m| m.max(sum)));
            }
        }
        check!(format!("v = {v:?}, size = {size}, k = {k}"), (chunk_sums(&v, size), max_window_sum(&v, k)), (want_chunks, want_max));
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i32> = (0..200_000).map(|i| i % 7 - 3).collect();
    let sums = chunk_sums(&v, 3);
    check!("v = 200000 values, size = 3, k = 2", (sums.len(), sums[0], max_window_sum(&v, 2)), (66_667, -6, Some(5)));
}
