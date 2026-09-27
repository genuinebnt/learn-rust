/// Every line of `text`, trimmed, skipping blank ones.
pub fn trimmed_lines(text: &str) -> Vec<&str> {
    text.lines().map(str::trim_start).filter(|l| !l.is_empty()).collect()
}
