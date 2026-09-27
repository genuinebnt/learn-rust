pub fn restore_ip_addresses(s: &str) -> Vec<String> {
    fn go<'a>(rest: &'a str, parts: &mut Vec<&'a str>, out: &mut Vec<String>) {
        let left = 4 - parts.len();
        if left == 0 {
            if rest.is_empty() {
                out.push(parts.join("."));
            }
            return;
        }
        // Each remaining part takes 1 to 3 digits.
        if rest.len() < left || rest.len() > 3 * left {
            return;
        }
        for len in 1..=rest.len().min(3) {
            let part = &rest[..len];
            // A longer part would keep the leading zero or be larger still.
            if (len > 1 && part.starts_with('0')) || part.parse::<u16>().is_ok_and(|v| v > 255) {
                break;
            }
            parts.push(part);
            go(&rest[len..], parts, out);
            parts.pop();
        }
    }
    let mut out = Vec::new();
    go(s, &mut Vec::with_capacity(4), &mut out);
    out
}
