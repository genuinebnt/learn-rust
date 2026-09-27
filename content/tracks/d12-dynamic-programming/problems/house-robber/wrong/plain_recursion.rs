fn best(nums: &[u32]) -> u64 {
    match nums {
        [] => 0,
        [x, rest @ ..] => best(rest).max(*x as u64 + best(rest.get(1..).unwrap_or(&[]))),
    }
}

pub fn rob(nums: &[u32]) -> u64 {
    best(nums)
}
