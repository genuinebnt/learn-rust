pub fn push_sum(mut v: Vec<i64>) -> Vec<i64> {
    let sum: i32 = v.iter().map(|&x| x as i32).sum();
    v.push(sum as i64);
    v
}

pub fn swap_owned(a: String, b: String) -> (String, String) {
    (b, a)
}
