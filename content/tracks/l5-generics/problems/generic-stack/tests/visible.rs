use solution::*;

#[test]
fn last_in_first_out() {
    let mut s = Stack::new();
    s.push(1);
    s.push(2);
    s.push(3);
    check!(r#"push 1, 2, 3; pop four times"#, (s.pop(), s.pop(), s.pop(), s.pop()), (Some(3), Some(2), Some(1), None));
}

#[test]
fn empty() {
    let mut s: Stack<i32> = Stack::new();
    check!(r#"a new Stack<i32>"#, (s.len(), s.is_empty(), s.peek().copied(), s.pop()), (0, true, None::<i32>, None::<i32>));
}

#[test]
fn peek_keeps_the_item() {
    let mut s = Stack::new();
    s.push("a".to_string());
    s.push("b".to_string());
    check!(r#"push "a", "b"; peek twice, then len"#, (s.peek().map(String::as_str), s.peek().map(String::as_str), s.len()), (Some("b"), Some("b"), 2));
}

#[test]
fn peek_mut_edits_the_top() {
    let mut s = Stack::new();
    s.push(1);
    s.push(2);
    *s.peek_mut().unwrap() += 10;
    check!(r#"push 1, 2; add 10 through peek_mut; pop twice"#, (s.pop(), s.pop()), (Some(12), Some(1)));
}

#[test]
fn no_bounds_on_t() {
    struct Token(u32);
    let mut s = Stack::new();
    s.push(Token(1));
    s.push(Token(2));
    check!(r#"a type with no derives: push Token(1), Token(2); pop"#, (s.pop().map(|t| t.0), s.len()), (Some(2), 1));
}
