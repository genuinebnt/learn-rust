use solution::*;

fn norm<T: Ord>(mut groups: Vec<Vec<T>>) -> Vec<Vec<T>> {
    for g in &mut groups {
        g.sort();
    }
    groups.sort();
    groups
}

#[test]
fn empty() {
    check!(r#"nums = []"#, subsets(&[]), vec![Vec::<i32>::new()]);
}

#[test]
fn single_negative() {
    check!(r#"nums = [-7]"#, norm(subsets(&[-7])), vec![vec![], vec![-7]]);
}

#[test]
fn two() {
    check!(r#"nums = [5, 3]"#, norm(subsets(&[5, 3])), vec![vec![], vec![3], vec![3, 5], vec![5]]);
}

#[test]
fn not_contiguous_only() {
    check!(r#"nums = [1, 2, 3]: [1, 3] is a subset"#, subsets(&[1, 2, 3]).into_iter().any(|mut s| { s.sort(); s == vec![1, 3] }), true);
}

#[test]
fn ten_values() {
    check!(r#"nums = 0..10"#, subsets(&(0..10).collect::<Vec<i32>>()).len(), 1024);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN, i32::MAX]"#, norm(subsets(&[i32::MIN, i32::MAX])), vec![vec![], vec![i32::MIN], vec![i32::MIN, i32::MAX], vec![i32::MAX]]);
}

#[test]
fn no_duplicate_subsets() {
    check!(r#"nums = [4, 1, 3, 2]"#, { let mut s = norm(subsets(&[4, 1, 3, 2])); s.dedup(); s.len() }, 16);
}

#[test]
fn unsorted_input() {
    check!(r#"nums = [3, 1, 2]"#, norm(subsets(&[3, 1, 2])), norm(vec![vec![], vec![1], vec![2], vec![1, 2], vec![3], vec![1, 3], vec![2, 3], vec![1, 2, 3]]));
}

#[test]
fn random_vs_bitmasks() {
    let mut rng = anneal_prelude::Rng::new(1111);
    for _ in 0..200 {
        let n = rng.below(9);
        let mut nums: Vec<i32> = (-10..10).collect();
        rng.shuffle(&mut nums);
        nums.truncate(n);
        let want: Vec<Vec<i32>> = (0..1u32 << n).map(|mask| (0..n).filter(|&i| mask >> i & 1 == 1).map(|i| nums[i]).collect()).collect();
        check!(format!("nums = {nums:?}"), norm(subsets(&nums)), norm(want));
    }
}

#[test]
fn scale_18_values() {
    let nums: Vec<i32> = (0..18).collect();
    let mut all = norm(subsets(&nums));
    let total: usize = all.iter().map(Vec::len).sum();
    all.dedup();
    check!("nums = 0..18", (all.len(), total), (1 << 18, 18 << 17));
}
