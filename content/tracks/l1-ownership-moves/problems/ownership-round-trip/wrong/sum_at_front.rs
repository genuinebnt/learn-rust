pub fn push_sum(mut v: Vec<i64>) -> Vec<i64> {
    let sum = v.iter().sum();
    v.insert(0, sum);
    v
}

pub fn swap_owned(a: String, b: String) -> (String, String) {
    (b, a)
}
