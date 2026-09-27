use solution::*;

#[test]
fn empty() {
    check!(r#"nothing stored"#, Stash::new().all::<i64>().len(), 0);
}

#[test]
fn types_are_exact() {
    let mut s = Stash::new();
    s.put(1u64);
    check!(r#"put 1u64; all::<u32>()"#, s.all::<u32>().len(), 0);
}
