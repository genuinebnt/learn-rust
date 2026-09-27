pub fn my_atoi(s: &str) -> i32 {
    let s = s.trim_start();
    let end = s.char_indices().position(|(i, c)| !(c.is_ascii_digit() || (i == 0 && (c == '+' || c == '-')))).unwrap_or(s.len());
    s[..end].parse::<i64>().map(|v| v.clamp(i64::from(i32::MIN), i64::from(i32::MAX)) as i32).unwrap_or(0)
}
