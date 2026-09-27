use solution::*;

#[test]
fn push_after_emptying() {
    let mut s = Stack::new();
    s.push(1);
    let a = s.pop();
    let b = s.pop();
    s.push(2);
    check!(r#"push 1, pop, pop, push 2, peek"#, (a, b, s.peek().copied()), (Some(1), None, Some(2)));
}

#[test]
fn len_counts() {
    let mut s = Stack::new();
    for i in 0..5 {
        s.push(i);
    }
    s.pop();
    s.pop();
    check!(r#"push 5 items, pop 2"#, (s.len(), s.is_empty()), (3, false));
}

#[test]
fn empty_again() {
    let mut s = Stack::new();
    s.push(1);
    s.pop();
    check!(r#"push 1, pop"#, (s.len(), s.is_empty(), s.peek().is_none()), (0, true, true));
}

#[test]
fn peek_mut_on_empty() {
    let mut s: Stack<String> = Stack::new();
    check!(r#"peek_mut on a new stack"#, s.peek_mut().is_none(), true);
}

#[test]
fn pop_hands_over_ownership() {
    let mut s = Stack::new();
    s.push(String::from("hi"));
    let mut got = s.pop().unwrap();
    got.push('!');
    check!(r#"push "hi"; pop and append "!""#, got, "hi!".to_string());
}

#[test]
fn boxed_closures() {
    let mut s: Stack<Box<dyn Fn(i32) -> i32>> = Stack::new();
    s.push(Box::new(|x| x + 1));
    s.push(Box::new(|x| x * 2));
    let f = s.pop().unwrap();
    let g = s.pop().unwrap();
    check!(r#"a Stack<Box<dyn Fn(i32) -> i32>>: push +1, then *2; pop and call with 5"#, (f(5), g(5)), (10, 6));
}

#[test]
fn zero_sized_items() {
    let mut s = Stack::new();
    for _ in 0..3 {
        s.push(());
    }
    check!(r#"push () three times"#, (s.len(), s.pop(), s.len()), (3, Some(()), 2));
}

#[test]
fn drops_its_items() {
    let rc = std::rc::Rc::new(5);
    let mut s = Stack::new();
    s.push(rc.clone());
    s.push(rc.clone());
    drop(s);
    check!(r#"push two Rc clones, drop the stack"#, std::rc::Rc::strong_count(&rc), 1);
}

#[test]
fn peek_mut_then_peek() {
    let mut s = Stack::new();
    s.push(String::from("a"));
    s.peek_mut().unwrap().push_str("b");
    check!(r#"push "a"; push_str "b" through peek_mut; peek"#, s.peek().map(String::as_str), Some("ab"));
}

#[test]
fn random_vs_vec_model() {
    let mut rng = anneal_prelude::Rng::new(4501);
    for _ in 0..300 {
        let mut s = Stack::new();
        let mut model: Vec<i64> = Vec::new();
        let ops = rng.below(20);
        let mut log = Vec::new();
        for _ in 0..ops {
            match rng.below(4) {
                0 | 1 => {
                    let x = rng.int(-9, 9);
                    log.push(format!("push {x}"));
                    s.push(x);
                    model.push(x);
                }
                2 => {
                    log.push("pop".to_string());
                    check!(format!("{log:?}"), s.pop(), model.pop());
                }
                _ => {
                    log.push("peek_mut += 1".to_string());
                    if let Some(t) = s.peek_mut() {
                        *t += 1;
                    }
                    if let Some(t) = model.last_mut() {
                        *t += 1;
                    }
                }
            }
            check!(format!("{log:?}"), (s.len(), s.is_empty(), s.peek().copied()), (model.len(), model.is_empty(), model.last().copied()));
        }
    }
}

#[test]
fn scale_push_pop() {
    let n = 400_000u64;
    let mut s = Stack::new();
    for i in 0..n {
        s.push(i);
    }
    let mut sum = 0u64;
    let mut last = n;
    while let Some(x) = s.pop() {
        assert!(x < last, "popped {x} after {last}");
        last = x;
        sum += x;
    }
    check!("push 0..400000, pop all", sum, n * (n - 1) / 2);
}
