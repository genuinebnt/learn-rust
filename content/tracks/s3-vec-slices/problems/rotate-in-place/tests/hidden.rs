use solution::*;

#[test]
fn empty() {
    check!(r#"v = [], k = 3"#, { let mut v: [i32; 0] = []; rotate_right(&mut v, 3); v }, []);
}

#[test]
fn large_k() {
    check!(r#"v = [1, 2, 3], k = 7"#, { let mut v = [1, 2, 3]; rotate_right(&mut v, 7); v }, [3, 1, 2]);
}

#[test]
fn single() {
    check!(r#"v = [5], k = 4"#, { let mut v = [5]; rotate_right(&mut v, 4); v }, [5]);
}

#[test]
fn by_one() {
    check!(r#"v = [1, 2, 3, 4], k = 1"#, { let mut v = [1, 2, 3, 4]; rotate_right(&mut v, 1); v }, [4, 1, 2, 3]);
}

#[test]
fn len_minus_one() {
    check!(r#"v = [1, 2, 3, 4], k = 3"#, { let mut v = [1, 2, 3, 4]; rotate_right(&mut v, 3); v }, [2, 3, 4, 1]);
}

#[test]
fn k_max() {
    check!(r#"v = [1, 2, 3, 4, 5, 6, 7], k = usize::MAX (≡ 1 mod 7)"#, { let mut v = [1, 2, 3, 4, 5, 6, 7]; rotate_right(&mut v, usize::MAX); v }, [7, 1, 2, 3, 4, 5, 6]);
}

#[test]
fn duplicates() {
    check!(r#"v = [1, 1, 2, 2], k = 1"#, { let mut v = [1, 1, 2, 2]; rotate_right(&mut v, 1); v }, [2, 1, 1, 2]);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MIN, 0, i32::MAX], k = 2"#, { let mut v = [i32::MIN, 0, i32::MAX]; rotate_right(&mut v, 2); v }, [0, i32::MAX, i32::MIN]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2306);
    for _ in 0..300 {
        let n = rng.below(9);
        let v: Vec<i32> = rng.vec(n, -9, 9);
        let k = rng.below(20);
        let want: Vec<i32> = (0..n).map(|i| v[(i + n - k % n) % n]).collect();
        let mut got = v.clone();
        rotate_right(&mut got, k);
        check!(format!("v = {v:?}, k = {k}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut v: Vec<i32> = (0..200_000).collect();
    rotate_right(&mut v, 100_000);
    check!("v = 0..200000, k = 100000", (v[0], v[99_999], v[100_000], v[199_999]), (100_000, 199_999, 0, 99_999));
}
