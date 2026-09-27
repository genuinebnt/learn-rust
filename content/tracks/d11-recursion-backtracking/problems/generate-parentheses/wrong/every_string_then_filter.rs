pub fn generate_parenthesis(n: usize) -> Vec<String> {
    let mut out = Vec::new();
    for mask in 0u64..1 << (2 * n) {
        let s: String = (0..2 * n).map(|i| if mask >> i & 1 == 1 { '(' } else { ')' }).collect();
        let mut depth = 0i32;
        let mut ok = true;
        for ch in s.chars() {
            depth += if ch == '(' { 1 } else { -1 };
            if depth < 0 {
                ok = false;
                break;
            }
        }
        if ok && depth == 0 {
            out.push(s);
        }
    }
    out
}
