use solution::*;

/// No derives at all: not Default, Clone, Debug or Display.
struct Token(u32);

#[test]
fn extend_pushes_in_order() {
    let mut s = Stack::new();
    s.push(1);
    s.extend(vec![2, 3]);
    check!(r#"push 1, extend [2, 3], pop"#, (s.pop(), s.len()), (Some(3), 2));
}

#[test]
fn display_strings() {
    let s: Stack<String> = vec!["a".to_string(), "b".to_string()].into_iter().collect();
    check!(r#"collect ["a", "b"] as Strings"#, s.to_string(), "[b, a]");
}

#[test]
fn display_nested() {
    let mut s: Stack<Stack<i32>> = Stack::new();
    s.push(vec![1, 2].into_iter().collect());
    s.push(Stack::new());
    check!(r#"a Stack<Stack<i32>>: push [1, 2], then an empty stack"#, s.to_string(), "[[], [2, 1]]");
}

#[test]
fn empty_iterations() {
    let s: Stack<i32> = Stack::default();
    check!(r#"empty Stack<i32>: by-ref and by-value iteration"#, ((&s).into_iter().count(), s.into_iter().count()), (0, 0));
}

#[test]
fn collect_empty() {
    let s: Stack<u8> = std::iter::empty().collect();
    check!(r#"collect an empty iterator"#, (s.is_empty(), s.peek().is_none()), (true, true));
}

#[test]
fn no_clone_needed() {
    let s: Stack<Token> = (1..=3).map(Token).collect();
    let by_ref: Vec<u32> = (&s).into_iter().map(|t| t.0).collect();
    let by_val: Vec<u32> = s.into_iter().map(|t| t.0).collect();
    check!(r#"Tokens: collect, iterate by ref, then by value"#, (by_ref, by_val), (vec![3, 2, 1], vec![3, 2, 1]));
}

#[test]
fn first_of_into_iter_is_peek() {
    let s: Stack<char> = "xyz".chars().collect();
    check!(r#"collect "xyz" chars"#, (s.peek().copied(), s.into_iter().next()), (Some('z'), Some('z')));
}

#[test]
fn extend_with_strings_by_ref_loop() {
    let mut s: Stack<String> = Stack::new();
    s.extend("one three ab".split(' ').map(String::from));
    let mut total = 0;
    for w in &s {
        total += w.len();
    }
    check!(r#"extend with words, then sum lengths by ref"#, (total, s.len()), (10, 3));
}

#[test]
fn drops_unconsumed_items() {
    let rc = std::rc::Rc::new(0);
    let s: Stack<std::rc::Rc<i32>> = (0..3).map(|_| rc.clone()).collect();
    let mut it = s.into_iter();
    let first = it.next();
    drop(it);
    drop(first);
    check!(r#"Rc clones: take one from into_iter, drop the rest"#, std::rc::Rc::strong_count(&rc), 1);
}

#[test]
fn random_vs_vec_model() {
    let mut rng = anneal_prelude::Rng::new(4501);
    for _ in 0..300 {
        let n = rng.below(6);
        let start: Vec<i32> = rng.vec(n, -9, 9);
        let m = rng.below(4);
        let more: Vec<i32> = rng.vec(m, -9, 9);
        let mut s: Stack<i32> = start.clone().into_iter().collect();
        s.extend(more.clone());
        let mut model = start.clone();
        model.extend(more.clone());
        let top_first: Vec<i32> = model.iter().rev().copied().collect();
        let shown = format!("[{}]", top_first.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(", "));
        let by_ref: Vec<i32> = (&s).into_iter().copied().collect();
        let text = s.to_string();
        let by_val: Vec<i32> = s.into_iter().collect();
        check!(format!("collect {start:?}, extend {more:?}"), (by_ref, text, by_val), (top_first.clone(), shown, top_first));
    }
}
