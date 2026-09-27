use solution::*;

/// No derives: not Default, Clone or Copy.
struct Token(u32);

#[test]
fn ring_of_strings() {
    let mut r: Ring<String, 2> = Ring::new();
    let pushed: Vec<Option<String>> = ["a", "b", "c"].iter().map(|s| r.push(s.to_string())).collect();
    check!(r#"Ring<String, 2>: push a, b, c"#, (pushed, r.iter().cloned().collect::<Vec<_>>()), (vec![None, None, Some("a".to_string())], vec!["b".to_string(), "c".to_string()]));
}

#[test]
fn no_default_needed() {
    let mut r: Ring<Token, 2> = Ring::new();
    r.push(Token(1));
    r.push(Token(2));
    let evicted = r.push(Token(3)).map(|t| t.0);
    check!(r#"Ring<Token, 2>: push 1, 2, 3"#, (evicted, r.iter().map(|t| t.0).collect::<Vec<_>>()), (Some(1), vec![2, 3]));
}

#[test]
fn zero_capacity() {
    let mut r: Ring<i32, 0> = Ring::new();
    check!(r#"Ring<i32, 0>: push 5"#, (r.push(5), r.len(), Ring::<i32, 0>::CAPACITY), (Some(5), 0, 0));
}

#[test]
fn concat_ints() {
    let c: [i32; 5] = concat([1, 2], [3, 4, 5]);
    check!(r#"concat([1, 2], [3, 4, 5]) as [i32; 5]"#, c, [1, 2, 3, 4, 5]);
}

#[test]
fn concat_strings() {
    let c: [String; 3] = concat(["a".to_string()], ["b".to_string(), "c".to_string()]);
    check!(r#"concat(["a"], ["b", "c"]) as Strings"#, c, ["a".to_string(), "b".to_string(), "c".to_string()]);
}
