use solution::*;

#[test]
fn nums1_empty() {
    check!(r#"nums1 = [0], m = 0, nums2 = [1]"#, { let mut a = [0]; merge(&mut a, 0, &[1]); a }, [1]);
}

#[test]
fn all_smaller() {
    check!(r#"nums1 = [4, 5, 0, 0], m = 2, nums2 = [1, 2]"#, { let mut a = [4, 5, 0, 0]; merge(&mut a, 2, &[1, 2]); a }, [1, 2, 4, 5]);
}

#[test]
fn both_empty() {
    check!(r#"nums1 = [], m = 0, nums2 = []"#, { let mut a: [i32; 0] = []; merge(&mut a, 0, &[]); a }, [0i32; 0]);
}

#[test]
fn all_larger() {
    check!(r#"nums1 = [1, 2, 0, 0], m = 2, nums2 = [3, 4]"#, { let mut a = [1, 2, 0, 0]; merge(&mut a, 2, &[3, 4]); a }, [1, 2, 3, 4]);
}

#[test]
fn interleaved() {
    check!(r#"nums1 = [1, 3, 5, 0, 0, 0], m = 3, nums2 = [2, 4, 6]"#, { let mut a = [1, 3, 5, 0, 0, 0]; merge(&mut a, 3, &[2, 4, 6]); a }, [1, 2, 3, 4, 5, 6]);
}

#[test]
fn duplicates() {
    check!(r#"nums1 = [2, 2, 0, 0], m = 2, nums2 = [2, 2]"#, { let mut a = [2, 2, 0, 0]; merge(&mut a, 2, &[2, 2]); a }, [2, 2, 2, 2]);
}

#[test]
fn negatives_and_zeros() {
    check!(r#"nums1 = [-3, 0, 0, 0], m = 2, nums2 = [-5, 0]"#, { let mut a = [-3, 0, 0, 0]; merge(&mut a, 2, &[-5, 0]); a }, [-5, -3, 0, 0]);
}

#[test]
fn extremes() {
    check!(r#"nums1 = [i32::MIN, i32::MAX, 0, 0], m = 2, nums2 = [i32::MIN, i32::MAX]"#, { let mut a = [i32::MIN, i32::MAX, 0, 0]; merge(&mut a, 2, &[i32::MIN, i32::MAX]); a }, [i32::MIN, i32::MIN, i32::MAX, i32::MAX]);
}

#[test]
fn nums1_empty_several() {
    check!(r#"nums1 = [0, 0, 0], m = 0, nums2 = [-1, 0, 7]"#, { let mut a = [0, 0, 0]; merge(&mut a, 0, &[-1, 0, 7]); a }, [-1, 0, 7]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(203);
    for _ in 0..300 {
        let m = rng.below(8);
        let n = rng.below(8);
        let mut a: Vec<i32> = rng.vec(m, -9, 9);
        let mut b: Vec<i32> = rng.vec(n, -9, 9);
        a.sort();
        b.sort();
        let mut want = [a.clone(), b.clone()].concat();
        want.sort();
        let mut got = a.clone();
        got.resize(m + n, 0);
        merge(&mut got, m, &b);
        check!(format!("nums1 = {a:?} + {n} zeros, m = {m}, nums2 = {b:?}"), got, want);
    }
}

#[test]
fn scale_100k_each() {
    let n = 100_000;
    let mut a: Vec<i32> = (0..n as i32).map(|i| 1_000_000 + i).collect();
    a.resize(2 * n, 0);
    let b: Vec<i32> = (0..n as i32).collect();
    merge(&mut a, n, &b);
    let want: Vec<i32> = (0..n as i32).chain((0..n as i32).map(|i| 1_000_000 + i)).collect();
    check!("nums1 = 1000000..1100000 + 100000 zeros, m = 100000, nums2 = 0..100000", a == want, true);
}
