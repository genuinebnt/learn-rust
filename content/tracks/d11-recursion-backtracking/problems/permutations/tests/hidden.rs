use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn empty() {
    check!(r#"nums = []"#, permute(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, -2]"#, sorted(permute(&[-1, -2])), vec![vec![-2, -1], vec![-1, -2]]);
}

#[test]
fn unsorted_input() {
    check!(r#"nums = [3, 1, 2]"#, sorted(permute(&[3, 1, 2])), vec![vec![1, 2, 3], vec![1, 3, 2], vec![2, 1, 3], vec![2, 3, 1], vec![3, 1, 2], vec![3, 2, 1]]);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MAX, i32::MIN]"#, sorted(permute(&[i32::MAX, i32::MIN])), vec![vec![i32::MIN, i32::MAX], vec![i32::MAX, i32::MIN]]);
}

#[test]
fn four_distinct() {
    check!(r#"nums = [4, 3, 2, 1]"#, { let mut p = sorted(permute(&[4, 3, 2, 1])); p.dedup(); p.len() }, 24);
}

#[test]
fn each_is_a_rearrangement() {
    check!(r#"nums = [5, 6, 7, 8]"#, permute(&[5, 6, 7, 8]).into_iter().all(|mut p| { p.sort(); p == vec![5, 6, 7, 8] }), true);
}

#[test]
fn six_values() {
    check!(r#"nums = [1, 2, 3, 4, 5, 6]"#, permute(&[1, 2, 3, 4, 5, 6]).len(), 720);
}

#[test]
fn zero_and_negatives() {
    check!(r#"nums = [0, -1, 1]"#, sorted(permute(&[0, -1, 1])), vec![vec![-1, 0, 1], vec![-1, 1, 0], vec![0, -1, 1], vec![0, 1, -1], vec![1, -1, 0], vec![1, 0, -1]]);
}

/// Every ordering of `v` in lexicographic order, by repeated next-permutation steps.
fn lexicographic(mut v: Vec<i32>) -> Vec<Vec<i32>> {
    v.sort();
    let mut out = vec![v.clone()];
    loop {
        let Some(i) = (1..v.len()).rev().find(|&i| v[i - 1] < v[i]) else { return out };
        let j = (i..v.len()).rev().find(|&j| v[j] > v[i - 1]).unwrap();
        v.swap(i - 1, j);
        v[i..].reverse();
        out.push(v.clone());
    }
}

#[test]
fn random_vs_next_permutation() {
    let mut rng = anneal_prelude::Rng::new(1122);
    for _ in 0..200 {
        let n = rng.below(7);
        let mut nums: Vec<i32> = (-5..5).collect();
        rng.shuffle(&mut nums);
        nums.truncate(n);
        check!(format!("nums = {nums:?}"), sorted(permute(&nums)), lexicographic(nums.clone()));
    }
}

#[test]
fn scale_eight_values() {
    let nums = vec![8, 1, 7, 2, 6, 3, 5, 4];
    check!("nums = [8, 1, 7, 2, 6, 3, 5, 4]", sorted(permute(&nums)) == lexicographic(nums.clone()), true);
}
