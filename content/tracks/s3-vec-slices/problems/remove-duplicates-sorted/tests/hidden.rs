use solution::*;

#[test]
fn single() {
    check!(r#"v = [7], k = 1"#, { let mut v = [7]; let n = dedup_keep(&mut v, 1); (n, v[..n].to_vec()) }, (1, vec![7]));
}

#[test]
fn k_larger_than_runs() {
    check!(r#"v = [1, 1, 2], k = 5"#, { let mut v = [1, 1, 2]; let n = dedup_keep(&mut v, 5); (n, v[..n].to_vec()) }, (3, vec![1, 1, 2]));
}

#[test]
fn all_same_k_three() {
    check!(r#"v = [4, 4, 4, 4, 4, 4, 4], k = 3"#, { let mut v = [4, 4, 4, 4, 4, 4, 4]; let n = dedup_keep(&mut v, 3); (n, v[..n].to_vec()) }, (3, vec![4, 4, 4]));
}

#[test]
fn all_distinct() {
    check!(r#"v = [-3, 0, 7], k = 1"#, { let mut v = [-3, 0, 7]; let n = dedup_keep(&mut v, 1); (n, v[..n].to_vec()) }, (3, vec![-3, 0, 7]));
}

#[test]
fn negatives_and_extremes() {
    check!(r#"v = [-2147483648, -2147483648, -2147483648, 0, 2147483647, 2147483647], k = 2"#, { let mut v = [-2147483648, -2147483648, -2147483648, 0, 2147483647, 2147483647]; let n = dedup_keep(&mut v, 2); (n, v[..n].to_vec()) }, (5, vec![-2147483648, -2147483648, 0, 2147483647, 2147483647]));
}

#[test]
fn alternating_run_lengths() {
    check!(r#"v = [1, 2, 2, 2, 3, 4, 4, 4, 4, 5], k = 2"#, { let mut v = [1, 2, 2, 2, 3, 4, 4, 4, 4, 5]; let n = dedup_keep(&mut v, 2); (n, v[..n].to_vec()) }, (7, vec![1, 2, 2, 3, 4, 4, 5]));
}

#[test]
fn runs_at_the_end() {
    check!(r#"v = [1, 2, 3, 3, 3, 3], k = 2"#, { let mut v = [1, 2, 3, 3, 3, 3]; let n = dedup_keep(&mut v, 2); (n, v[..n].to_vec()) }, (4, vec![1, 2, 3, 3]));
}

#[test]
fn vec_empty_and_k_one() {
    check!(r#"v = [], then [2, 2, 3] with k = 1"#, { let mut a: Vec<i32> = vec![]; dedup_keep_vec(&mut a, 1); let mut b = vec![2, 2, 3]; dedup_keep_vec(&mut b, 1); (a, b) }, (vec![], vec![2, 3]));
}

#[test]
fn vec_keeps_capacity() {
    let mut v = vec![5; 100];
    let cap = v.capacity();
    dedup_keep_vec(&mut v, 2);
    let v_cap_same = v.capacity() == cap;
    check!(r#"v = [5; 100], k = 2: truncated in place"#, (v, v_cap_same), (vec![5, 5], true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7307);
    for _ in 0..400 {
        let n = rng.below(14);
        let mut v: Vec<i32> = rng.vec(n, -3, 3);
        v.sort();
        let k = rng.below(4) + 1;
        let mut want: Vec<i32> = Vec::new();
        for &x in &v {
            if want.iter().filter(|&&y| y == x).count() < k {
                want.push(x);
            }
        }
        let mut got = v.clone();
        let len = dedup_keep(&mut got, k);
        let mut got_vec = v.clone();
        dedup_keep_vec(&mut got_vec, k);
        check!(format!("v = {v:?}, k = {k}"), (len, got[..len].to_vec(), got_vec), (want.len(), want.clone(), want));
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).map(|i| i / 4).collect();
    v.extend(vec![50_000; 100_000]);
    let k = dedup_keep(&mut v, 3);
    check!("v = [0, 0, 0, 0, 1, …, 49999 ×4] then 100000 × 50000, k = 3", (k, v[k - 1], v[k - 4]), (150_003, 50_000, 49_999));
}
