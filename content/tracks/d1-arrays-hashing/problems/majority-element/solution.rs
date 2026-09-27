/// Boyer–Moore voting: the majority survives pairing off against everything else.
pub fn majority(nums: &[i32]) -> i32 {
    nums.iter()
        .fold((0, 0), |(candidate, count), &x| match count {
            0 => (x, 1),
            _ if x == candidate => (candidate, count + 1),
            _ => (candidate, count - 1),
        })
        .0
}
