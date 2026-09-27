use solution::*;

#[test]
fn empty_lists() {
    check!(r#"[[],[]]"#, merge_k(vec![None, None]), None);
}

#[test]
fn negatives() {
    check!(r#"[[-3,0],[-5]]"#, values(&merge_k(vec![list(&[-3, 0]), list(&[-5])])), vec![-5, -3, 0]);
}

#[test]
fn many() {
    let lists: Vec<_> = (0..100).map(|k| list(&(0..100).map(|i| i * 100 + k).collect::<Vec<i32>>())).collect();
    check!(r#"100 lists × 100 values"#, values(&merge_k(lists)) == (0..10_000).collect::<Vec<_>>(), true);
}
