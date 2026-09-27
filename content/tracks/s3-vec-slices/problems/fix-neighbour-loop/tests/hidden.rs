use solution::*;

#[test]
fn empty() {
    check!(r#"v = []"#, pair_sums(&[]), Vec::<i32>::new());
}

#[test]
fn negatives() {
    check!(r#"v = [-1, 1, -1]"#, pair_sums(&[-1, 1, -1]), vec![0, 0]);
}

#[test]
fn zeros() {
    check!(r#"v = [0, 0, 0]"#, pair_sums(&[0, 0, 0]), vec![0, 0]);
}

#[test]
fn big_values() {
    check!(r#"v = [1000000000, 1000000000, -1000000000]"#, pair_sums(&[1_000_000_000, 1_000_000_000, -1_000_000_000]), vec![2_000_000_000, 0]);
}

#[test]
fn extremes() {
    check!(r#"v = [i32::MAX, 0, i32::MIN]"#, pair_sums(&[i32::MAX, 0, i32::MIN]), vec![i32::MAX, i32::MIN]);
}

#[test]
fn overlapping_pairs() {
    check!(r#"v = [1, 10, 100, 1000]"#, pair_sums(&[1, 10, 100, 1000]), vec![11, 110, 1100]);
}

#[test]
fn length() {
    check!(r#"v = [1; 1000]"#, pair_sums(&[1; 1000]).len(), 999);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2305);
    for _ in 0..300 {
        let n = rng.below(10);
        let v: Vec<i32> = rng.vec(n, -1000, 1000);
        let mut want = Vec::new();
        for i in 1..n {
            want.push(v[i - 1] + v[i]);
        }
        check!(format!("v = {v:?}"), pair_sums(&v), want);
    }
}

#[test]
fn scale_200k() {
    let v: Vec<i32> = (0..200_000).collect();
    let out = pair_sums(&v);
    check!("v = 0..200000", (out.len(), out[0], out[199_998]), (199_999, 1, 399_997));
}
