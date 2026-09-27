/// Every line of `text`, trimmed, skipping blank ones.
pub fn trimmed_lines(text: &str) -> Vec<&str> {
    fn trim(s: &str) -> &str {
        s.trim()
    }
    text.lines().map(trim).filter(|l| !l.is_empty()).collect()
}
