use solution::*;

fn collect_upper(text: &str) -> Vec<String> {
    let mut it = upper_lines(text);
    let mut out = Vec::new();
    while let Some(s) = it.next() {
        out.push(s.to_string());
    }
    out
}

#[test]
fn prefix_sums() {
    let mut v = vec![1, 2, 3, 4];
    let mut it = windows_mut(&mut v, 2);
    while let Some(w) = it.next() {
        w[1] += w[0];
    }
    check!(r#"windows of 2 over [1, 2, 3, 4], w[1] += w[0]"#, v, vec![1, 3, 6, 10]);
}

#[test]
fn window_count() {
    check!(r#"count(windows_mut(&mut [0; 5], 3))"#, count(windows_mut(&mut [0; 5], 3)), 3);
}

#[test]
fn too_big() {
    check!(r#"count(windows_mut(&mut [1, 2], 3))"#, count(windows_mut(&mut [1, 2], 3)), 0);
}

#[test]
fn upper() {
    check!(r#"upper_lines(" ab\ncd ")"#, collect_upper(" ab\ncd "), vec!["AB", "CD"]);
}

#[test]
fn upper_count() {
    check!(r#"count(upper_lines("a\nb\nc"))"#, count(upper_lines("a\nb\nc")), 3);
}
