pub fn is_valid(s: &str) -> bool {
    let mut s = s.to_string();
    loop {
        let t = s.replace("()", "").replace("[]", "").replace("{}", "");
        if t.len() == s.len() {
            return t.is_empty();
        }
        s = t;
    }
}
