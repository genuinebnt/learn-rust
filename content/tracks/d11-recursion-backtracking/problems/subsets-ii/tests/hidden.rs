use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn distinct_values() {
    check!(r#"nums = [1, 2, 3]"#, subsets_with_dup(&[1, 2, 3]).len(), 8);
}

#[test]
fn empty() {
    check!(r#"nums = []"#, subsets_with_dup(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-1, 2, -1]"#, norm(subsets_with_dup(&[-1, 2, -1])), vec![vec![], vec![-1], vec![-1, -1], vec![-1, -1, 2], vec![-1, 2], vec![2]]);
}

#[test]
fn two_equal() {
    check!(r#"nums = [5, 5]"#, norm(subsets_with_dup(&[5, 5])), vec![vec![], vec![5], vec![5, 5]]);
}

#[test]
fn two_pairs() {
    check!(r#"nums = [3, 1, 3, 1]"#, subsets_with_dup(&[3, 1, 3, 1]).len(), 9);
}

#[test]
fn pair_kept_after_skipping() {
    check!(r#"nums = [2, 1, 2]: [2, 2] is there"#, norm(subsets_with_dup(&[2, 1, 2])).contains(&vec![2, 2]), true);
}

#[test]
fn extremes() {
    check!(r#"nums = [10, -10, 10]"#, norm(subsets_with_dup(&[10, -10, 10])), vec![vec![], vec![-10], vec![-10, 10], vec![-10, 10, 10], vec![10], vec![10, 10]]);
}

#[test]
fn ten_distinct() {
    check!(r#"nums = 0..10"#, subsets_with_dup(&(0..10).collect::<Vec<i32>>()).len(), 1024);
}

#[test]
fn random_vs_bitmasks_and_a_set() {
    let mut rng = anneal_prelude::Rng::new(1121);
    for _ in 0..300 {
        let n = rng.below(10);
        let nums: Vec<i32> = rng.vec(n, -2, 2);
        let mut all = std::collections::BTreeSet::new();
        for mask in 0..1u32 << n {
            let mut s: Vec<i32> = (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).collect();
            s.sort();
            all.insert(s);
        }
        check!(format!("nums = {nums:?}"), norm(subsets_with_dup(&nums)), all.into_iter().collect::<Vec<_>>());
    }
}

#[test]
fn scale_twenty_six_equal() {
    check!("nums = [5; 26]", norm(subsets_with_dup(&vec![5; 26])), (0..=26).map(|k| vec![5; k]).collect::<Vec<_>>());
}

#[test]
fn scale_two_runs_of_thirteen() {
    let mut nums = vec![7; 13];
    nums.extend(vec![3; 13]);
    let got = norm(subsets_with_dup(&nums));
    check!("nums = [7; 13] + [3; 13]", (got.len(), got[195].clone()), (196, vec![7; 13]));
}
