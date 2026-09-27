use solution::*;

#[test]
fn single_array() {
    check!(r#"arrays = [[1, 2, 3]]"#, merge_k_sorted(&[vec![1, 2, 3]]), vec![1, 2, 3]);
}

#[test]
fn extremes() {
    check!(r#"arrays = [[i32::MIN, i32::MAX], [0], [i32::MIN]]"#, merge_k_sorted(&[vec![i32::MIN, i32::MAX], vec![0], vec![i32::MIN]]), vec![i32::MIN, i32::MIN, 0, i32::MAX]);
}

#[test]
fn disjoint_ranges() {
    check!(r#"arrays = [[7, 8, 9], [1, 2, 3], [4, 5, 6]]"#, merge_k_sorted(&[vec![7, 8, 9], vec![1, 2, 3], vec![4, 5, 6]]), vec![1, 2, 3, 4, 5, 6, 7, 8, 9]);
}

#[test]
fn interleaved() {
    check!(r#"arrays = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]"#, merge_k_sorted(&[vec![1, 4, 7], vec![2, 5, 8], vec![3, 6, 9]]), vec![1, 2, 3, 4, 5, 6, 7, 8, 9]);
}

#[test]
fn very_different_lengths() {
    check!(r#"arrays = [[5], 0..10, [-1]]"#, merge_k_sorted(&[vec![5], (0..10).collect(), vec![-1]]), vec![-1, 0, 1, 2, 3, 4, 5, 5, 6, 7, 8, 9]);
}

#[test]
fn all_equal() {
    check!(r#"arrays = [[0, 0], [0], [0, 0, 0]]"#, merge_k_sorted(&[vec![0, 0], vec![0], vec![0, 0, 0]]), vec![0; 6]);
}

#[test]
fn many_empty() {
    check!(r#"arrays = 1000 empty arrays"#, merge_k_sorted(&vec![Vec::new(); 1000]), Vec::<i32>::new());
}

#[test]
fn last_array_holds_the_minimum() {
    check!(r#"arrays = [[2], [3], [1]]"#, merge_k_sorted(&[vec![2], vec![3], vec![1]]), vec![1, 2, 3]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(711);
    for _ in 0..300 {
        let k = rng.below(6);
        let mut arrays: Vec<Vec<i32>> = Vec::new();
        for _ in 0..k {
            let len = rng.below(6);
            let mut v: Vec<i32> = rng.vec(len, -10, 10);
            v.sort_unstable();
            arrays.push(v);
        }
        let mut want: Vec<i32> = arrays.concat();
        want.sort_unstable();
        check!(format!("arrays = {arrays:?}"), merge_k_sorted(&arrays), want);
    }
}

#[test]
fn scale_20k_arrays() {
    let mut rng = anneal_prelude::Rng::new(712);
    let arrays: Vec<Vec<i32>> = (0..20_000)
        .map(|_| {
            let mut v: Vec<i32> = rng.vec(10, -1_000_000, 1_000_000);
            v.sort_unstable();
            v
        })
        .collect();
    let mut want = arrays.concat();
    want.sort_unstable();
    check!("20000 sorted arrays of 10 random values", merge_k_sorted(&arrays) == want, true);
}
