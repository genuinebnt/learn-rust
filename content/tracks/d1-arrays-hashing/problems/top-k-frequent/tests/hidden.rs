use solution::*;

#[test]
fn all_distinct() {
    check!(r#"nums = [5, 3, 9], k = 3"#, top_k_frequent(&[5, 3, 9], 3), vec![3, 5, 9]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, -1, 2, -1, 2, 3], k = 1"#, top_k_frequent(&[-1, -1, 2, -1, 2, 3], 1), vec![-1]);
}

#[test]
fn all_same() {
    check!(r#"nums = [8, 8, 8], k = 1"#, top_k_frequent(&[8, 8, 8], 1), vec![8]);
}

#[test]
fn tie_picks_smaller() {
    check!(r#"nums = [9, 2, 9, 2], k = 1"#, top_k_frequent(&[9, 2, 9, 2], 1), vec![2]);
}

#[test]
fn negative_breaks_tie() {
    check!(r#"nums = [3, -3, 3, -3, 0], k = 2"#, top_k_frequent(&[3, -3, 3, -3, 0], 2), vec![-3, 3]);
}

#[test]
fn count_beats_value() {
    check!(r#"nums = [1, 5, 5, 1, 5], k = 2"#, top_k_frequent(&[1, 5, 5, 1, 5], 2), vec![5, 1]);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MAX, i32::MIN, i32::MAX], k = 2"#, top_k_frequent(&[i32::MAX, i32::MIN, i32::MAX], 2), vec![i32::MAX, i32::MIN]);
}

#[test]
fn all_distinct_k() {
    check!(r#"nums = [4, 1, 3, 2], k = 4"#, top_k_frequent(&[4, 1, 3, 2], 4), vec![1, 2, 3, 4]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(12);
    for _ in 0..300 {
        let n = 1 + rng.below(14);
        let nums: Vec<i32> = rng.vec(n, -4, 4);
        let mut distinct = nums.clone();
        distinct.sort();
        distinct.dedup();
        let k = 1 + rng.below(distinct.len());
        let count = |x: i32| nums.iter().filter(|&&y| y == x).count();
        // Stable sort by count keeps ascending values within a tie.
        distinct.sort_by(|a, b| count(*b).cmp(&count(*a)));
        distinct.truncate(k);
        check!(format!("nums = {nums:?}, k = {k}"), top_k_frequent(&nums, k), distinct);
    }
}

#[test]
fn scale_200k() {
    // 100000 distinct values; 0..10 appear three times, everything else twice.
    let mut nums: Vec<i32> = (0..100_000).flat_map(|x| [x, x]).collect();
    nums.extend(0..10);
    check!("nums = each of 0..100000 twice, then 0..10 again; k = 12", top_k_frequent(&nums, 12), vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]);
}
