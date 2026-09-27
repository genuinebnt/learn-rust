use solution::*;

#[test]
fn four_takes_the_upper_middle() {
    check!(r#"nums = [1,2,3,4]"#, level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4])), vec![Some(3), Some(2), Some(4), Some(1)]);
}

#[test]
fn seven() {
    check!(r#"nums = [1,2,3,4,5,6,7]"#, level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4, 5, 6, 7])), vec![Some(4), Some(2), Some(6), Some(1), Some(3), Some(5), Some(7)]);
}

#[test]
fn negatives() {
    check!(r#"nums = [-5,-4]"#, level_order_values(&sorted_array_to_bst(&[-5, -4])), vec![Some(-4), Some(-5)]);
}

#[test]
fn extremes() {
    check!(r#"nums = [i32::MIN,0,i32::MAX]"#, level_order_values(&sorted_array_to_bst(&[i32::MIN, 0, i32::MAX])), vec![Some(0), Some(i32::MIN), Some(i32::MAX)]);
}

#[test]
fn five() {
    check!(r#"nums = [1,2,3,4,5]"#, level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4, 5])), vec![Some(3), Some(2), Some(5), Some(1), None, Some(4)]);
}

#[test]
fn six() {
    check!(r#"nums = [1,2,3,4,5,6]"#, level_order_values(&sorted_array_to_bst(&[1, 2, 3, 4, 5, 6])), vec![Some(4), Some(2), Some(6), Some(1), Some(3), Some(5)]);
}

#[test]
fn two_negative_one_positive() {
    check!(r#"nums = [-3,-1,2]"#, level_order_values(&sorted_array_to_bst(&[-3, -1, 2])), vec![Some(-1), Some(-3), Some(2)]);
}

#[test]
fn eight() {
    check!(r#"nums = [0,1,2,3,4,5,6,7]"#, level_order_values(&sorted_array_to_bst(&[0, 1, 2, 3, 4, 5, 6, 7])), vec![Some(4), Some(2), Some(6), Some(1), Some(3), Some(5), Some(7), Some(0)]);
}

/// The expected level order, walking index ranges breadth first.
fn by_ranges(nums: &[i32]) -> Vec<Option<i32>> {
    let mut out = Vec::new();
    let mut queue = std::collections::VecDeque::from([(0, nums.len())]);
    while let Some((lo, hi)) = queue.pop_front() {
        if lo == hi {
            out.push(None);
            continue;
        }
        let mid = lo + (hi - lo) / 2;
        out.push(Some(nums[mid]));
        queue.push_back((lo, mid));
        queue.push_back((mid + 1, hi));
    }
    while out.last() == Some(&None) {
        out.pop();
    }
    out
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(607);
    for _ in 0..300 {
        let n = rng.below(20);
        let mut nums: Vec<i32> = rng.vec(n, -50, 50);
        nums.sort();
        nums.dedup();
        check!(format!("nums = {nums:?}"), level_order_values(&sorted_array_to_bst(&nums)), by_ranges(&nums));
    }
}

#[test]
fn scale_200000() {
    let nums: Vec<i32> = (0..200_000).map(|i| i * 3 - 300_000).collect();
    check!("nums = [-300000, -299997, …] (200000 values)", level_order_values(&sorted_array_to_bst(&nums)) == by_ranges(&nums), true);
}
