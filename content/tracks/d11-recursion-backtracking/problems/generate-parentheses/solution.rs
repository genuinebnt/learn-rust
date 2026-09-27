pub fn generate_parenthesis(n: usize) -> Vec<String> {
    fn go(n: usize, open: usize, close: usize, path: &mut String, out: &mut Vec<String>) {
        if path.len() == 2 * n {
            out.push(path.clone());
            return;
        }
        if open < n {
            path.push('(');
            go(n, open + 1, close, path, out);
            path.pop();
        }
        // A `)` needs an unmatched `(` before it.
        if close < open {
            path.push(')');
            go(n, open, close + 1, path, out);
            path.pop();
        }
    }
    let mut out = Vec::new();
    go(n, 0, 0, &mut String::with_capacity(2 * n), &mut out);
    out
}
