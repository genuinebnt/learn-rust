use solution::*;

#[test]
fn emoji() {
    check!(r#""🦀!""#, sizes("🦀!"), (5, 2));
}

#[test]
fn nth() {
    check!(r#""héllo", 1 and 9"#, (nth_char("héllo", 1), nth_char("héllo", 9)), (Some('é'), None));
}

#[test]
fn offsets_slice_cleanly() {
    let s = "x→y→z";
    let ok = positions(s, '→').iter().all(|&i| s.is_char_boundary(i) && s[i..].starts_with('→'));
    check!(r#"every offset from positions("x→y→z", '→') is a char boundary"#, ok, true);
}
