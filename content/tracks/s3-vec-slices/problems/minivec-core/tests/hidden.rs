use solution::*;

use std::rc::Rc;

#[test]
fn drop_releases_every_element() {
    let counter = Rc::new(());
    {
        let mut v = MiniVec::new();
        for _ in 0..10 {
            v.push(Rc::clone(&counter));
        }
        v.pop();
    }
    check!("10 Rc clones pushed, one popped, then the MiniVec dropped", Rc::strong_count(&counter), 1);
}

#[test]
fn many_strings_survive_reallocation() {
    let mut v = MiniVec::new();
    for i in 0..1000 {
        v.push(i.to_string());
    }
    check!("push 0..1000 as Strings", (v.len(), v.get(999).cloned()), (1000, Some("999".to_string())));
}

#[test]
fn pop_empty() {
    check!(r#"new MiniVec"#, MiniVec::<u8>::new().pop(), None);
}
