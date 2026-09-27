pub fn length_of_lis(nums: &[i32]) -> usize {
    let mut tails: Vec<i32> = Vec::new();
    for &x in nums {
        match tails.last() {
            Some(&t) if t >= x => *tails.last_mut().unwrap() = x,
            _ => tails.push(x),
        }
    }
    tails.len()
}
