/// Every line of `text`, trimmed, skipping blank ones.
pub fn trimmed_lines(text: &str) -> Vec<&str> {
    text.split_whitespace().collect()
}
