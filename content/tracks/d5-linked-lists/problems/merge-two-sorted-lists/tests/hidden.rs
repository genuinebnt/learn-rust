use solution::*;

#[test]
fn both_empty() {
    check!(r#"[] + []"#, merge(None, None), None);
}

#[test]
fn disjoint() {
    check!(r#"[5,6] + [1,2]"#, values(&merge(list(&[5, 6]), list(&[1, 2]))), vec![1, 2, 5, 6]);
}

#[test]
fn long() {
    let odd: Vec<i32> = (0..10_000).filter(|x| x % 2 == 1).collect();
    let even: Vec<i32> = (0..10_000).filter(|x| x % 2 == 0).collect();
    check!(r#"odds + evens below 10⁴"#, values(&merge(list(&odd), list(&even))) == (0..10_000).collect::<Vec<_>>(), true);
}
