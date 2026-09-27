use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

#[test]
fn single() {
    check!(r#"nums = [7]"#, permute_unique(&[7]), vec![vec![7]]);
}

#[test]
fn two_pairs() {
    check!(r#"nums = [1, 1, 2, 2]"#, sorted(permute_unique(&[1, 1, 2, 2])), vec![vec![1, 1, 2, 2], vec![1, 2, 1, 2], vec![1, 2, 2, 1], vec![2, 1, 1, 2], vec![2, 1, 2, 1], vec![2, 2, 1, 1]]);
}

#[test]
fn two_equal() {
    check!(r#"nums = [-4, -4]"#, permute_unique(&[-4, -4]), vec![vec![-4, -4]]);
}

#[test]
fn negatives() {
    check!(r#"nums = [0, -1, 0]"#, sorted(permute_unique(&[0, -1, 0])), vec![vec![-1, 0, 0], vec![0, -1, 0], vec![0, 0, -1]]);
}

#[test]
fn unsorted_pairs() {
    check!(r#"nums = [2, 1, 2, 1]"#, permute_unique(&[2, 1, 2, 1]).len(), 6);
}

#[test]
fn three_kinds() {
    check!(r#"nums = [1, 1, 2, 2, 3]"#, permute_unique(&[1, 1, 2, 2, 3]).len(), 30);
}

#[test]
fn six_distinct() {
    check!(r#"nums = [1, 2, 3, 4, 5, 6]"#, permute_unique(&[1, 2, 3, 4, 5, 6]).len(), 720);
}

#[test]
fn extremes() {
    check!(r#"nums = [10, -10, 10]"#, sorted(permute_unique(&[10, -10, 10])), vec![vec![-10, 10, 10], vec![10, -10, 10], vec![10, 10, -10]]);
}

/// Distinct orderings of `v` in lexicographic order; next-permutation skips repeats by itself.
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
    let mut rng = anneal_prelude::Rng::new(1123);
    for _ in 0..300 {
        let n = rng.below(8);
        let nums: Vec<i32> = rng.vec(n, -2, 2);
        check!(format!("nums = {nums:?}"), sorted(permute_unique(&nums)), lexicographic(nums.clone()));
    }
}

#[test]
fn scale_ten_equal_and_one_other() {
    let mut nums = vec![0; 10];
    nums.push(1);
    check!("nums = [0; 10] + [1]", permute_unique(&nums).len(), 11);
}

#[test]
fn scale_two_runs_of_five() {
    let mut nums = vec![1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 2];
    let got = sorted(permute_unique(&nums));
    nums.sort();
    check!("nums = [1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 2]", (got.len(), got[0].clone()), (2772, nums));
}
