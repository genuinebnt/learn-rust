fn best(nums: &[i32], prev: Option<i32>) -> usize {
    match nums {
        [] => 0,
        [x, rest @ ..] => {
            let skip = best(rest, prev);
            if prev.map_or(true, |p| p < *x) { skip.max(1 + best(rest, Some(*x))) } else { skip }
        }
    }
}

pub fn length_of_lis(nums: &[i32]) -> usize {
    best(nums, None)
}
