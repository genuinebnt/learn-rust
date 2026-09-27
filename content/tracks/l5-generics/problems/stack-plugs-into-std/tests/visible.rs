use solution::*;

/// No derives at all: not Default, Clone, Debug or Display.
struct Token(u32);

#[test]
fn collect_then_pop() {
    let mut s: Stack<i32> = (1..=3).collect();
    check!(r#"(1..=3).collect(), then pop"#, (s.pop(), s.len()), (Some(3), 2));
}

#[test]
fn into_iter_top_first() {
    let s: Stack<i32> = vec![1, 2, 3].into_iter().collect();
    check!(r#"collect [1, 2, 3], then into_iter"#, s.into_iter().collect::<Vec<_>>(), vec![3, 2, 1]);
}

#[test]
fn borrowing_loop() {
    let s: Stack<i32> = vec![1, 2, 3].into_iter().collect();
    let mut seen = Vec::new();
    for x in &s {
        seen.push(*x);
    }
    check!(r#"for x in &s over [1, 2, 3], then len"#, (seen, s.len()), (vec![3, 2, 1], 3));
}

#[test]
fn display() {
    let s: Stack<i32> = vec![1, 2, 3].into_iter().collect();
    check!(r#"[1, 2, 3] and an empty stack"#, (s.to_string(), Stack::<i32>::new().to_string()), ("[3, 2, 1]".to_string(), "[]".to_string()));
}

#[test]
fn default_for_any_t() {
    let mut s = Stack::<Token>::default();
    s.push(Token(7));
    check!(r#"Stack::<Token>::default(), push Token(7)"#, (s.len(), s.pop().map(|t| t.0)), (1, Some(7)));
}
