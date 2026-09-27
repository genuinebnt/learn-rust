pub fn restore_ip_addresses(s: &str) -> Vec<String> {
    fn go(rest: &str, parts: &mut Vec<String>, out: &mut Vec<String>) {
        if parts.len() == 4 {
            if rest.is_empty() {
                out.push(parts.join("."));
            }
            return;
        }
        for len in 1..=rest.len().min(3) {
            let part = &rest[..len];
            if len > 1 && part.starts_with('0') {
                break;
            }
            parts.push(part.to_string());
            go(&rest[len..], parts, out);
            parts.pop();
        }
    }
    let mut out = Vec::new();
    go(s, &mut Vec::new(), &mut out);
    out
}
